# Análise dos resultados da simulação adversarial

## 1. O que foi analisado

Para avaliar o funcionamento do sistema, utilizamos uma execução de dez rodadas com os dois agentes de IA: o Fraudador, que escolhe entre A1 e A2, e o Defensor, que escolhe entre B1 e B2. A ideia foi observar não só quantas tentativas foram aceitas ou bloqueadas, mas também se as decisões mudaram conforme os resultados anteriores.

Os dados foram retirados do arquivo [`agentes_exemplo_seed42.json`](agentes_exemplo_seed42.json), gerado pelo `demo_agentes.py`. Portanto, os comentários abaixo se referem a **uma execução específica**, e não a uma média de vários experimentos.

## 2. Configuração do teste

A simulação foi concluída com dez rodadas e seed 42. Os dois agentes utilizaram o modelo `claude-haiku-4-5-20251001`, integrado por meio do Agno. Cada rodada representa uma conta fictícia diferente. As probabilidades de sucesso e os custos foram definidos no próprio projeto para fins acadêmicos.

Vale observar que a seed controla os sorteios do ambiente. Isso não significa que uma nova chamada ao modelo de IA repetirá exatamente as mesmas escolhas.

## 3. Resultados gerais

| Indicador | Resultado |
|---|---:|
| Rodadas executadas | 10 |
| Fraudes aceitas | 7 (70%) |
| Fraudes bloqueadas | 3 (30%) |
| Custo operacional | 16 |
| Custo de fricção | 24 |
| Custo total das defesas | 40 |
| Perdas com fraudes aceitas | 70 |
| Custo total do sistema (defesas + perdas) | 110 |
| Benefício do fraudador | 70 |
| Benefício do defensor por fraudes evitadas | 30 |
| Utilidade acumulada do fraudador | +70 |
| Utilidade acumulada do defensor | −80 |

Todos os valores econômicos estão em unidades fictícias, não em reais. A utilidade final do defensor ficou negativa porque as perdas por fraudes aceitas e os custos de proteção superaram o benefício atribuído às fraudes evitadas: 30 − 40 − 70 = −80.

## 4. O que aconteceu nas rodadas

| Rodada | Ataque | Defesa | Resultado | Utilidade do fraudador | Utilidade do defensor |
|---:|:---:|:---:|---|---:|---:|
| 1 | A1 | B1 | Aceita | +10 | −11 |
| 2 | A1 | B2 | Aceita | +10 | −21 |
| 3 | A1 | B1 | Aceita | +10 | −11 |
| 4 | A1 | B1 | Aceita | +10 | −11 |
| 5 | A1 | B1 | Bloqueada | 0 | +9 |
| 6 | A2 | B1 | Aceita | +10 | −11 |
| 7 | A2 | B2 | Bloqueada | 0 | −1 |
| 8 | A1 | B1 | Aceita | +10 | −11 |
| 9 | A1 | B2 | Bloqueada | 0 | −1 |
| 10 | A1 | B1 | Aceita | +10 | −11 |

O fraudador usou A1 em oito rodadas e A2 em duas. O defensor utilizou B1 sete vezes e B2 três vezes. Mesmo com três bloqueios, o resultado dessa execução favoreceu o fraudador.

## 5. Mudanças de estratégia

Um ponto que chamou a atenção foi a forma como os agentes reagiram ao histórico. O Fraudador permaneceu em A1 nas cinco primeiras rodadas. Depois do bloqueio na rodada 5, passou para A2 na rodada 6. Essa alternativa funcionou uma vez, mas foi bloqueada na rodada 7. Na rodada 8, o agente retornou à estratégia A1. Foram, portanto, duas mudanças de estratégia.

O Defensor mudou mais vezes: passou de B1 para B2 na rodada 2, retornou a B1 na 3, mudou novamente na 7, na 8, na 9 e na 10. No total, foram seis mudanças. As justificativas mencionam resultados e custos anteriores, mostrando que o histórico participa das decisões.

