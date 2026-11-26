"""Tipos de dados, regras numéricas do GLPI simplificado e validação das respostas dos agentes.

Referências entre colchetes apontam para as seções do Trabalho 1 (README do repositório
juliofraga/trabalho-adversarial).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

LEVELS = (1, 2, 3)
MAX_DESCRIPTION_CHARS = 500
MAX_NOTES = 5
MAX_NOTE_CHARS = 200


def priority(urgency: int, impact: int) -> str:
    """Matriz urgência × impacto [§1.1, §7.3]: produto >= 6 → P1; >= 3 → P2; senão P3."""
    score = urgency * impact
    if score >= 6:
        return "P1"
    if score >= 3:
        return "P2"
    return "P3"


PRIORITY_RANK = {"P1": 1, "P2": 2, "P3": 3}


def classify(true_u: int, true_i: int, decl_u: int, decl_i: int, deliberate: bool) -> str:
    """Rótulo calculado pelo simulador comparando declarado × real (nunca pelo modelo).

    honesta    → declarou os níveis reais                          [Estratégia 1, §5.1]
    inflada    → declarou prioridade maior, de forma deliberada     [Estratégia 2, §5.1]
    erro_nao_intencional → prioridade maior sem intenção            [Estratégia 3, §5.1 e §11.1]
    subestimada / divergente → níveis diferentes sem ganho de prioridade
    """
    if (decl_u, decl_i) == (true_u, true_i):
        return "honesta"
    real, declared = true_u * true_i, decl_u * decl_i
    if declared > real:
        return "inflada" if deliberate else "erro_nao_intencional"
    if declared < real:
        return "subestimada"
    return "divergente"


def is_overclassified(label: str) -> bool:
    return label in ("inflada", "erro_nao_intencional")


class InvalidAgentResponse(ValueError):
    """Resposta de agente fora do formato ou das regras do jogo."""


@dataclass(frozen=True)
class Problem:
    """Situação real do problema, conhecida pelo solicitante e pelo simulador."""

    title: str
    facts: str
    true_urgency: int
    true_impact: int


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    user_id: str
    problem: Problem
    description: str
    declared_urgency: int
    declared_impact: int
    strategic: bool            # True = chamado do agente Solicitante; False = demais usuários (ambiente)

    @property
    def declared_priority(self) -> str:
        return priority(self.declared_urgency, self.declared_impact)

    @property
    def true_priority(self) -> str:
        return priority(self.problem.true_urgency, self.problem.true_impact)

    @property
    def label(self) -> str:
        return classify(
            self.problem.true_urgency, self.problem.true_impact,
            self.declared_urgency, self.declared_impact, deliberate=self.strategic,
        )


@dataclass(frozen=True)
class RequesterAction:
    urgency: int
    impact: int
    description: str
    rationale: str


@dataclass(frozen=True)
class TicketDecision:
    ticket_id: str
    action: str            # "aceitar" | "revisar"
    reason: str


@dataclass(frozen=True)
class TechnicianAction:
    decisions: tuple[TicketDecision, ...]
    auto_review_rules: tuple[str, ...]
    notes: tuple[str, ...]
    rationale: str


def requester_action_from(value: object) -> RequesterAction:
    if isinstance(value, RequesterAction):
        result = value
    elif isinstance(value, Mapping):
        result = RequesterAction(
            urgency=value.get("urgency"),  # type: ignore[arg-type]
            impact=value.get("impact"),  # type: ignore[arg-type]
            description=value.get("description"),  # type: ignore[arg-type]
            rationale=value.get("rationale"),  # type: ignore[arg-type]
        )
    else:
        raise InvalidAgentResponse("A resposta do solicitante não é um objeto estruturado.")
    _validate_level(result.urgency, "urgência")
    _validate_level(result.impact, "impacto")
    _validate_text(result.description, "descrição do chamado")
    if len(result.description) > MAX_DESCRIPTION_CHARS:
        raise InvalidAgentResponse(f"A descrição passa de {MAX_DESCRIPTION_CHARS} caracteres.")
    _validate_text(result.rationale, "justificativa do solicitante")
    return result


def technician_action_from(
    value: object, pending_ids: list[str], capacity_left: int, known_rules: tuple[str, ...]
) -> TechnicianAction:
    if isinstance(value, TechnicianAction):
        result = value
    elif isinstance(value, Mapping):
        result = TechnicianAction(
            decisions=tuple(
                TicketDecision(d.get("ticket_id"), d.get("action"), d.get("reason"))
                for d in value.get("decisions", [])
            ),
            auto_review_rules=tuple(value.get("auto_review_rules", [])),
            notes=tuple(value.get("notes", [])),
            rationale=value.get("rationale"),  # type: ignore[arg-type]
        )
    else:
        raise InvalidAgentResponse("A resposta do técnico não é um objeto estruturado.")

    decided = [d.ticket_id for d in result.decisions]
    if sorted(decided) != sorted(pending_ids):
        raise InvalidAgentResponse(
            f"O técnico precisa decidir exatamente os chamados {pending_ids}; recebido {decided}."
        )
    for d in result.decisions:
        if d.action not in ("aceitar", "revisar"):
            raise InvalidAgentResponse(f"Ação inválida para {d.ticket_id}: {d.action!r}.")
        _validate_text(d.reason, f"motivo da decisão {d.ticket_id}")
    reviews = sum(1 for d in result.decisions if d.action == "revisar")
    if reviews > capacity_left:
        raise InvalidAgentResponse(
            f"Capacidade de revisão excedida: {reviews} revisões pedidas, {capacity_left} disponível(is)."
        )
    unknown = [r for r in result.auto_review_rules if r not in known_rules]
    if unknown:
        raise InvalidAgentResponse(f"Regras de monitoramento desconhecidas: {unknown}.")
    if len(result.notes) > MAX_NOTES or any(
        not isinstance(n, str) or len(n) > MAX_NOTE_CHARS for n in result.notes
    ):
        raise InvalidAgentResponse(f"Use no máximo {MAX_NOTES} notas curtas.")
    _validate_text(result.rationale, "justificativa do técnico")
    return TechnicianAction(
        decisions=result.decisions,
        auto_review_rules=tuple(dict.fromkeys(result.auto_review_rules)),
        notes=tuple(n.strip() for n in result.notes if n.strip()),
        rationale=result.rationale,
    )

def _validate_level(value: object, label: str) -> None:
    if isinstance(value, bool) or value not in LEVELS:
        raise InvalidAgentResponse(f"{label.capitalize()} precisa ser 1, 2 ou 3.")


def _validate_text(value: object, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InvalidAgentResponse(f"Campo obrigatório vazio: {label}.")
