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
