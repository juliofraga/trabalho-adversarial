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
