# Trabalho Análise de um Sistema Adversarial — Grupo 4

### Integrantes

| Nome |
|---|
| Adriano Gebert Gomes |
| André Nunes Monteiro |
| Júlio Eduardo da Silva Fraga |
| Mariana Kegler Lorentz |
| Nilton Jansenn Lopes Ribeiro Freitas |

Apresentação: https://docs.google.com/presentation/d/1fxto918xsuBtVlP9riYURDzHwWoi5pjF/edit?usp=sharing&ouid=108593861321601844373&rtpof=true&sd=true
---

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

# 9. Organização dos elementos principais do cenário adversarial

| Ator | Objetivo | Ações ou capacidades | Informações observáveis | Restrições ou custos |
| :--- | :--- | :--- | :--- | :--- |
| **Ator 1: Solicitante** | - Obter a resolução do seu problema no menor tempo possível<br>- Reduzir o tempo de espera pelo atendimento<br>- Minimizar o impacto da indisponibilidade do serviço<br>- Receber atendimento dentro do SLA aplicável<br>- Obter prioridade compatível com a importância percebida | - Criar e descrever chamado<br>- Informar a urgência e o impacto percebidos<br>- Atualizar informações e acompanhar o andamento<br>- Decisão estratégica de declarar a urgência/impacto real, superestimar deliberadamente ou superestimar de forma não intencional | - O próprio chamado e a descrição registrada<br>- Urgência e impacto informados por ele<br>- Prioridade atribuída pelo sistema<br>- Estado atual do chamado e atualizações do atendimento<br>- Informações de SLA e prazo (dependendo do sistema) | - Necessidade de fornecer informações mínimas e descrever/justificar o problema<br>- Acesso limitado às informações internas e à fila de suporte<br>- Dependência da capacidade da equipe<br>- Perda de confiabilidade/credibilidade em caso de superestimação recorrente |
| **Ator 2: Técnico de Suporte** | - Resolver os chamados adequadamente respeitando a prioridade e os SLAs<br>- Avaliar corretamente o impacto de cada chamado<br>- Utilizar recursos de atendimento de forma eficiente<br>- Reduzir o tempo de resolução<br>- Evitar que chamados de alto impacto fiquem sem atendimento | - Visualizar e analisar a descrição dos chamados<br>- Avaliar a urgência e o impacto real do chamado<br>- Alterar ou confirmar informações de classificação<br>- Atender, atualizar o estado e resolver o chamado<br>- Decisão estratégica de avaliar conforme a situação ou superestimar/subestimar a classificação | - Descrição do chamado<br>- Urgência e impacto informados pelo solicitante<br>- Prioridade calculada pelo sistema<br>- Categoria, informações do usuário e histórico do chamado<br>- Estado atual do atendimento | - Tempo limitado e capacidade para poucos chamados simultâneos<br>- Necessidade de respeitar prioridades e cumprir SLAs estabelecidos<br>- Complexidade técnica dos problemas<br>- Necessidade de justificar determinadas decisões<br>- Lidar com informações imprecisas ou incompletas sobre o problema |
| **Ator 3: Sistema GLPI** | - Produzir uma ordem de atendimento coerente com a urgência e o impacto dos chamados<br>- Evitar que decisões individuais provoquem uma distribuição inadequada dos recursos de suporte | - Processar as informações fornecidas (urgência e impacto)<br>- Calcular e atribuir a prioridade do chamado segundo a matriz e regras de negócio configuradas | - Dados registrados no chamado (urgência, impacto, prioridade, categoria, usuário, grupo responsável)<br>- Histórico do chamado<br>- Regras de negócio e configurações de SLA | - Dependência direta da qualidade e veracidade das informações fornecidas pelos participantes<br>- Rigidez da matriz de prioridade configurada<br>- Incapacidade de distinguir autonomamente informações verdadeiras de declarações estratégicas/manipuladas<br>- Falta de contexto sobre fatores externos não representados na matriz (ex: prazos regulatórios fora do sistema) |

---

# 10. Síntese do cenário adversarial

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


# 11. Modelo Estratégico Estático

## 11.1 Modelagem de Decisão Central : 

A decisão central escolhida para o modelo estático é a **classificação do chamado**, considerada a partir da interação entre o **Solicitante** e o **Técnico de suporte**.

O Solicitante decide como declarar a urgência e o impacto do chamado. O Técnico decide se aceita a classificação declarada ou se revisa o chamado antes de atendê-lo. O Sistema GLPI não é tratado como jogador, pois apenas transforma a classificação final em prioridade, conforme definido na seção 2 do item 3.1.

