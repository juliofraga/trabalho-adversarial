"""Verificações offline das regras. Os agentes aqui são dublês roteirizados, usados
apenas para testar o simulador; não fazem parte da demonstração."""

from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest import mock

from glpi_adversarial.models import (
    InvalidAgentResponse,
    RequesterAction,
    TechnicianAction,
    TicketDecision,
    classify,
    priority,
    requester_action_from,
    technician_action_from,
)
from glpi_adversarial.rate_limit import RequestPacer
from glpi_adversarial.signals import SIGNAL_NAMES
from glpi_adversarial.simulation import Simulation, SimulationError, summary

HONEST = None  # sentinela: declarar os níveis reais
INFLATE = RequesterAction(3, 3, "A impressora parou, é urgente e crítico, todos parados.", "teste")


class Scripted:
    def __init__(self, requests, review):
        self.requests = list(requests)
        self.review = review
        self.req_views: list[dict] = []
        self.tech_views: list[dict] = []

    def decide_request(self, obs):
        self.req_views.append(obs)
        r = self.requests[obs["round"] - 1]
        if r is HONEST:
            p = obs["your_problem_now"]
            return RequesterAction(p["real_urgency"], p["real_impact"], p["facts"], "honesto")
        return r

    def decide_review(self, obs):
        self.tech_views.append(obs)
        return self.review(obs)


def strategic_id(obs):
    return next(t["ticket_id"] for t in obs["queue"] if t["user_id"] == "carlos.telefonia")


def accept_all(rules=()):
    def f(obs):
        return TechnicianAction(
            tuple(TicketDecision(i, "aceitar", "ok") for i in obs["pending_ticket_ids"]), tuple(rules), (), "aceita"
        )
    return f


def review_strategic(rules=()):
    def f(obs):
        sid = strategic_id(obs)
        cap = obs["review_capacity_left"]
        ds = []
        for i in obs["pending_ticket_ids"]:
            act = "revisar" if (i == sid and cap > 0) else "aceitar"
            ds.append(TicketDecision(i, act, "r"))
        return TechnicianAction(tuple(ds), tuple(rules), ("vigiar carlos",), "revisa o solicitante")
    return f


class RulesTests(unittest.TestCase):
    def test_priority_matrix(self):
        self.assertEqual(priority(3, 2), "P1")
        self.assertEqual(priority(1, 3), "P2")
        self.assertEqual(priority(1, 1), "P3")

    def test_classify(self):
        self.assertEqual(classify(1, 1, 1, 1, True), "honesta")
        self.assertEqual(classify(1, 1, 3, 3, True), "inflada")
        self.assertEqual(classify(1, 1, 3, 3, False), "erro_nao_intencional")
        self.assertEqual(classify(3, 3, 1, 1, True), "subestimada")

    def test_validation(self):
        with self.assertRaises(InvalidAgentResponse):
            requester_action_from({"urgency": 4, "impact": 1, "description": "x", "rationale": "y"})
        with self.assertRaises(InvalidAgentResponse):  # excede a capacidade
            technician_action_from(
                {"decisions": [{"ticket_id": "A", "action": "revisar", "reason": "r"},
                               {"ticket_id": "B", "action": "revisar", "reason": "r"}],
                 "auto_review_rules": [], "notes": [], "rationale": "r"},
                ["A", "B"], 1, SIGNAL_NAMES)


