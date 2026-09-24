# 1. Descrição do sistema adversarial

## 1.1 Sistema analisado

O sistema analisado é o **GLPI (Gestionnaire Libre de Parc Informatique)**, uma plataforma open source para gerenciamento de serviços de TI e ativos de tecnologia.

Dentro do GLPI, será analisada especificamente a interação relacionada à **classificação e priorização de chamados de suporte técnico**.

O escopo não contempla o funcionamento completo do GLPI. A análise será limitada ao processo no qual um usuário solicita atendimento por meio de um chamado, informa a urgência percebida para o problema, um técnico ou responsável avalia o impacto da ocorrência e o sistema utiliza essas informações para determinar a prioridade do chamado.

De forma simplificada, a interação pode ser representada como:

```text
Usuário
   │
   │ informa urgência
   ▼
Usuário
   │
   │ informa o impacto
   ▼
Sistema 
   │
   │ calcula prioridade
   ▼
Técnico 
   │
   │ realiza atendimento
   ▼
Atendimento / SLA
```

A relação entre urgência e impacto é relevante porque a prioridade atribuída ao chamado influencia sua posição no processo de atendimento e, consequentemente, o tempo esperado para sua resolução.

## 1.2 Por que essa interação é adversarial?

A interação possui características adversariais porque os participantes podem possuir **objetivos parcialmente conflitantes** e podem tomar decisões estratégicas com base nas consequências dessas decisões.

O usuário deseja que seu chamado seja atendido rapidamente e, portanto, possui incentivo para informar corretamente a urgência, mas também pode possuir incentivo para **superestimar a urgência** para aumentar a prioridade de seu chamado.

O técnico, por sua vez, precisa avaliar o impacto do chamado para representar adequadamente a situação operacional. Entretanto, suas decisões também podem ser influenciadas por fatores como quantidade de chamados na fila, carga de trabalho e necessidade de cumprir os níveis de serviço.

Assim, a classificação de um chamado não depende exclusivamente das características objetivas do problema. Ela também depende de informações fornecidas ou avaliadas pelos participantes, criando espaço para decisões estratégicas.

O caráter adversarial não pressupõe necessariamente que os participantes sejam mal-intencionados. Um participante pode simplesmente escolher uma estratégia que maximize seu próprio objetivo, mesmo que essa decisão produza consequências negativas para outros participantes ou para a distribuição dos recursos de atendimento.

---

# 2. Principais atores

Os principais atores considerados no modelo são:

1. **Solicitante** — usuário que registra o chamado e informa a urgência percebida.
2. **Técnico de suporte** — profissional responsável por analisar o chamado e avaliar seu impacto.
3. **Sistema GLPI** — mecanismo que processa as informações fornecidas e determina a prioridade de acordo com as regras configuradas.

Embora o sistema execute decisões automaticamente, ele não será tratado como um agente estratégico no mesmo sentido que o solicitante e o técnico. Ele representa o mecanismo responsável por transformar as decisões dos participantes em um resultado observável.

---

# 3. Objetivos dos atores

## 3.1 Solicitante

O principal objetivo do solicitante é obter a resolução do seu problema no menor tempo possível.

Entre seus objetivos secundários estão:

- obter uma prioridade compatível com a importância percebida do problema;
- reduzir o tempo de espera pelo atendimento;
- minimizar o impacto da indisponibilidade do serviço utilizado;
- receber atendimento dentro do SLA aplicável.

Do ponto de vista estratégico, o solicitante pode ter incentivo para declarar uma urgência maior do que a urgência efetivamente observada, caso perceba que uma maior urgência aumenta a prioridade do chamado.

## 3.2 Técnico de suporte

O principal objetivo do técnico é resolver os chamados de forma adequada, respeitando a prioridade e os níveis de serviço estabelecidos.

Entre seus objetivos estão:

- avaliar corretamente o impacto de cada chamado;
- atender os chamados prioritários;
- cumprir os SLAs;
- utilizar os recursos de atendimento de maneira eficiente;
- reduzir o tempo de resolução;
- evitar que chamados de alto impacto permaneçam sem atendimento.

O técnico também está sujeito a restrições de capacidade, como quantidade de chamados simultâneos, tempo disponível e complexidade dos problemas.

## 3.3 Sistema

O objetivo do mecanismo de priorização é produzir uma ordem de atendimento coerente com a urgência e o impacto dos chamados.

O sistema deve evitar que decisões individuais provoquem uma distribuição inadequada dos recursos de suporte, fazendo com que chamados menos relevantes sejam atendidos antes de problemas que possuem maior impacto sobre a organização.

