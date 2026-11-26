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