As decisões são consideradas simultâneas: o Técnico define sua conduta sem saber, previamente, se aquele Solicitante declarou a classificação de forma honesta ou inflada. Essa hipótese é coerente com a seção 6, segundo a qual o Técnico observa apenas a urgência e o impacto declarados, e não a situação real do problema.

A Estratégia 3 do Solicitante descrita na seção 5.1 (superestimação não intencional) não é incluída como ação do jogo, pois não corresponde a uma escolha deliberada. Ela é tratada como uma fonte de incerteza, mais adequada ao modelo dinâmico.

## 11.2 Matriz de payoffs 

Os payoffs representam a **ordem de preferências** de cada jogador sobre os resultados possíveis, sendo 2 o resultado mais preferido  e o 0 o menos preferido. Os valores são ordinais: indicam apenas a posição de cada resultado na preferência do jogador e não devem ser comparados enre os jogadores. 

Cada célula apresenta um par (**payoff do Solicitante**, **payoff do Técnico**).
| Solicitante \  Técnico | B1: Aceitar a classificação | B2: Revisar o chamado | 
|:--- | :---: | :---: |
|**A1 : declarar honestamente** | (2,3) | (2,2) | 
|**A2 : Inflar a classificação** | (3,0) |(0,1) |

## 11.3 Significado das Ações 

**Solicitante (jogador das Linhas)**

-**A1 - Declarar Honestamente :** O solicitante informa a urgência e o impacto de acordo com a situação real do problema. Corresponde a Estratégia 1 da seção 5.1.

-**A2 - inflar a classificação:** O solicitante informa, de forma deliberada, urgẽncia e/ou impacto superiores aos reais, com o Objetivo de obter uma prioridade maior. Corresponde á Estratégia 2 da seção 5.1.1 

## 11.4 Justificativas dos Payoffs 

**Preferências do Solicitante** 

O Solicitante prefere, em primeiro lugar, obter uma prioridade superior a que seu problema justificaria, sem sofrer consequências. Em segundo lugar, prefere receber a prioridade correspondente à necessidade real. O pior resultado é ter a classíficação inflada descoberta, pois a vantagem pretendida e compromote a confiabildade das informações que fornece ( seção 7.1). 

Ordem : (inflar, Aceitar) = 3 > (Honesto, Aceitar ) = (honesto, Revisar) = 2 > ( inflar, revisar) = 0. 

**Preferências do Técnico**

O Técnico prefere uma fila que represente corretamente a necessidade de atendimento e que não exija esforço adicional de verificação, dada a sua restrição de tempo (seção 7.2). O pior resultado é atender chamados fora da ordem adequada, prejudicando chamados realmente prioritários e o cumprimento dos SLAs (seções 3.2 e 4).

Ordem: (Honesto, Aceitar) = 3 > (Honesto, Revisar) = 2 > (Inflar, Revisar) = 1 > (Inflar, Aceitar) = 0.

**Justificativa por resultados** 

| Resultado | Payoff do Solicitante | Payoff do Técnico |
| :--- | :--- | :--- |
| **(Honesto, Aceitar)** | **2** — recebe a prioridade compatível com a necessidade real do problema. | **3** — a fila representa a necessidade real e nenhum tempo é gasto com verificação. É o melhor resultado para o Técnico. |
| **(Honesto, Revisar)** | **2** — a revisão confirma a classificação, e o Solicitante recebe a mesma prioridade que receberia se o Técnico aceitasse. | **2** — a fila permanece correta, mas o Técnico consumiu tempo verificando um chamado que já estava corretamente classificado. |
| **(Inflar, Aceitar)** | **3** — obtém prioridade superior à necessária e passa à frente de outros chamados. É o melhor resultado para o Solicitante. | **0** — o recurso de atendimento é alocado de forma inadequada, e chamados de maior necessidade real podem ser atrasados ou ter o SLA descumprido. É o pior resultado para o Técnico e para o ativo da seção 4. |
| **(Inflar, Revisar)** | **0** — a manipulação é identificada, a prioridade é corrigida e o Solicitante perde credibilidade. É o pior resultado para o Solicitante. | **1** — a fila é corrigida, mas à custa do tempo de revisão. É melhor do que aceitar um chamado inflado, porém pior do que lidar com chamados honestos. |

Os dois resultados em que o Solicitante é honesto recebem o mesmo payoff para ele, pois, do seu ponto de vista, a prioridade obtida é a mesma com ou sem revisão.

## 11.5 Melhores Respostas 

A melhor resposta de um jogador é a ação que lhe proporciona o maior payoff, considerando fixa a ação do outro jogador.

