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