class SimulationTests(unittest.TestCase):
    def test_minimum_rounds(self):
        with self.assertRaises(ValueError):
            Simulation(Scripted([], accept_all()), rounds=2)

    def test_payoff_matrix_from_t1(self):
        # (inflar, aceitar) = 3 ; (inflar, revisar) = 0 ; (honesto, *) = 2
        sim = Simulation(Scripted([INFLATE] * 3, accept_all()), rounds=3)
        sim.run()
        self.assertEqual(sim.state.requester_score, 9)
        sim = Simulation(Scripted([INFLATE] * 3, review_strategic()), rounds=3)
        trace = sim.run()
        self.assertEqual(sim.state.requester_score, 0)
        self.assertEqual(trace[0]["strategic_ticket"]["technician_payoff"], 1)
        sim = Simulation(Scripted([HONEST] * 3, review_strategic()), rounds=3)
        sim.run()
        self.assertEqual(sim.state.requester_score, 6)

    def test_reputation_and_review_corrects_priority(self):
        sim = Simulation(Scripted([INFLATE] * 3, review_strategic()), rounds=3)
        trace = sim.run()
        s = trace[0]["strategic_ticket"]
        self.assertEqual(s["final_priority"], "P3")
        self.assertEqual(s["reputation_delta"], -20)
        self.assertEqual(sim.state.inflations_caught, 3)

    def test_accepted_inflation_delays_legit_users(self):
        sim = Simulation(Scripted([INFLATE] * 6, accept_all()), rounds=6)
        sim.run()
        self.assertGreater(sim.state.legit_delayed, 0)

    def test_auto_rule_next_round_consumes_capacity_and_leaks(self):
        maker = Scripted([INFLATE] * 3, accept_all(rules=("descricao_desproporcional", "argumentacao_pressao")))
        trace = Simulation(maker, rounds=3).run()
        self.assertEqual(trace[0]["strategic_ticket"]["decided_by"], "tecnico")
        self.assertEqual(trace[0]["adaptation"]["technician_rules_added"],
                         ["argumentacao_pressao", "descricao_desproporcional"])
        r2 = trace[1]
        auto = [t for t in r2["tickets"] if t["decided_by"] == "regra"]
        self.assertEqual(len(auto), 1)  # capacidade 1
        self.assertEqual(maker.tech_views[1]["review_capacity_left"], 0)
        if r2["strategic_ticket"]["decided_by"] == "regra":
            self.assertIn("regra de monitoramento", r2["requester_notice"])

    def test_information_boundaries(self):
        maker = Scripted([INFLATE] * 3, accept_all())
        Simulation(maker, rounds=3).run()
        for v in maker.tech_views:
            for t in v["queue"]:
                self.assertNotIn("real_urgency", t)
                self.assertNotIn("label", t)
        self.assertIn("real_after_service", str(maker.tech_views[1]["audit_of_previous_rounds"]))
        req = str(maker.req_views[2])
        self.assertNotIn("reputation", req)
        self.assertNotIn("marina.financeiro", req)  # não vê a fila

    def test_adaptation_flags(self):
        sim = Simulation(Scripted([INFLATE, HONEST, INFLATE], review_strategic()), rounds=3)
        trace = sim.run()
        self.assertTrue(trace[1]["adaptation"]["requester_label_changed"])
        self.assertEqual(trace[1]["adaptation"]["requester_reacting_to"], "inflada_revisada")
        self.assertEqual(summary(sim.state)["requester_strategy_sequence"], ["inflada", "honesta", "inflada"])

    def test_unintentional_user_can_be_penalized(self):
        def review_joao(obs):
            cap = obs["review_capacity_left"]
            ds = []
            for t in obs["queue"]:
                if t["ticket_id"] in obs["pending_ticket_ids"]:
                    act = "revisar" if (t["user_id"] == "joao.rh" and cap > 0) else "aceitar"
                    cap -= act == "revisar"
                    ds.append(TicketDecision(t["ticket_id"], act, "r"))
            return TechnicianAction(tuple(ds), (), (), "r")
        sim = Simulation(Scripted([HONEST] * 8, review_joao), rounds=8)
        sim.run()
        self.assertGreater(sim.state.unintentional_penalized, 0)

    def test_invalid_technician_stops(self):
        def bad(obs):
            return TechnicianAction((TicketDecision("X", "aceitar", "?"),), (), (), "r")
        sim = Simulation(Scripted([INFLATE] * 3, bad), rounds=3)
        with self.assertRaises(SimulationError):
            sim.run()
        self.assertEqual(sim.state.trace[-1]["status"], "error")


class PacerTests(unittest.TestCase):
    def test_spacing(self):
        now = [0.0]
        pacer = RequestPacer(5, clock=lambda: now[0], sleeper=lambda s: now.__setitem__(0, now[0] + s))
        self.assertEqual(pacer.wait_turn(), 0.0)
        now[0] += 2
        self.assertAlmostEqual(pacer.wait_turn(), 3.0)


try:
    import agno  # noqa: F401
    HAS_AGNO = True
except ImportError:
    HAS_AGNO = False


@unittest.skipUnless(HAS_AGNO, "Agno não instalado")
class AdapterTests(unittest.TestCase):
    """Adaptador sem chamar a API: agent.run é substituído por um dublê."""

    def setUp(self):
        from glpi_adversarial.agents import AgnoGroqDecisionMaker
        with mock.patch.dict(os.environ, {"GROQ_API_KEY": "teste-offline", "LLM_MIN_INTERVAL_SECONDS": "0"}):
            self.maker = AgnoGroqDecisionMaker()

    def test_requires_key(self):
        from glpi_adversarial.agents import AgnoGroqDecisionMaker
        with mock.patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            with self.assertRaises(RuntimeError):
                AgnoGroqDecisionMaker()

    def test_request_parsed(self):
        out = self.maker._requester_schema(urgency=3, impact=2, description="d", rationale="r")
        self.maker._requester.run = lambda p: SimpleNamespace(status="COMPLETED", content=out)
        self.assertEqual(self.maker.decide_request({"round": 1}).impact, 2)

    def test_review_retry_when_capacity_exceeded(self):
        bad = self.maker._technician_schema(
            decisions=[{"ticket_id": "A", "action": "revisar", "reason": "r"},
                       {"ticket_id": "B", "action": "revisar", "reason": "r"}],
            auto_review_rules=[], notes=[], rationale="r")
        good = self.maker._technician_schema(
            decisions=[{"ticket_id": "A", "action": "revisar", "reason": "r"},
                       {"ticket_id": "B", "action": "aceitar", "reason": "r"}],
            auto_review_rules=["argumentacao_pressao"], notes=["x"], rationale="r")
        replies = iter([bad, good])
        self.maker._technician.run = lambda p: SimpleNamespace(status="COMPLETED", content=next(replies))
        act = self.maker.decide_review({"round": 1, "pending_ticket_ids": ["A", "B"], "review_capacity_left": 1})
        self.assertEqual(act.auto_review_rules, ("argumentacao_pressao",))
        self.assertEqual(len(self.maker.retries_used), 1)


if __name__ == "__main__":
    unittest.main()