**Melhores respostas do Solicitante**

- Se o Técnico **aceita** a classificação: Honesto = 2 e Inflar = 3. A melhor resposta é **Inflar**.
- Se o Técnico **revisa** o chamado: Honesto = 2 e Inflar = 0. A melhor resposta é **Declarar honestamente**.

**Melhores respostas do Técnico**

- Se o Solicitante **declara honestamente**: Aceitar = 3 e Revisar = 2. A melhor resposta é **Aceitar**.
- Se o Solicitante **infla** a classificação: Aceitar = 0 e Revisar = 1. A melhor resposta é **Revisar**.

Na matriz abaixo, os payoffs correspondentes a melhores respostas estão destacados em negrito:

| Solicitante \ Técnico | B1: Aceitar | B2: Revisar |
| :--- | :---: | :---: |
| **A1: Honesto** | (2, **3**) | (**2**, 2) |
| **A2: Inflar** | (**3**, 0) | (0, **1**) |

A melhor decisão de cada jogador depende da decisão do outro. O Solicitante só tem incentivo para inflar quando espera que o Técnico aceite a classificação; o Técnico só tem incentivo para revisar quando espera que o Solicitante infle.

## 11.6 Estrategia Dominante 

Uma estratégia  é dominante quando é a melhor resposta de um jogador independentemente  da ação escolhida pelo outro.

- **solicitante :** não possui estratégia dominante.  Inflar é a melhor resposta quando o Técnico aceita, mas declarar honestamente é melhor resposta quando o técnico revisa.
- **Técnico:** não possui estratégia dominante.  Aceitar é a melhor resposta quando o solicitante é honesto, mas Revisar é a melhor resposta quando o solicitante infla. 

postanto, **não existe etratégia dominante para nenhum dos jogadores**. Nenhum deles pode escolhar  sua ação sem considerar o comportamento esperado do outro.

## 11.7 Resultado em que nenhum jogador melhora mudando sozinho

Um resultado no qual nenhum jogador consegue melhorar seu payoff alterando sozinho sua ação corresponde a um **equilíbrio de Nash**. Na matriz, ele seria identificado por uma célula em que os dois payoffs estivessem destacados como melhores respostas.

Verificando cada resultado:

| Resultado | Desvio unilateral vantajoso | É equilíbrio? |
| :--- | :--- | :--- |
| (Honesto, Aceitar) | O Solicitante muda para Inflar e passa de 2 para 3. | Não |
| (Inflar, Aceitar) | O Técnico muda para Revisar e passa de 0 para 1. | Não |
| (Inflar, Revisar) | O Solicitante muda para Honesto e passa de 0 para 2. | Não |
| (Honesto, Revisar) | O Técnico muda para Aceitar e passa de 2 para 3. | Não |

Assim, **não existe equilíbrio de Nash em estratégias puras**. Em todos os resultados, algum jogador possui incentivo para mudar de ação, o que produz um ciclo:

```text
(Honesto, Aceitar)
        │
        │ o Solicitante percebe que pode inflar sem ser verificado
        ▼
(Inflar, Aceitar)
        │
        │ o Técnico passa a revisar os chamados
        ▼
(Inflar, Revisar)
        │
        │ o Solicitante volta a declarar honestamente
        ▼
(Honesto, Revisar)
        │
        │ o Técnico deixa de revisar, pois a revisão não traz ganho
        ▼
(Honesto, Aceitar) ...
```

Esse resultado é compatível com o enunciado, que não exige a existência de equilíbrio. A ausência de equilíbrio em estratégias puras evidencia justamente que a melhor decisão de cada participante depende da escolha do outro.

## 11.8 Avaliação do Resultado para o Sistema e para os Usuários legítimos 

O resultado mais desejável para o sistema é **(Honesto, Aceitar)**. Nele, a prioridade representa a necessidade real de atendimento e o técnico não consome tempo com verificações desnecessários, preservando o ativo definido na seção 4.

Entretanto, esse resultado **não é estável**. Quando o Técnico aceita as classificações sem verificação, o Solicitante tem incentivo para inflar a urgência e o impacto. Assim, o presuposto 8.1, de que a urgência informada representa razoavelmente a situação real, não se sustenta por si só: ele depende da existência de uma possibilidade real de revisão.

O resultado do "jogo" não é bom para o sistema nem para os usuários legítimos:

-**Para o sistema :** sempre que o técnico aceitar as classificações sem verficação, abre-se espaço para que chamados inflados ocupem possições indevidas na fila, comprometendo a distribuição  adequada do recurso de atendimento. 