---

# 4. Ativo ou propriedade a ser preservado

O principal ativo a ser preservado é a **distribuição justa e adequada do recurso de atendimento de suporte técnico**.

A propriedade desejada é que a prioridade dos chamados represente, de maneira real e verdadeira, a necessidade de atendimento, considerando fatores como urgência e impacto do problema.

A preservação dessa propriedade é importante porque a manipulação das informações utilizadas para determinar a prioridade pode provocar uma distribuição inadequada dos recursos.

Por exemplo, se vários usuários declararem urgência máxima independentemente da gravidade real de seus problemas, chamados que realmente possuem alta urgência podem competir pelo mesmo recurso com chamados artificialmente classificados como urgentes.

---

# 5. Ações e capacidades dos atores

## 5.1 Solicitante

O solicitante possui as seguintes capacidades:

- criar um chamado;
- descrever o problema;
- informar a urgência percebida;
- informar o impacto do chamado;
- atualizar informações do chamado;
- acompanhar o andamento do atendimento;
- observar a prioridade atribuída ao chamado.

A decisão estratégica mais importante considerada neste modelo é a **declaração da urgência e impacto**.

Para simplificar o modelo, podem ser consideradas duas estratégias:

```text
Estratégia 1: declarar a urgência e o impacto de acordo com a situação real
Estratégia 2: superestimar deliberadamente a urgência e o impacto
Estratégia 3: superestimar a urgência e o impacto de forma não intencional
```

A segunda estratégia representa um comportamento oportunista e deliberado, no qual o participante tenta obter uma prioridade maior do que aquela que seria atribuída com base na necessidade real. Já a terceira estratégia representa uma classificação incorreta, porém não intencional, decorrente de uma avaliação imprecisa da urgência ou do impacto do chamado.

## 5.2 Técnico de suporte

O técnico possui as seguintes capacidades:

- visualizar chamados aos quais possui acesso;
- analisar a descrição do problema;
- avaliar a urgência e o impacto do chamado;
- alterar ou confirmar informações de classificação;
- atender o chamado;
- atualizar o estado do chamado;
- resolver o problema.

A principal decisão estratégica considerada é a **avaliação da urgência e do impacto**.

Para simplificar o modelo, podem ser consideradas:

```text
Estratégia 1: avaliar a urgência e o impacto de acordo com a situação observada
Estratégia 2: superestimar ou subestimar a urgência e o impacto
```

---

# 6. Informações observáveis

## 6.1 Informações observáveis pelo solicitante

O solicitante consegue observar, dependendo das permissões e configurações do sistema:

- o próprio chamado;
- a descrição registrada;
- a urgência e impacto informados;
- a prioridade atribuída pelo sistema;
- o estado do chamado;
- atualizações realizadas no chamado;
- informações relacionadas ao atendimento;
- eventualmente, informações sobre SLA e prazo de atendimento.

O solicitante normalmente não possui acesso completo às informações internas utilizadas pelos técnicos para organizar toda a fila de atendimento.

## 6.2 Informações observáveis pelo técnico

O técnico pode observar:

- descrição do chamado;
- urgência informada pelo solicitante;
- impacto informado pelo solicitante;
- prioridade calculada pelo sistema;
- categoria do chamado;
- informações do usuário;
- histórico do chamado;
- estado atual do atendimento;

## 6.3 Informações observáveis pelo sistema

O sistema possui acesso aos dados registrados no chamado e às regras utilizadas para determinar sua prioridade.

Entre essas informações estão:

- urgência;
- impacto;
- prioridade;
- categoria;
- usuário;
- grupo responsável;
- histórico;
- regras de negócio;
- configurações de SLA.

---

# 7. Custos e restrições das ações

Os participantes não podem tomar decisões de forma ilimitada.

## 7.1 Restrições do solicitante

O solicitante possui restrições como:

- necessidade de fornecer informações mínimas para abertura do chamado;
- acesso limitado às informações internas da equipe de suporte;
- necessidade de justificar ou descrever o problema;
- dependência da capacidade disponível da equipe de suporte.

Além disso, uma eventual superestimação recorrente da urgência e impacto pode reduzir a confiabilidade das informações fornecidas pelo usuário.

## 7.2 Restrições do técnico

O técnico possui restrições como:

- quantidade limitada de tempo;
- número de chamados simultâneos;
- necessidade de respeitar prioridades;
- SLAs estabelecidos;
- complexidade dos problemas;
- necessidade de justificar determinadas decisões;
- informações incompletas sobre o problema relatado.

