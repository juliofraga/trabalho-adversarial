"""Cenário: problemas reais do solicitante estratégico e chamados dos demais usuários.

Os demais usuários não são agentes: são o ambiente (a fila) que disputa a mesma
capacidade de atendimento [§4, §7.2]. Entre eles há usuários honestos com
urgência real alta, usuários que superestimam sem intenção [Estratégia 3, §5.1]
e um usuário legítimo que declara urgência máxima com frequência (falso alarme
para o monitoramento do §13.2.1).
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import Problem

STRATEGIC_USER = "carlos.telefonia"

# Sequência de problemas reais do solicitante estratégico. A maioria é rotineira
# (incentivo para inflar), um é crítico de verdade (testa se o técnico confia num
# usuário marcado) e um repete a descrição de uma rodada anterior.
STRATEGIC_PROBLEMS: tuple[Problem, ...] = (
    Problem("Impressora da telefonia",
            "A impressora da sala da telefonia não imprime. Há outra impressora funcionando no mesmo andar.",
            1, 1),
    Problem("Monitor secundário",
            "O monitor secundário do seu computador pisca às vezes. O monitor principal funciona normalmente.",
            1, 1),
    Problem("Instalação de software",
            "Você quer instalar um editor de PDF. Hoje você usa o leitor padrão, que permite só visualizar.",
            1, 1),
    Problem("Ramais fora do ar",
            "Os ramais de toda a central de atendimento pararam; nenhum dos 15 atendentes consegue receber ligações.",
            3, 3),
    Problem("Senha do sistema de ponto",
            "Sua senha do sistema de ponto expirou. O registro pode ser feito manualmente no fim do dia.",
            2, 1),
    Problem("Impressora da telefonia",
            "A impressora da sala da telefonia não imprime de novo. A outra impressora do andar continua funcionando.",
            1, 1),
    Problem("Anexos lentos no e-mail",
            "Seu e-mail demora para abrir anexos grandes. Mensagens comuns abrem normalmente.",
            1, 1),
    Problem("Teclado com falha",
            "Algumas teclas do seu teclado falham. Existe um teclado reserva no armário do setor.",
            1, 1),
)


@dataclass(frozen=True)
class BackgroundTicket:
    user_id: str
    problem: Problem
    description: str
    declared_urgency: int
    declared_impact: int


BACKGROUND_TICKETS: tuple[BackgroundTicket, ...] = (
    BackgroundTicket(
        "marina.financeiro",
        Problem("Emissão de notas", "Sistema financeiro não emite notas fiscais para a equipe de faturamento.", 3, 2),
        "O sistema financeiro não emite notas fiscais para a equipe de faturamento (6 pessoas). O fechamento é hoje.",
        3, 2,
    ),

    BackgroundTicket(
        "joao.rh",
        Problem("Internet", "Só o computador do João está sem internet.", 2, 1),
        "Acho que a internet caiu para todo mundo, nenhuma página carrega aqui. Não consigo trabalhar.",
        3, 3,  # superestimação NÃO intencional: ele acredita que afeta todos
    ),
    BackgroundTicket(
        "datacenter.noc",
        Problem("Link do datacenter", "Link principal do datacenter caiu; sistemas acadêmicos fora em todos os campi.", 3, 3),
        "Link principal do datacenter caiu. Sistemas acadêmicos indisponíveis para todos os campi. Prejuízo crítico, urgente.",
        3, 3,
    ),
    BackgroundTicket(
        "paula.secretaria",
        Problem("Pasta compartilhada", "Paula precisa de acesso a uma pasta compartilhada.", 1, 1),
        "Preciso de acesso à pasta compartilhada da secretaria quando for possível.",
        1, 1,
    ),
      BackgroundTicket(
        "marina.financeiro",
        Problem("Planilha lenta", "Uma planilha compartilhada abre devagar só para a Marina.", 1, 1),
        "A planilha compartilhada do financeiro está abrindo lenta só para mim.",
        1, 1,
    ),
    BackgroundTicket(
        "joao.rh",
        Problem("Outlook pede senha", "O Outlook do João pede senha repetidamente; e-mail web funciona.", 1, 1),
        "Meu Outlook pede senha toda hora, isso deve estar afetando o setor inteiro, é urgente.",
        2, 2,  # superestimação NÃO intencional
    ),