-**Para os Usuários Legítimos:** eles são prejudicados de duas formas. Primeiro, chamados inflados podem ser atendidos antes dos seus, mesmo possuindo menor necessidade real. Segundo, o tempo que o técnico dedica á revisão de chamados corretamente classificados reduz a capacidade disponível para atendimento.

**Para o Téncico:**a revisão protege a fila, mas consome capacidade, uma das principais restrições descritas na seção 7.2. 

Conclui-se que, em uma interação isolada, a honestidade do Solicitante e a confiança do Técnico não se sustentam simultaneamente. A qualidade da priorização depende de mecanismos que tornem a revisão crível e que reduzam o ganho obtido com a manipulação. Esse resultado motiva a análise do modelo dinâmico, no qual o histórico e a credibilidade do Solicitante podem alterar os incentivos dos participantes ao longo das interações.

# 12 Modelo estratégico dinâmico

| Rodada | Ação do participante | Resposta do sistema ou defensor | O que se torna observável | Adaptação para a rodada seguinte |
| :--- | :--- | :--- | :--- | :--- |
| 1 | O solicitante abre um chamado rotineiro e decide inflar a urgência e o impacto para obter prioridade máxima. | O sistema processa os dados e atribui prioridade alta de forma automatizada, sem intervenção imediata do técnico. | O solicitante observa que a manipulação da urgência e do impacto garantiu atendimento imediato, enquanto o técnico percebe uma distorção na fila de atendimentos. | O solicitante conclui que inflar compensa. O técnico passa a desconfiar das métricas informadas e decide checar as próximas demandas do solicitante. |
| 2 | O solicitante repete a estratégia de inflar a urgência e o impacto em um novo chamado de baixa criticidade. | O técnico revisa o chamado, validando a real necessidade e reclassifica a prioridade par ao nível correto. | O solicitante percebe a perda de privilégio e a demora no atendimento do chamado. O técnico contata a reincidência da manipulação pelo histórico. | O solicitante sofre penalidade de credibilidade e opta por declarar honestamente da rodada seguinte. O técnico registra o perfil do solicitante. |
| 3 | Com o perfil marcado no histórico de reclassificações anteriores, o solicitante opta por declarar a urgência e o impacto corretamente. | O sistema e o técnico processam o chamado sem revisão adicional, aceitando a prioridade informada e liberando recursos. | O solicitante recebe um atendimento ágil e previsível. O técnico valida que a reputação restabeleceu eficiência da fila. | O sistema consolida uma política baseada em histórico de confiabilidade (reputação), restringindo auditorias apenas a perfis reincidentes. |

## 12.1 Diagrama do Ciclo Adaptativo

```text
             ┌───────────────────────┐
             │ Ação do Participante  │ Declaração honesta ou inflada
             └─────────┬─────────────┘
                       │
                       │ 
                       ▼
             ┌───────────────────────┐
             │ Resposta do Técnico   │ Aceitação automática ou revisão críitica
             └─────────┬─────────────┘                       
                       │
                       │ 
                       ▼
             ┌───────────────────────┐
             │     Observalidade     │ Feedback de tempo, histórico e penalidades
             └─────────┬─────────────┘                       
                       │
                       │ 
                       ▼             
             ┌───────────────────────┐
             │ Adaptação Estratégica │ Ajuste do comportamento para a próxima rodada
             └───────────────────────┘                                 
```

## 12.2 Quem observa quem?
O solicitante observa o tempo de atendimento e o status do chamado atribuído pelo sistema. O técnico observa o histórico de chamados anteriores, a consistência das justificativas e a reincidência de desvios por parte do usuário. 

## 12.3 O que cada lado consegue mudar?
O solicitante pode alterar sua estratégia de declaração (alternando entre honestidade e inflação artificial). O técnico consegue alterar o rigor da defesa, podendo instituir auditorias sistemáticas, restrições de submissão ou checagem manual baseada em perfil de risco.

## 12.4 O que dispara uma adaptação?
No lado do solicitante, o gatilho é o custo de ser pego na manipulação (atrasos e perda de credibilidade). No lado do técnico, o gatilho é a saturação da fila de atendimento e o descumprimento sistemático dos SLAs gerados por chamados falsamente priorizados.

## 12.5 Qual é o custo da adaptação para cada lado? 
Para o solicitante, o custo é o risco de ter seu chamado rebaixado, perdendo tempo de prioridade. Para o técnico, o custo é o esforço operacional e o tempo consumido na triagem e revisão manual de chamados, reduzindo a capacidade de resolução de problemas reais.

