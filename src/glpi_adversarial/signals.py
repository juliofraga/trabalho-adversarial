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