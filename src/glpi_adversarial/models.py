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