## 12.6 Em que ponto pode surgir uma corrida armamentista? 
A corrida armamentista surge quando o defensor implementa barreiras automatizadas rígidas no GLPI (como exigência de aprovação gerencial ou laudos para qualquer nível de urgência alta) e, em resposta, o solicitante passa a adotar engenharia social avançada, inserindo descrições elaboradas e técnicas para burlar o filtro automatizado sem levantar suspeitas imediatas.

# 13 Ameaças

| ID	| Cenário de ameaça | Ponto de exploração	| Pressuposto ou fraqueza |	Ativo afetado	| Probabilidade |	Impacto | Risco |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| A1 | Superestimação da urgência. O usuário pode informar uma urgência superior para o problema por meio do campo de urgência do chamado.	| Campo de urgência do chamado. |	A informação fornecida representa de fato a urgência da ocorrência. | Ordem dos chamados na fila. | 3 | 2 | 6		
| A2 | Manipular as informações para influenciar a prioridade. O usuário pode alterar ou adicionar mais informações ao chamado para elevar a prioridade. | 	Descrição e atualização das informações de urgência. | As informações fornecidas são suficientes para descrever o problema .| Classificação inadequada de prioridade. | 3 | 2 | 6						
| A3 | Repudiar a informação fornecida. O usuário pode negar posteriormente que informou prioridade urgente. | Ausência de rastreabilidade/histórico do chamado | Mecanismos de registros de alterações insuficiente | Rastreabilidade do processo de atendimento. | 2 | 2 | 4 |					

# 13.1 Diagrama de ataque:

```text
                         SUPERFÍCIE DE ATAQUE
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  USUÁRIO                                                    │
│     │                                                       │
│     │ cria chamado                                          │
│     ▼                                                       │
│  ┌──────────────┐                                           │
│  │    CHAMADO   │                                           │
│  └──────┬───────┘                                           │
│         │                                                   │
│         │ informa urgência                                  │
│         ▼                                                   │
│  ┌──────────────┐       P1                                  │
│  │   URGÊNCIA   │◄─────────────── A1: superestimação        │
│  └──────┬───────┘                                           │
│         │                                                   │
│         │                     TÉCNICO                       │
│         │                        │                          │
│         │                        │ avalia impacto           │
│         │                        ▼                          │
│         │                 ┌──────────────┐                  │
│         │                 │    IMPACTO   │◄── P2            │
│         │                 └──────┬───────┘                  │
│         │                        │                          │
│         └──────────┬─────────────┘                          │
│                    ▼                                        │
│             ┌───────────────┐                               │
│             │ REGRA DE      │                               │
│             │ PRIORIZAÇÃO   │◄── P3: exploração da regra    │
│             └───────┬───────┘                               │
│                     │                                       │
│                     ▼                                       │
│             ┌───────────────┐                               │
│             │   PRIORIDADE  │                               │
│             └───────┬───────┘                               │
│                     │                                       │
│                     ▼                                       │
│             ORDEM DE ATENDIMENTO                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
# 13.2 Ameaça mais importante: A1 - Superestimação da urgência
## 13.2.1 Como o sistema poderia responder? 
O sistema poderia detectar padrões anormais de urgência, tais como: 
Um usuário que frequentemente informa urgência máxima em seus chamados;
um grande número de chamados classificados com urgência máxima. 
Alterações repetidas da urgência;
Divergência frequente entre urgência informada e avaliação posterior do técnico.

## 13.2.2 Que informação essa resposta revelaria?
Que as alterações de urgência estão sendo monitoradas, que alterações frequentes podem ser detectadas.

## 13.2.3 Como o adversário poderia se adaptar na rodada seguinte?
O usuário pode passar a alternar a urgência. Pode também fornecer na descrição do problema, argumentações para tentar influenciar a avaliação.

## 13.2.4 Quais efeitos colaterais poderiam atingir usuários legítimos?
Se a defesa for muito rígida, pode influenciar aqueles que realmente tem urgência no atendimento e o usuário pode ter um atraso no atendimento. Agregar muitas barreiras também pode tornar a alteração da urgência complexa. Ou seja, o mecanismo de defesa precisa reduzir a manipulação sem impedir que usuários legítimos comuniquem situações realmente urgentes.

## 13.2.5 Qual risco continuaria existindo após a resposta?
O risco de informações subjetivas influenciarem a priorização.

## 13.2.6 O que o sistema precisa continuar preservando apesar das adaptações?
Apesar das adaptações do adversário, o sistema deve continuar preservando a integridade do processo de priorização, a justiça na distribuição dos recursos de atendimento, a rastreabilidade das alterações realizadas e a disponibilidade e usabilidade do sistema para usuários legítimos.