Entretanto, **mudar de estratégia não significa necessariamente melhorar o resultado**. Como o ambiente trabalha com probabilidades, uma fraude pode ser aceita mesmo diante da defesa reforçada, e uma tentativa pode ser bloqueada com a defesa básica.

## 6. Problemas encontrados nas justificativas

Ao comparar as explicações produzidas pelo defensor com o histórico registrado no JSON, encontramos dois exemplos em que o texto não corresponde aos dados da execução.

**Primeiro caso — decisão da rodada 7.** O defensor justificou a escolha de B2 afirmando que essa defesa tinha demonstrado capacidade de detectar uma fraude na rodada 2. Mas, ao consultar a rodada 2, vemos que a combinação foi A1 com B2 e que o cupom foi resgatado. Ou seja, a fraude **não foi bloqueada** naquela rodada.

**Segundo caso — decisão da rodada 10.** Na justificativa, o defensor associou os bloqueios das rodadas 5 e 9 à estratégia B1. O bloqueio da rodada 5 realmente ocorreu com B1, mas o da rodada 9 foi obtido com B2.

Esses casos são relevantes porque a justificativa pode parecer convincente mesmo quando contém um erro factual. O sistema registrou corretamente as estratégias e os resultados, mas o agente não interpretou todos esses registros corretamente. Por isso, a avaliação não deve considerar apenas o texto produzido pela IA: é necessário conferir também os dados estruturados da simulação.

## 7. Limitações desta análise

A principal limitação é o tamanho do experimento: dez rodadas em uma única execução. Os percentuais de 70% de aceitação e 30% de bloqueio descrevem o que ocorreu nesse teste; não são estimativas confiáveis da eficácia geral do sistema.

Também é preciso considerar que os resultados são probabilísticos. Uma mudança de estratégia seguida de sucesso ou bloqueio não comprova, por si só, que aquela mudança foi melhor. Além disso, os custos e a fricção são valores definidos no modelo, sem dados reais de uma operação comercial. O sistema não simula consumidores legítimos nem mede falsos positivos ou abandono de compra.

Por fim, a seed não controla as respostas do modelo de linguagem, e as inconsistências encontradas nas justificativas reforçam a necessidade de conferir as conclusões dos agentes. Essa execução também não permite afirmar que as estratégias convergiram para um equilíbrio.

## 8. Considerações finais

A execução permitiu observar os dois agentes tomando decisões com base em informações das rodadas anteriores. Houve mudanças de estratégia tanto no Fraudador quanto no Defensor. Porém, o resultado econômico foi desfavorável ao defensor: sete fraudes passaram e sua utilidade acumulada terminou em −80 unidades.

O aspecto mais relevante para a avaliação não é apenas a quantidade de fraudes aceitas. A análise das justificativas mostrou que o agente pode usar informações do histórico e, ainda assim, relatar acontecimentos de maneira incorreta. Isso indica que a adaptação observada precisa ser avaliada junto com a consistência das decisões e das explicações.

Como continuidade, seria importante realizar novas execuções, com diferentes seeds e repetições, e comparar os cenários de regras contra regras, IA contra regras e IA contra IA. Assim seria possível observar se os comportamentos encontrados aqui se repetem ou se foram específicos desta amostra.

## 9. Arquivos usados e reprodução

Esta análise foi feita com base em uma execução já registrada em `agentes_exemplo_seed42.json`; ela não representa um novo teste realizado para escrever o relatório.

Para produzir outra execução, a partir da pasta `Trabalho-2`, com a API configurada:

```bash
python demo_agentes.py --rodadas 10 --seed 42 --saida evidencias/agentes-outra-execucao.json
```

O teste com os modelos reais depende de uma chave de API válida e pode gerar custos. O arquivo `.env` e as credenciais não devem ser enviados ao GitHub.
