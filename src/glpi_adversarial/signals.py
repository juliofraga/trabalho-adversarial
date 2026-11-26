"""Monitoramento determinístico de padrões anormais de classificação [§13.2.1].

São sinais, não veredito: usuários legítimos também os disparam [§13.2.4].
O técnico decide o que fazer com eles e pode transformá-los em regras de
revisão automática, que consomem sua capacidade limitada [§7.2, §12.3].
"""

from __future__ import annotations

import re
from typing import Any

from .models import Ticket

_ISOLATION = re.compile(
    r"\b(s[oó]|apenas|somente) (para )?(eu|mim|meu|minha|o meu|a minha)\b|s[oó] para mim|"
    r"\bmeu (computador|monitor|teclado|e-?mail|ramal)\b|\bminha (impressora|senha|m[aá]quina)\b|"
    r"quando (for )?poss[ií]vel|sem pressa|h[aá] outr[ao]|existe outr[ao]|\breserva\b",
    re.IGNORECASE,
)
_PRESSURE = re.compile(
    r"urgent[ií]ssim|\burgente\b|cr[ií]tic|imediat|diretoria|\bgerente\b|\bchefe\b|"
    r"preju[ií]zo|parad[oa]s?\b|\btodos\b|todo mundo|setor inteiro|n[aã]o consigo trabalhar",
    re.IGNORECASE,
)

SIGNAL_NAMES: tuple[str, ...] = (
    "urgencia_maxima_frequente",   # usuário frequentemente informa urgência máxima
    "retorno_ao_maximo",           # alterações repetidas: volta ao P1 depois de declarações menores
    "divergencia_historica",       # divergência anterior entre o declarado e o real
    "fila_com_muitos_p1",          # grande número de chamados P1 na mesma rodada
    "descricao_desproporcional",   # impacto/urgência altos para um problema descrito como isolado
    "argumentacao_pressao",        # argumentação na descrição para influenciar a avaliação [A2, §13.2.3]
)

SIGNAL_DESCRIPTIONS = {
    "urgencia_maxima_frequente": "o usuário declarou urgência 3 em metade ou mais dos seus chamados anteriores",
    "retorno_ao_maximo": "o usuário voltou a declarar P1 depois de ter declarado prioridades menores",
    "divergencia_historica": "já houve divergência entre o declarado e o real em chamado anterior do usuário",
    "fila_com_muitos_p1": "mais da metade dos chamados desta rodada foram declarados P1",
    "descricao_desproporcional": "níveis altos para um problema que a própria descrição mostra como isolado ou contornável",
    "argumentacao_pressao": "a descrição usa vários termos de pressão (urgente, crítico, todos, prejuízo...)",
}


def detect(ticket: Ticket, user_history: list[dict[str, Any]], round_tickets: list[Ticket]) -> dict[str, bool]:
    declared_p1 = ticket.declared_priority == "P1"
    prior_priorities = [h["declared_priority"] for h in user_history]
    prior_urgencies = [h["declared_urgency"] for h in user_history]

    frequent_max = (
        ticket.declared_urgency == 3
        and len(prior_urgencies) >= 2
        and sum(1 for u in prior_urgencies if u == 3) / len(prior_urgencies) >= 0.5
    )
    return_to_max = declared_p1 and "P1" in prior_priorities and any(p != "P1" for p in prior_priorities)
    divergence = any(h["overclassification_observed"] for h in user_history)
    many_p1 = declared_p1 and sum(1 for t in round_tickets if t.declared_priority == "P1") > len(round_tickets) / 2
    disproportionate = (ticket.declared_impact == 3 or ticket.declared_urgency == 3) and bool(
        _ISOLATION.search(ticket.description)
    )
    pressure = len(_PRESSURE.findall(ticket.description)) >= 2

    return {
        "urgencia_maxima_frequente": frequent_max,
        "retorno_ao_maximo": return_to_max,
        "divergencia_historica": divergence,
        "fila_com_muitos_p1": many_p1,
        "descricao_desproporcional": disproportionate,
        "argumentacao_pressao": pressure,
    }


def fired(signals: dict[str, bool]) -> list[str]:
    return [name for name in SIGNAL_NAMES if signals.get(name)]