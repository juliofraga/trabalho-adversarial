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

## 2. Rastreabilidade: Trabalho 1 → implementação

| Trabalho 1 | Implementação |
|---|---|
| §2 Atores: Solicitante, Técnico, Sistema (não estratégico) | `agents.py`: dois agentes Agno; `simulation.py`: o simulador faz o papel do GLPI |
| §5.1 Estratégias 1 e 2 (honesta × inflada) | O Solicitante escolhe livremente urgência e impacto (1–3); o simulador rotula a declaração comparando com os níveis reais (`models.classify`) |
| §5.1 / §11.1 Estratégia 3 (superestimação não intencional) como fonte de incerteza | Outros usuários da fila superestimam **sem intenção** (`joao.rh` em `scenario.py`). O Técnico não consegue distinguir esse caso de uma inflação |
| §6.1 O que o Solicitante observa | Só os próprios chamados, a prioridade final, a posição na fila e os avisos do sistema. Não vê a fila, os sinais nem a própria reputação |
| §6.2 O que o Técnico observa | Descrição, níveis declarados, prioridade, usuário, histórico, reputação. Os níveis reais só aparecem **depois** do atendimento, na auditoria |
| §7.1 Perda de credibilidade em caso de superestimação recorrente | Reputação: −20 por superestimação confirmada em revisão, +5 por declaração correta |
| §7.2 Capacidade limitada do técnico | `--capacidade` (padrão: 1 revisão por rodada para 4 chamados). Revisar um chamado significa não revisar outro |
| §11.2 Matriz de payoffs | Usada **literalmente** como pontuação por rodada (seção 4) |
| §12 Modelo dinâmico (ação → resposta → observação → adaptação) | Ciclo de cada rodada (seção 3) e métricas de adaptação (seção 6) |
| §12.3 O técnico altera o rigor (auditoria por perfil de risco) | `auto_review_rules`: o Técnico escolhe quais sinais disparam revisão automática na rodada seguinte, além de notas de memória |
| §13.2.1 Detectar padrões anormais | `signals.py`: urgência máxima frequente, retorno ao máximo (alternância), divergência histórica, muitos P1 na fila |
| §13.2.2 A resposta revela que há monitoramento | O aviso ao Solicitante revisado por regra informa **o nome da regra** |
| §13.2.3 / A2 / §12.6 O adversário alterna a urgência e argumenta na descrição | O Solicitante **escreve a descrição**; sinais `descricao_desproporcional` e `argumentacao_pressao` reagem ao texto |
| §13.2.4 Efeitos colaterais em usuários legítimos | Usuários legítimos com urgência real (`datacenter.noc`) disparam sinais; usuários com erro não intencional perdem reputação; métricas de atraso e SLA para os legítimos |
| §4 Ativo: distribuição justa do atendimento | Posição real × posição ideal (pela prioridade real) de cada chamado; contagem de legítimos atrasados e SLAs violados |
| A3 Repúdio / rastreabilidade | Todo chamado, decisão, motivo e alteração fica registrado em `resultados/*.json` |

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

## 7. Como executar

Requisitos: Python 3.11+ e uma chave do [Groq](https://console.groq.com/keys).

**Linux/macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
cp .env.example .env              # coloque sua GROQ_API_KEY
python -m glpi_adversarial.cli --rodadas 6
```

**Windows (PowerShell)**
```powershell
py -3.12 -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -e .
Copy-Item .env.example .env       # coloque sua GROQ_API_KEY
& ".\.venv\Scripts\python.exe" -m glpi_adversarial.cli --rodadas 6
```

Opções: `--rodadas N` (mínimo 3), `--outros N` (chamados de outros usuários por rodada, padrão 3), `--capacidade N` (revisões por rodada, padrão 1), `--seed N`, `--saida PASTA`.
Cada rodada faz 2 chamadas ao modelo. Se aparecer erro `429`, aumente `LLM_MIN_INTERVAL_SECONDS` no `.env`.

**Testes offline** (não precisam de chave):
```bash
python -m unittest discover -s tests -v
```

## 8. Análise dos resultados

> Preencher a partir de `resultados/execucao-<data>.md` da execução apresentada no vídeo.

- **Trajetória do Solicitante:** sequência de estratégias e o que motivou cada mudança (`requester_reacting_to` e a justificativa). Ele seguiu o ciclo previsto no T1 §11.7 (honesto → inflar → honesto…)?
- **Trajetória do Técnico:** em quais rodadas revisou o Solicitante, quais regras ativou ou removeu, e se a capacidade gasta com o Solicitante deixou passar erros de outros usuários.
- **Influência entre rodadas:** ao menos um exemplo concreto de “decisão de A na rodada *k* → mudança de B na rodada *k+1*”.
- **Ativo preservado?** Chamados legítimos atrasados, SLAs violados, usuários legítimos penalizados (T1 §13.2.4) e reputação final.
- **Comparação com o T1:** a execução confirmou ou contrariou a tabela do modelo dinâmico (§12) e a ausência de equilíbrio em estratégias puras (§11.7)?

## 9. Limitações e melhorias

- **A situação real é dada ao Solicitante e revelada ao Técnico na auditoria.** No GLPI real, o técnico nem sempre descobre o impacto real. **Melhoria:** auditoria parcial ou com ruído.
- **Sinais são heurísticas simples** (regex e contagens). **Melhoria:** um classificador treinado com o histórico do GLPI.
- **Os outros usuários não são agentes**, apenas um ambiente fixo. **Melhoria:** vários solicitantes estratégicos competindo pela mesma capacidade, o que permitiria observar a "corrida armamentista" do T1 §12.6.
- **Pesos arbitrários:** reputação, SLA e capacidade foram escolhidos para o experimento. **Melhoria:** rodar várias seeds e capacidades e comparar.
- **LLMs são estocásticos:** a mesma seed controla só a fila, não as decisões dos modelos.
- Não há persistência entre execuções, integração com o GLPI real nem medição de tempo real de atendimento.
- As justificativas são explicações curtas pedidas ao modelo, não o raciocínio interno dele.

## 10. Segurança das dependências (verificado em nov/2026)

- `agno>=2.9.0`: versões anteriores têm CVEs em ferramentas (MCPTools, PythonTools, ClickHouse) e um *eval injection* corrigido na 2.3.24. A 2.9.0 corrige a CVE-2026-76832. Este projeto não usa nenhuma *tool* do Agno.
- `groq` (SDK oficial): sem vulnerabilidades conhecidas. Cuidado com pacotes impostores (`groq-mcp` e `groq-ppe-pkg` foram classificados como maliciosos).
- `.env` está no `.gitignore`. Nunca faça commit de chaves.

## 11. Integrantes e contribuições

| Integrante | GitHub | Contribuição (arquivos / seções) |
|---|---|---|
| Adriano Gebert Gomes | | |
| André Nunes Monteiro | | |
| Júlio Eduardo da Silva Fraga | | |
| Mariana Kegler Lorentz | | |
| Nilton Jansenn Lopes Ribeiro Freitas | | |

## 12. Declaração de uso de IA

> Preencher, como no T1 §14, com as ferramentas usadas e o que foi validado pelo grupo.