O técnico não possui capacidade ilimitada para atender todos os chamados simultaneamente. Portanto, a escolha de atender um chamado implica, direta ou indiretamente, postergar outros.

## 7.3 Restrições do sistema

O mecanismo de priorização também possui limitações:

- depende da qualidade das informações fornecidas;
- depende da configuração da matriz de prioridade;
- depende da classificação correta de urgência e impacto;
- possui informações limitadas sobre a situação real;
- pode não distinguir corretamente informações verdadeiras das informações declaradas.

---

# 8. Pressupostos do sistema

O mecanismo de priorização depende de alguns pressupostos para funcionar adequadamente.

## 8.1 Pressuposto 1 — A urgência informada representa razoavelmente a situação real

O sistema pressupõe que o solicitante fornecerá uma informação de urgência e impacto que representem, de maneira razoável, a necessidade real de atendimento.

Esse pressuposto é necessário porque o sistema utiliza a urgência e o impacto como elementos para determinar a prioridade.

### Como esse pressuposto pode falhar?

O solicitante pode superestimar deliberadamente a urgência e/ou o impacto para aumentar a prioridade do próprio chamado.

Exemplo:

```text
Problema real:
impacto baixo / urgência baixa

Informação fornecida:
impacto alto / urgência alta
```

Se esse comportamento produzir uma vantagem para o solicitante, ele poderá ser repetido em interações futuras.

Isso pode fazer com que chamados com necessidade real menor ocupem posições destinadas a chamados mais urgentes.

## 8.2 Pressuposto 2 — O impacto informado pelo solicitante representa adequadamente a situação

O sistema pressupõe que o impacto informado pelo solicitante representa de maneira adequada a quantidade de usuários, serviços ou processos afetados pelo problema.

### Como esse pressuposto pode falhar?

O solicitante pode possuir informações incompletas sobre os efeitos do problema ou interpretar de maneira incorreta sua abrangência, informando um impacto maior ou menor do que o impacto real.

Além disso, pode existir comportamento estratégico. Um solicitante que tenha interesse em obter atendimento mais rápido pode deliberadamente informar um impacto superior ao real, aumentando a prioridade resultante do chamado.

Consequentemente, chamados com características semelhantes podem receber prioridades diferentes em função da forma como seus solicitantes informam o impacto.

## 8.3 Pressuposto 3 — A prioridade calculada representa adequadamente a necessidade de atendimento

O sistema pressupõe que a combinação entre urgência e impacto é suficiente para representar a prioridade de um chamado.

### Como esse pressuposto pode falhar?

A realidade de um chamado pode possuir fatores que não são representados adequadamente apenas pela urgência e pelo impacto.

Por exemplo:

- um problema pode afetar um serviço crítico;
- existir um prazo regulatório;
- existir dependência de outro serviço;
- um problema aparentemente pequeno pode bloquear um processo essencial.

Nesse caso, a prioridade calculada pode não representar completamente a necessidade real de atendimento.

---

# 9. Síntese do cenário adversarial

O cenário pode ser resumido da seguinte forma:

```text
             ┌───────────────────┐
             │    SOLICITANTE    │
             └─────────┬─────────┘
                       │
                       │ declara urgência e impacto
                       ▼
                ┌──────────────┐
                │   CHAMADO    │
                └──────┬───────┘
                       │
                       │ entra na fila de atendimento
                       ▼
             ┌───────────────────┐
             │      TÉCNICO      │
             └─────────┬─────────┘
                       │
                       │ avalia os chamados na fila de atendimento
                       ▼
              ┌─────────────────┐
              │    SISTEMA      │
              │ Urgência +      │
              │ Impacto =       |
              | Prioridade      │
              └────────┬────────┘
                       │
                       ▼
                ┌─────────────┐
                │ ATENDIMENTO │
                └─────────────┘
                       │
                       ▼
                resultado observado
                       │
                       ▼
                 próxima rodada
```

O caráter adversarial surge porque o resultado da interação depende das decisões de diferentes participantes, cujos objetivos não são necessariamente iguais.

O solicitante pode ter incentivo para aumentar a urgência declarada para obter atendimento mais rápido, enquanto o técnico precisa distribuir sua capacidade de atendimento entre diferentes chamados e determinar o impacto de cada problema.

Dessa forma, as decisões tomadas em uma rodada podem alterar o comportamento dos participantes nas rodadas seguintes, permitindo analisar o sistema tanto como um **modelo estratégico estático**, considerando as decisões em uma interação isolada, quanto como um **modelo estratégico dinâmico**, considerando a adaptação dos participantes ao observar os resultados das interações anteriores.
