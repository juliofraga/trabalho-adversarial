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
