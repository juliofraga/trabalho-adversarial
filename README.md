# GLPI Adversarial — Solicitante × Técnico (Trabalho 2, Grupo 4)

Protótipo funcional do sistema adversarial proposto no [Trabalho 1](https://github.com/juliofraga/trabalho-adversarial): **classificação e priorização de chamados no GLPI**. Dois agentes de software, construídos com **Agno** e o modelo **Groq** (`openai/gpt-oss-120b`), têm objetivos conflitantes:

- o **Solicitante** quer ser atendido o mais rápido possível e pode declarar a urgência e o impacto reais ou inflá-los;
- o **Técnico de suporte** quer uma fila que represente a necessidade real, mas tem **capacidade limitada de revisão**.

O **Sistema GLPI** não é jogador (T1 §2): ele é o simulador determinístico que calcula a prioridade, aplica as regras e transforma as decisões em resultado observável.

> **Pergunta central:** como as decisões de um agente influenciam o comportamento do adversário nas rodadas seguintes?
> Uma inflação aceita incentiva o Solicitante a repetir a estratégia. Uma revisão o empurra de volta à honestidade. As regras automáticas do Técnico revelam o que está sendo vigiado e levam o Solicitante a mudar de tática. A auditoria da fila leva o Técnico a endurecer ou afrouxar o monitoramento.

## 1. Escopo

Implementamos **uma única interação**: a declaração de urgência e impacto pelo Solicitante e a decisão do Técnico de **aceitar ou revisar** essa classificação (a decisão central do T1 §11.1), repetida em rodadas conectadas (o modelo dinâmico do T1 §12).

Fora do escopo: o GLPI real, o atendimento técnico em si e o cálculo de SLA em tempo real. A fila é representada pela posição de atendimento.


## 3. Ciclo de cada rodada

```
AÇÃO        Solicitante recebe a situação REAL do problema e decide urgência, impacto e descrição
              │
            Sistema monta a fila: o chamado dele + 3 chamados de outros usuários (ordem de chegada aleatória, seed fixa)
            e calcula os sinais de monitoramento de cada chamado
              │
            Regras automáticas (definidas pelo Técnico na rodada ANTERIOR) revisam os chamados que dispararem,
            em ordem de chegada, enquanto houver capacidade
              │
RESPOSTA    Técnico aceita ou revisa os chamados pendentes (dentro da capacidade restante)
            e define as regras e notas da próxima rodada
              │
OBSERVAÇÃO  Sistema calcula a prioridade final, a fila, os payoffs e a reputação.
            Solicitante recebe o aviso do sistema (que pode citar a regra que o pegou).
            Técnico recebe a auditoria: níveis reais revelados pelo atendimento e atraso sofrido por cada chamado
              │
ADAPTAÇÃO   Nova política do Técnico passa a valer; o Solicitante replaneja a partir do histórico
```

## 4. Regras do jogo (determinísticas)

- **Prioridade:** urgência × impacto, com P1 para produto ≥ 6, P2 para ≥ 3 e P3 para o resto. A fila atende P1 antes de P2, e P2 antes de P3; em empate, vale a ordem de chegada.
- **Revisão:** recalcula a prioridade com os níveis reais e consome 1 unidade de capacidade.
- **Payoffs por rodada (T1 §11.2)**

| Solicitante \ Técnico | Aceitar | Revisar |
|---|:---:|:---:|
| Honesto | (2, 3) | (2, 2) |
| Inflar | (3, 0) | (0, 1) |

  O Técnico pontua **por chamado da fila**: correto aceito = 3, correto revisado = 2, superestimado revisado = 1, superestimado aceito = 0. Declarar abaixo do real vale 1 ao Solicitante.
- **Reputação:** começa em 70, ganha +5 por declaração correta e perde −20 por superestimação confirmada em revisão. O sistema aplica a penalidade **sem distinguir intenção**.
- **SLA (simplificado):** um chamado com prioridade real P1 precisa estar até a posição 2 da fila, e um P2 até a posição 3.
- **Sinais** (`signals.py`) são heurísticas e não veredito. Usuários legítimos também os disparam.
- **Sem roteiro e sem invenção:** as decisões vêm do LLM a cada rodada. Se uma resposta violar as regras (chamado inexistente, revisões acima da capacidade, campo vazio), o adaptador pede **uma** correção. Se continuar inválida, a execução para com erro explícito e salva o histórico parcial. Os dublês roteirizados existem só em `tests/`.

## 5. Arquitetura

```
src/glpi_adversarial/
├── models.py      Tipos, matriz de prioridade, classificação honesta/inflada/erro, validação das respostas
├── scenario.py    Problemas reais do Solicitante e chamados dos demais usuários (ambiente)
├── signals.py     Monitoramento de padrões anormais (T1 §13.2.1)
├── simulation.py  "Sistema GLPI": estado, ciclo da rodada, payoffs, reputação, fila, observações por papel, métricas
├── agents.py      Adaptador Agno + Groq: dois Agent com instruções explícitas e output_schema Pydantic
├── report.py      Relatório no terminal + Markdown + JSON
├── rate_limit.py  Espaçamento entre chamadas à API
└── cli.py         Linha de comando
tests/             Verificações offline (sem API)
resultados/        Evidências de cada execução
```

O simulador depende só de um protocolo `DecisionMaker` (`decide_request`, `decide_review`). Os agentes LLM o implementam em `agents.py`.


## 6. Evidências e métricas de adaptação

O terminal mostra cada rodada em blocos **[AÇÃO] [RESPOSTA] [OBSERVAÇÃO] [ADAPTAÇÃO]**. Cada execução também salva em `resultados/`:
- `execucao-<data>.md`: tabela da evolução por rodada e detalhe de cada fila, pronto para o vídeo e a análise;
- `execucao-<data>.json`: rastro completo e auditável.

O simulador calcula estas métricas de adaptação (o LLM não as produz):

| Métrica | Significado |
|---|---|
| `requester_label_changed` | O Solicitante mudou de estratégia (honesta ↔ inflada…) em relação à rodada anterior |
| `requester_reacting_to` | O que aconteceu com ele na rodada anterior (ex.: `inflada_revisada`, `inflada_aceita`) |
| `requester_evaded_previous_rule` | Foi pego por uma regra automática e, na rodada seguinte, deixou de disparar aquele sinal |
| `technician_rules_added` / `removed` | O Técnico endureceu ou afrouxou o monitoramento |
| `technician_review_of_strategic_changed` | O Técnico passou a revisar, ou deixou de revisar, o Solicitante |

## Integrantes e contribuições

| Integrante | GitHub | Contribuição (arquivos / seções) |
|---|---|---|
| Adriano Gebert Gomes | | |
| André Nunes Monteiro | | |
| Júlio Eduardo da Silva Fraga | | |
| Mariana Kegler Lorentz | | |
| Nilton Jansenn Lopes Ribeiro Freitas |Nilton-Jansenn | Cenário da fila (problemas do solicitante, usuários honestos e superestimação não intencional) e sinais de monitoramento de padrões anormais (scenario.py, signals.py, README §5 e§6)
| Thalis Antunes da Silva | thalisantuness | Simulador determinístico, ciclo da rodada, regras de transição e SLA configurável (`simulation.py`, `tests/test_simulation.py`, README §3) |

