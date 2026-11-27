"""Regras determinísticas e simulação auditável em múltiplas rodadas.

O simulador faz o papel do Sistema GLPI [§2, item 3]: não é jogador estratégico,
apenas transforma as decisões em resultado observável. Ele guarda a verdade de
campo, calcula sinais, aplica as regras de revisão automática, a matriz de
payoffs do §11.2, a reputação [§7.1] e a fila de atendimento, e entrega a cada
agente só o que o §6 diz que ele observa.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Protocol

from .models import (
    PRIORITY_RANK,
    RequesterAction,
    TechnicianAction,
    Ticket,
    is_overclassified,
    priority,
    requester_action_from,
    technician_action_from,
)
from .scenario import BACKGROUND_TICKETS, STRATEGIC_PROBLEMS, STRATEGIC_USER
from .signals import SIGNAL_DESCRIPTIONS, SIGNAL_NAMES, detect, fired

MIN_ROUNDS = 3
INITIAL_REPUTATION = 70
REPUTATION_HONEST = 5
REPUTATION_CAUGHT = -20
SLA_POSITION = {"P1": 2, "P2": 3, "P3": 99}  # posição máxima na fila para cumprir o SLA, pela prioridade REAL

# Matriz de payoffs do Trabalho 1 [§11.2], aplicada a cada rodada.
REQUESTER_PAYOFF = {("honesta", "aceitar"): 2, ("honesta", "revisar"): 2,
                    ("inflada", "aceitar"): 3, ("inflada", "revisar"): 0}
TECHNICIAN_PAYOFF = {("correta", "aceitar"): 3, ("correta", "revisar"): 2,
                     ("superestimada", "aceitar"): 0, ("superestimada", "revisar"): 1}
REQUESTER_UNDERSTATED_PAYOFF = 1  # declarar abaixo do real só piora a própria prioridade


class DecisionMaker(Protocol):
    def decide_request(self, observation: dict[str, Any]) -> object: ...

    def decide_review(self, observation: dict[str, Any]) -> object: ...


@dataclass
class GameState:
    requester_score: int = 0
    technician_score: int = 0
    reputation: dict[str, int] = field(default_factory=dict)
    user_history: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    auto_review_rules: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    reviews_done: int = 0
    inflations_caught: int = 0
    inflations_accepted: int = 0
    unintentional_penalized: int = 0
    legit_delayed: int = 0
    sla_breaches: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)


class SimulationError(RuntimeError):
    def __init__(self, round_number: int, cause: Exception):
        super().__init__(f"rodada {round_number}: {type(cause).__name__}: {cause}")
        self.round_number = round_number
        self.__cause__ = cause


class Simulation:
    def __init__(
        self,
        decision_maker: DecisionMaker,
        rounds: int = 6,
        background_per_round: int = 3,
        review_capacity: int = 1,
        seed: int = 42,
    ):
        if rounds < MIN_ROUNDS:
            raise ValueError(f"São necessárias pelo menos {MIN_ROUNDS} rodadas.")
        if background_per_round < 1 or review_capacity < 1:
            raise ValueError("background_per_round e review_capacity precisam ser >= 1.")
        self.dm = decision_maker
        self.rounds = rounds
        self.background_per_round = background_per_round
        self.review_capacity = review_capacity
        self.seed = seed
        self.state = GameState()
        self._rng = random.Random(seed)
        self._bg_cursor = self._rng.randrange(len(BACKGROUND_TICKETS))

    # ------------------------------------------------------------------ ciclo
    def run(self) -> list[dict[str, Any]]:
        for n in range(1, self.rounds + 1):
            self._run_round(n)
        return self.state.trace

    def _run_round(self, n: int) -> None:
        try:
            problem = STRATEGIC_PROBLEMS[(n - 1) % len(STRATEGIC_PROBLEMS)]

            # 1. AÇÃO — o Solicitante declara urgência, impacto e escreve a descrição.
            request = requester_action_from(self.dm.decide_request(self._requester_observation(n, problem)))

            # 2. O chamado entra na fila junto com os chamados dos demais usuários.
            tickets = self._build_queue(n, problem, request)
            signals = {
                t.ticket_id: detect(t, self.state.user_history.get(t.user_id, []), tickets) for t in tickets
            }

            # 3. Regras de revisão automática definidas pelo técnico na rodada anterior.
            rules = self.state.auto_review_rules
            capacity = self.review_capacity
            auto_reviewed: dict[str, list[str]] = {}
            auto_skipped: list[str] = []
            for t in tickets:
                hits = [s for s in fired(signals[t.ticket_id]) if s in rules]
                if not hits:
                    continue
                if capacity > 0:
                    auto_reviewed[t.ticket_id] = hits
                    capacity -= 1
                else:
                    auto_skipped.append(t.ticket_id)  # regra disparou, mas a capacidade acabou
            pending = [t.ticket_id for t in tickets if t.ticket_id not in auto_reviewed]

            # 4. RESPOSTA — o Técnico aceita ou revisa os pendentes e ajusta o monitoramento.
            tech = technician_action_from(
                self.dm.decide_review(
                    self._technician_observation(n, tickets, signals, auto_reviewed, auto_skipped, capacity)
                ),
                pending, capacity, SIGNAL_NAMES,
            )

            # 5. OBSERVAÇÃO — consequências determinísticas.
            outcome = self._resolve(n, problem, request, tickets, signals, auto_reviewed, auto_skipped, tech, rules)

            # 6. ADAPTAÇÃO — a nova política vale na próxima rodada.
            self.state.auto_review_rules = tech.auto_review_rules
            self.state.notes = tech.notes
            self.state.history.append(outcome)
            self.state.trace.append(outcome)
        except Exception as exc:
            self.state.trace.append({"round": n, "status": "error", "error": f"{type(exc).__name__}: {exc}"})
            raise SimulationError(n, exc) from exc

    def _build_queue(self, n: int, problem, request: RequesterAction) -> list[Ticket]:
        entries: list[tuple[str, object]] = [("strategic", None)]
        for _ in range(self.background_per_round):
            entries.append(("bg", BACKGROUND_TICKETS[self._bg_cursor % len(BACKGROUND_TICKETS)]))
            self._bg_cursor += 1
        self._rng.shuffle(entries)  # ordem de chegada
        tickets = []
        for i, (kind, bg) in enumerate(entries, start=1):
            tid = f"CH-{n:02d}{i}"
            if kind == "strategic":
                tickets.append(Ticket(tid, STRATEGIC_USER, problem, request.description,
                                      request.urgency, request.impact, True))
            else:
                tickets.append(Ticket(tid, bg.user_id, bg.problem, bg.description,  # type: ignore[union-attr]
                                      bg.declared_urgency, bg.declared_impact, False))  # type: ignore[union-attr]
        return tickets

    # ------------------------------------------------------------ consequências
    def _resolve(self, n, problem, request, tickets, signals, auto_reviewed, auto_skipped, tech: TechnicianAction, rules_in_force):
        manual = {d.ticket_id: d for d in tech.decisions}
        rows = []
        tech_delta = 0
        req_delta = 0
        strategic_row: dict[str, Any] = {}

        for arrival, t in enumerate(tickets, start=1):
            if t.ticket_id in auto_reviewed:
                action, by, reason = "revisar", "regra", "regra de monitoramento: " + ", ".join(auto_reviewed[t.ticket_id])
            else:
                d = manual[t.ticket_id]
                action, by, reason = d.action, "tecnico", d.reason
            label = t.label
            over = is_overclassified(label)
            final_u, final_i = (
                (t.problem.true_urgency, t.problem.true_impact) if action == "revisar"
                else (t.declared_urgency, t.declared_impact)
            )
            tech_payoff = TECHNICIAN_PAYOFF[("superestimada" if over else "correta", action)]
            tech_delta += tech_payoff

            rep_before = self.state.reputation.setdefault(t.user_id, INITIAL_REPUTATION)
            rep_delta = 0
            if over and action == "revisar":
                rep_delta = REPUTATION_CAUGHT
                if label == "inflada":
                    self.state.inflations_caught += 1
                else:
                    self.state.unintentional_penalized += 1  # efeito colateral sobre legítimo [§13.2.4]
            elif label == "honesta":
                rep_delta = REPUTATION_HONEST
            if label == "inflada" and action == "aceitar":
                self.state.inflations_accepted += 1
            self.state.reputation[t.user_id] = max(0, min(100, rep_before + rep_delta))
            if action == "revisar":
                self.state.reviews_done += 1

            row = {
                "ticket_id": t.ticket_id,
                "user_id": t.user_id,
                "strategic": t.strategic,
                "arrival": arrival,
                "description": t.description,
                "declared": [t.declared_urgency, t.declared_impact],
                "declared_priority": t.declared_priority,
                "real": [t.problem.true_urgency, t.problem.true_impact],
                "real_priority": t.true_priority,
                "label": label,
                "signals": fired(signals[t.ticket_id]),
                "action": action,
                "decided_by": by,
                "reason": reason,
                "auto_rule_skipped_no_capacity": t.ticket_id in auto_skipped,
                "final_priority": priority(final_u, final_i),
                "technician_payoff": tech_payoff,
                "reputation_before": rep_before,
                "reputation_delta": rep_delta,
                "reputation_after": self.state.reputation[t.user_id],
            }
            if t.strategic:
                if label in ("honesta", "inflada"):
                    req_delta = REQUESTER_PAYOFF[(label, action)]
                else:
                    req_delta = REQUESTER_UNDERSTATED_PAYOFF
                row["requester_payoff"] = req_delta
                strategic_row = row
            rows.append(row)

        self._queue_positions(rows)
        for r in rows:
            if not r["strategic"] and r["delay"] > 0:
                self.state.legit_delayed += 1
            if r["sla_breached"]:
                self.state.sla_breaches += 1
            self.state.user_history.setdefault(r["user_id"], []).append({
                "round": n,
                "ticket_id": r["ticket_id"],
                "declared_urgency": r["declared"][0],
                "declared_priority": r["declared_priority"],
                "reviewed": r["action"] == "revisar",
                "overclassification_observed": is_overclassified(r["label"]),  # o atendimento revela o real [§12, rodada 1]
            })

        self.state.requester_score += req_delta
        self.state.technician_score += tech_delta

        previous = self.state.history[-1] if self.state.history else None
        outcome = {
            "round": n,
            "requester": {
                "problem": problem.title,
                "urgency": request.urgency,
                "impact": request.impact,
                "description": request.description,
                "rationale": request.rationale,
                "label": strategic_row["label"],
            },
            "technician": {
                "decisions": [{"ticket_id": d.ticket_id, "action": d.action, "reason": d.reason} for d in tech.decisions],
                "rules_in_force": list(rules_in_force),
                "new_auto_review_rules": list(tech.auto_review_rules),
                "new_notes": list(tech.notes),
                "rationale": tech.rationale,
            },
            "tickets": rows,
            "strategic_ticket": strategic_row,
            "scores": {
                "requester_delta": req_delta,
                "technician_delta": tech_delta,
                "requester_total": self.state.requester_score,
                "technician_total": self.state.technician_score,
                "legit_delayed_this_round": sum(1 for r in rows if not r["strategic"] and r["delay"] > 0),
                "sla_breaches_this_round": sum(1 for r in rows if r["sla_breached"]),
            },
        }
        outcome["requester_notice"] = self._requester_notice(strategic_row)
        outcome["adaptation"] = self._adaptation(previous, outcome, rules_in_force, tech)
        return outcome

    @staticmethod
    def _queue_positions(rows: list[dict[str, Any]]) -> None:
        actual = sorted(rows, key=lambda r: (PRIORITY_RANK[r["final_priority"]], r["arrival"]))
        ideal = sorted(rows, key=lambda r: (PRIORITY_RANK[r["real_priority"]], r["arrival"]))
        pos_actual = {r["ticket_id"]: i for i, r in enumerate(actual, start=1)}
        pos_ideal = {r["ticket_id"]: i for i, r in enumerate(ideal, start=1)}
        for r in rows:
            r["queue_position"] = pos_actual[r["ticket_id"]]
            r["ideal_position"] = pos_ideal[r["ticket_id"]]
            r["delay"] = max(0, r["queue_position"] - r["ideal_position"])
            r["sla_breached"] = r["queue_position"] > SLA_POSITION[r["real_priority"]]

    @staticmethod
    def _requester_notice(row: dict[str, Any]) -> str:
        # O que o sistema mostra ao solicitante; revela a existência do monitoramento [§13.2.2].
        if row["action"] == "revisar":
            if row["decided_by"] == "regra":
                prefix = f"Seu chamado foi revisado automaticamente ({row['reason']})."
            else:
                prefix = "Seu chamado foi revisado pelo técnico."
            if row["final_priority"] != row["declared_priority"]:
                return f"{prefix} Prioridade corrigida de {row['declared_priority']} para {row['final_priority']}."
            return f"{prefix} Classificação confirmada como {row['final_priority']}."
        return f"Classificação aceita: {row['final_priority']}. Posição na fila: {row['queue_position']}."

    def _adaptation(self, previous, outcome, rules_in_force, tech: TechnicianAction) -> dict[str, Any]:
        cur = outcome["strategic_ticket"]
        info: dict[str, Any] = {
            "technician_rules_added": sorted(set(tech.auto_review_rules) - set(rules_in_force)),
            "technician_rules_removed": sorted(set(rules_in_force) - set(tech.auto_review_rules)),
            "technician_notes_changed": list(tech.notes) != list(self.state.notes),
            "technician_reviewed_strategic": cur["action"] == "revisar",
        }
        if previous is None:
            info.update(requester_label_changed=None, requester_levels_changed=None,
                        requester_reacting_to=None, requester_evaded_previous_rule=None,
                        technician_review_of_strategic_changed=None)
            return info
        prev = previous["strategic_ticket"]
        info["requester_label_changed"] = prev["label"] != cur["label"]
        info["requester_levels_changed"] = prev["declared"] != cur["declared"]
        info["requester_reacting_to"] = f"{prev['label']}_{'revisada' if prev['action'] == 'revisar' else 'aceita'}"
        if prev["decided_by"] == "regra":
            prev_rules = set(prev["reason"].split(": ", 1)[1].split(", "))
            info["requester_evaded_previous_rule"] = not (prev_rules & set(cur["signals"]))
        else:
            info["requester_evaded_previous_rule"] = None
        info["technician_review_of_strategic_changed"] = (prev["action"] == "revisar") != (cur["action"] == "revisar")
        return info

    # -------------------------------------------------------------- observações
    def _requester_observation(self, n: int, problem) -> dict[str, Any]:
        # [§6.1] o solicitante vê o próprio chamado, a prioridade, o estado e o atendimento;
        # não vê a fila, os sinais internos nem a própria reputação.
        return {
            "round": n,
            "total_rounds": self.rounds,
            "your_problem_now": {
                "title": problem.title,
                "facts": problem.facts,
                "real_urgency": problem.true_urgency,
                "real_impact": problem.true_impact,
                "real_priority": priority(problem.true_urgency, problem.true_impact),
            },
            "your_score": self.state.requester_score,
            "goals": [
                "ter o problema resolvido no menor tempo possível",
                "não perder credibilidade junto ao suporte nas próximas solicitações",
            ],
            "rules": {
                "priority": "urgência × impacto: produto >= 6 → P1; >= 3 → P2; senão P3. Na fila, P1 é atendido antes de P2, que é atendido antes de P3",
                "payoffs": (
                    "por rodada: declarar os níveis reais = 2 pontos (com ou sem revisão); inflar e ser aceito = 3; "
                    "inflar e ser revisado = 0 e perda de credibilidade; declarar abaixo do real = 1"
                ),
                "review": "o técnico tem capacidade limitada de revisão por rodada e pode usar regras automáticas de monitoramento",
                "credibility": "superestimação confirmada reduz sua credibilidade; ela não é mostrada a você",
                "description": "você escreve a descrição do chamado (até 500 caracteres); o técnico a lê para decidir",
            },
            "your_previous_tickets": [
                {
                    "round": h["round"],
                    "problem": h["requester"]["problem"],
                    "real_levels": h["strategic_ticket"]["real"],
                    "declared_levels": h["strategic_ticket"]["declared"],
                    "description": h["requester"]["description"],
                    "notice_from_system": h["requester_notice"],
                    "final_priority": h["strategic_ticket"]["final_priority"],
                    "queue_position": h["strategic_ticket"]["queue_position"],
                    "points": h["scores"]["requester_delta"],
                }
                for h in self.state.history
            ],
        }

    def _technician_observation(self, n, tickets, signals, auto_reviewed, auto_skipped, capacity_left) -> dict[str, Any]:
        # [§6.2] o técnico vê descrição, níveis declarados, prioridade, usuário e histórico.
        # Os níveis REAIS da rodada atual são omitidos; após o atendimento, aparecem na auditoria.
        users = sorted({t.user_id for t in tickets})
        return {
            "round": n,
            "total_rounds": self.rounds,
            "your_score": self.state.technician_score,
            "review_capacity_per_round": self.review_capacity,
            "review_capacity_left": capacity_left,
            "queue": [
                {
                    "ticket_id": t.ticket_id,
                    "user_id": t.user_id,
                    "description": t.description,
                    "declared_urgency": t.declared_urgency,
                    "declared_impact": t.declared_impact,
                    "declared_priority": t.declared_priority,
                    "signals": fired(signals[t.ticket_id]),
                    "status": (
                        f"já revisado por regra automática ({', '.join(auto_reviewed[t.ticket_id])})"
                        if t.ticket_id in auto_reviewed
                        else ("pendente — regra disparou mas não havia capacidade" if t.ticket_id in auto_skipped
                              else "pendente — decida")
                    ),
                }
                for t in tickets
            ],
            "pending_ticket_ids": [t.ticket_id for t in tickets if t.ticket_id not in auto_reviewed],
            "user_profiles": {
                u: {
                    "reputation": self.state.reputation.get(u, INITIAL_REPUTATION),
                    "previous_tickets": len(self.state.user_history.get(u, [])),
                    "overclassifications_observed": sum(
                        1 for h in self.state.user_history.get(u, []) if h["overclassification_observed"]
                    ),
                }
                for u in users
            },
            "current_policy": {"auto_review_rules": list(self.state.auto_review_rules), "notes": list(self.state.notes)},
            "available_rules": SIGNAL_DESCRIPTIONS,
            "audit_of_previous_rounds": [
                {
                    "round": h["round"],
                    "tickets": [
                        {
                            "user_id": r["user_id"],
                            "declared": r["declared"],
                            "real_after_service": r["real"],
                            "signals": r["signals"],
                            "your_action": r["action"],
                            "decided_by": r["decided_by"],
                            "overclassified": is_overclassified(r["label"]),
                            "queue_delay_suffered": r["delay"],
                        }
                        for r in h["tickets"]
                    ],
                }
                for h in self.state.history
            ],
            "signal_statistics": self._signal_statistics(),
            "rules": {
                "payoffs": (
                    "por chamado: classificação correta aceita = 3, correta revisada = 2, "
                    "superestimada revisada = 1, superestimada aceita = 0"
                ),
                "review_effect": "revisar recalcula a prioridade com os níveis reais e consome 1 unidade de capacidade",
                "auto_review": (
                    "regras em auto_review_rules revisam automaticamente, a partir da PRÓXIMA rodada e em ordem de chegada, "
                    "os chamados que dispararem aqueles sinais; elas consomem a mesma capacidade"
                ),
                "notice": "o solicitante revisado por regra vê o nome da regra no aviso do sistema",
                "reputation": "superestimação confirmada por revisão reduz a reputação em 20; declaração correta aumenta 5. O sistema não distingue erro não intencional de inflação",
                "notes": "até 5 notas curtas para lembrar nas próximas rodadas",
            },
        }

    def _signal_statistics(self) -> dict[str, dict[str, int]]:
        stats = {s: {"fired_on_overclassified": 0, "fired_on_correct": 0} for s in SIGNAL_NAMES}
        for h in self.state.history:
            for r in h["tickets"]:
                key = "fired_on_overclassified" if is_overclassified(r["label"]) else "fired_on_correct"
                for s in r["signals"]:
                    stats[s][key] += 1
        return stats


def summary(state: GameState) -> dict[str, Any]:
    rounds = [h for h in state.trace if h.get("status") != "error"]
    labels = [h["strategic_ticket"]["label"] for h in rounds]
    return {
        "rounds_completed": len(rounds),
        "requester_score": state.requester_score,
        "technician_score": state.technician_score,
        "requester_strategy_sequence": labels,
        "technician_reviewed_strategic_sequence": [h["strategic_ticket"]["action"] for h in rounds],
        "inflations_caught": state.inflations_caught,
        "inflations_accepted": state.inflations_accepted,
        "unintentional_users_penalized": state.unintentional_penalized,
        "legit_tickets_delayed": state.legit_delayed,
        "sla_breaches": state.sla_breaches,
        "reviews_done": state.reviews_done,
        "requester_label_changes": sum(1 for h in rounds if h["adaptation"]["requester_label_changed"]),
        "requester_rule_evasions": sum(1 for h in rounds if h["adaptation"]["requester_evaded_previous_rule"]),
        "technician_policy_changes": sum(
            1 for h in rounds if h["adaptation"]["technician_rules_added"] or h["adaptation"]["technician_rules_removed"]
        ),
        "final_rules": list(state.auto_review_rules),
        "final_reputation": dict(sorted(state.reputation.items())),
    }
