# Análise de Sistema Adversarial - Fraude no Resgate de Cupom de Desconto

**Disciplina:** [Engenharia de Software Adversarial]

**Grupo (5 integrantes):** 
* Benjamin Rios
* Bruno Canto
* Cassiano Henrique
* Mariana Kemmerich
* Paula Erdmann


**Data Entrega:** [06/10/2026]

**Duração da apresentação:** 10 minutos

## Sumário

1. [Descrição do Sistema Adversarial](#1-descrição-do-sistema-adversarial)
2. [Modelo Estratégico Estático](#2-modelo-estratégico-estático)
3. [Modelo Estratégico Dinâmico](#3-modelo-estratégico-dinâmico)
4. [Ameaças e Riscos](#4-ameaças-e-riscos)
5. [Contribuições dos Integrantes](#5-contribuições-dos-integrantes)
6. [Declaração de Uso de IA](#6-declaração-de-uso-de-ia-generativa)
7. [Referências](#7-referências)
8. [Nota sobre os Diagramas](#8-nota-sobre-os-diagramas)
9. [Roteiro da Apresentação (10 minutos)](#9-roteiro-da-apresentação-10-minutos)

---

## 1. Descrição do Sistema Adversarial

### 1.1 Sistema e interação analisada

O sistema analisado é uma **plataforma de e-commerce** e a interação específica avaliada é o **resgate de um cupom promocional de primeira compra** (`PRIMEIRACOMPRA10`, 10% de desconto), regra: **um cupom por pessoa física**, validado no momento do checkout.

A regra de negócio analisada estabelece que o benefício pode ser utilizado uma única vez por pessoa física. A elegibilidade é verificada durante o processo de checkout.

O trabalho não analisa o e-commerce em sua totalidade. O escopo está restrito ao fluxo:

cadastro → aplicação do cupom → validação antifraude → checkout

Durante esse fluxo, o sistema pode utilizar informações cadastrais e transacionais, como:

- CPF;
- e-mail;
- telefone;
- dispositivo;
- endereço IP;
- meio de pagamento;
- histórico de utilização do benefício.

Com base nesses sinais, o sistema pode:

- autorizar a aplicação do cupom;
- rejeitar a aplicação do cupom;
- solicitar uma verificação adicional.
### 1.2 Atores

| **Ator** | **Objetivo** | **Ações ou capacidades** | **Informações observáveis** | **Restrições ou custos** |
|---|---|---|---|---|
| **Fraudador** | Obter repetidamente o benefício promocional, reduzindo o custo das compras e evitando mecanismos de detecção. | Criar múltiplas identidades digitais; alterar dados cadastrais; variar sinais de dispositivo ou rede; realizar sucessivas tentativas de resgate. | Aceitação ou rejeição do cupom; solicitação de verificação adicional; bloqueio da conta; aprovação ou rejeição da compra. | Tempo e esforço para criação de novas identidades; necessidade de novos meios de verificação; possibilidade de bloqueio; limitação de tentativas. |
| **Sistema Antifraude (defensor)** | Impedir usos indevidos do benefício sem gerar fricção excessiva para usuários legítimos. | Validar unicidade de dados; correlacionar contas; analisar sinais cadastrais, transacionais, de dispositivo e rede; solicitar verificações adicionais; bloquear tentativas suspeitas. | Frequência e velocidade dos cadastros; repetição de dispositivos, meios de pagamento ou outros sinais; histórico de utilização do cupom; resultados das verificações anteriores. | Custo computacional e operacional; possibilidade de falsos positivos; aumento de fricção durante o checkout; eventual redução da taxa de conversão. |
| **Cliente legítimo** | Utilizar corretamente o benefício em sua primeira compra e concluir o checkout com pouca fricção. | Criar uma conta; informar dados cadastrais; aplicar o cupom; realizar verificações solicitadas; concluir a compra. | Resultado da validação do cupom; mensagens de erro; solicitações adicionais de confirmação. | Tempo necessário para concluir verificações; possibilidade de bloqueio incorreto; abandono da compra caso o processo seja excessivamente complexo. |


### 1.3 Ativos e propriedades a preservar

O principal ativo do sistema é a **integridade financeira do programa promocional**, garantindo que o desconto seja concedido somente aos usuários que atendam aos critérios estabelecidos.

Além disso, o sistema deve preservar:

- **justiça na distribuição do benefício**, evitando que um mesmo agente obtenha a vantagem repetidamente;
- **confiabilidade da regra de primeira compra**, garantindo o cumprimento das condições da promoção;
- **experiência dos clientes legítimos**, reduzindo falsos positivos e verificações desnecessárias;
- **sustentabilidade econômica da promoção**, evitando perdas causadas pelo uso indevido do cupom;
- **disponibilidade do benefício**, evitando que abusos prejudiquem usuários realmente elegíveis.

Existe, portanto, um compromisso entre **segurança e usabilidade**: controles mais rigorosos podem reduzir a ocorrência de fraude, mas também podem aumentar a fricção enfrentada pelos compradores legítimos.

### 1.4 Pressupostos do sistema

O funcionamento do mecanismo antifraude depende de alguns pressupostos.

### 1.4.1 Identificadores cadastrais representam adequadamente uma pessoa

O sistema assume que informações como **CPF, telefone e e-mail** permitem diferenciar compradores distintos.

**Como esse pressuposto pode falhar:** diferentes identidades digitais podem ser utilizadas pelo mesmo agente ou dados válidos pertencentes a terceiros podem aparecer em novos cadastros, dificultando a identificação de que diferentes contas estão relacionadas.

### 1.4.2 Verificações de contato aumentam a confiança na identidade cadastrada

O sistema assume que a confirmação de **e-mail ou telefone** representa uma barreira suficiente para dificultar a criação repetida de contas.

**Como esse pressuposto pode falhar:** um mesmo agente pode conseguir acesso a múltiplos canais de contato ou criar novas identidades digitais com baixo custo, reduzindo a eficácia desse mecanismo de validação.

### 1.4.3 Sinais técnicos e transacionais permitem correlacionar contas relacionadas

O sistema assume que informações como **dispositivo, endereço de rede, meio de pagamento e padrões de comportamento** podem indicar que diferentes contas pertencem ao mesmo agente.

**Como esse pressuposto pode falhar:** esses sinais podem variar entre diferentes tentativas. Além disso, clientes legítimos podem compartilhar determinadas características, como a mesma rede, endereço ou dispositivo, aumentando o risco de falsos positivos.


A OWASP destaca que funcionalidades que concedem valor, como promoções e recompensas, precisam considerar abusos como a criação de múltiplas contas e recomenda utilizar sinais mais estáveis do que apenas o endereço de e-mail (OWASP FOUNDATION, s.d.).


### 1.5 Por que isso é adversarial (e não um erro/acidente)

Um erro de sistema é não-intencional e não se adapta a contramedidas. Aqui, o fraudador **tem um objetivo definido** (extrair valor do cupom), **observa a resposta do sistema** a cada tentativa (bloqueio, mensagem de erro) e **ajusta deliberadamente sua estratégia** para contornar a barreira encontrada — o que caracteriza um agente racional reagindo a incentivos, e não uma falha aleatória. O próprio sistema também age de forma estratégica, reagindo aos padrões observados. Essa dupla adaptação, ao longo de rodadas, é a marca de um sistema adversarial.

> **Diagrama de contexto:** ver [`diagramas/contexto.mmd`](diagramas/contexto.mmd)
> _(exportar para `diagramas/contexto.png` — ver instruções no final deste documento)_

```mermaid
graph TD
    U["Usuário legítimo"]
    F["Fraudador (cria múltiplas contas)"]
    P["Plataforma de E-commerce"]
    C["Serviço de Cadastro / Autenticação"]
    V["Motor Antifraude (validação do cupom)"]
    PG["Gateway de Pagamento"]
    BD[("Base de Cupons e Contas")]

    U -- "cadastra-se e compra" --> C
    F -- "cria contas em lote / dados forjados" --> C
    C -- "registra conta" --> BD
    U -- "aplica cupom no checkout" --> P
    F -- "aplica cupom repetidamente" --> P
    P -- "solicita validação" --> V
    V -- "consulta histórico de uso" --> BD
    V -- "aprova ou recusa cupom" --> P
    P -- "processa pagamento" --> PG
    PG -- "confirma transação" --> P
    V -. "sinaliza padrão suspeito" .-> C
```

O cenário analisado não representa apenas um erro de software ou uma utilização acidental da promoção.

Existe um participante com objetivo próprio — o **fraudador** — que procura obter repetidamente um benefício que deveria ser concedido apenas uma vez. Para atingir esse objetivo, ele realiza ações, observa as respostas produzidas pelo sistema e pode modificar seu comportamento nas tentativas seguintes.

O **sistema antifraude** também possui um objetivo próprio: preservar a regra da promoção e reduzir perdas financeiras sem prejudicar excessivamente os clientes legítimos. Para isso, observa padrões de comportamento e pode modificar suas decisões ou exigir verificações adicionais.

Forma-se, portanto, um ciclo de interação adversarial:

```text
Ação do participante
        ↓
Resposta do sistema
        ↓
Observação do resultado
        ↓
Adaptação da estratégia
        ↓
Nova ação
```

A presença de **objetivos parcialmente conflitantes**, informações observáveis e capacidade de adaptação caracteriza o problema como um **sistema adversarial**, e não simplesmente como uma falha ou erro acidental.

---

## 1.6 Delimitação arquitetural

```text
Cliente/Fraudador
       │
       ▼
    Cadastro
       │
       ▼
Serviço de Cupons
       │
       ▼
Módulo Antifraude
       │
       ▼
    Checkout
```

O **Módulo Antifraude** recebe sinais associados à tentativa de utilização do benefício e produz uma decisão que influencia a continuidade do checkout.

De maneira simplificada:

```text
                         ┌────────────────────┐
                         │ Cliente legítimo   │
                         └─────────┬──────────┘
                                   │
                                   ▼
┌──────────────┐          ┌───────────────────┐
│  Fraudador   │─────────►│ Plataforma        │
└──────────────┘          │ de E-commerce     │
                          └─────────┬─────────┘
                                    │
                                    ▼
                          ┌───────────────────┐
                          │ Serviço de Cupons │
                          └─────────┬─────────┘
                                    │
                                    ▼
                          ┌───────────────────┐
                          │ Sistema Antifraude│
                          └─────────┬─────────┘
                                    │
                                    ▼
                          ┌───────────────────┐
                          │     Checkout      │
                          └───────────────────┘
```

---

## 1.7 Diagrama de contexto

O diagrama de contexto apresenta os principais participantes, componentes e interações existentes no cenário analisado.

O diagrama deve representar:

- **Cliente legítimo**;
- **Fraudador**;
- **Plataforma de e-commerce**;
- **Serviço de cupons**;
- **Sistema antifraude**;
- **Checkout**;
- Fluxo das solicitações e decisões tomadas pelo sistema.




---

## 2. Modelo Estratégico Estático

O modelo estratégico estático representa uma situação em que os jogadores escolhem suas estratégias considerando as possíveis ações dos demais participantes, sem uma sequência de decisões entre diferentes rodadas. Esse tipo de representação pode ser utilizado para modelar jogos finitos, nos quais os jogadores possuem um conjunto definido de estratégias e os resultados de suas escolhas podem ser representados por meio de payoffs (CRÖNERT; MINNER, 2024).

Nesse contexto, o equilíbrio de Nash constitui uma das principais formas de analisar os resultados de um jogo na forma normal, identificando situações nas quais nenhum jogador possui incentivo para alterar sua estratégia individualmente, considerando fixa a estratégia dos demais jogadores (BRANDL; BRANDT, 2024).

### 2.1 Decisão central e jogadores

A decisão central analisada é a interação entre o Fraudador e o Sistema Antifraude durante uma tentativa de resgate do cupom PRIMEIRACOMPRA10.

O Fraudador busca reutilizar um benefício destinado à primeira compra, enquanto o Sistema Antifraude busca identificar e impedir utilizações indevidas sem comprometer desnecessariamente a experiência dos usuários legítimos.

Para representar essa situação como um jogo, são considerados dois jogadores e duas estratégias possíveis para cada um.

- Jogador A (Fraudador)
  - A1 (tentativa simples): tenta reutilizar o benefício alterando poucos sinais identificadores.
  - A2 (tentativa adaptativa): tenta reutilizar o benefício modificando múltiplos sinais para dificultar a correlação entre contas.

- Jogador B (Sistema Antifraude)
  - B1 (validação básica): utiliza um conjunto limitado de sinais para verificar a elegibilidade do usuário.
  - B2 (validação reforçada): correlaciona múltiplos sinais e aplica controles adicionais para identificar tentativas de reutilização.

Os payoffs não são calculados por uma fórmula, mas atribuídos pelos autores para representar, de forma ordinal, a preferência de cada jogador entre os resultados possíveis, sendo 3 o melhor resultado e 0 o pior. Assim, importa a ordem entre os valores, e não a distância entre eles. Em cada célula da matriz, a ordem dos valores é (payoff do Fraudador, payoff do Sistema Antifraude).

### 2.2 Matriz de payoffs

| Fraudador \ Sistema Antifraude | B1 (validação básica) | B2 (validação reforçada) |
|---|---:|---:|
| A1 (tentativa simples) | (3, 0) | (0, 2) |
| A2 (tentativa adaptativa) | (3, 0) | (0, 2) |

### 2.3 Explicação das estratégias

Os payoffs não são calculados por uma fórmula, mas atribuídos pelos autores para representar, de forma ordinal, a preferência de cada jogador entre os resultados possíveis. Assim, importa a ordem entre os valores, e não a distância entre eles. A escala vai de 0 a 3 e tem o mesmo significado para os dois jogadores: 3 indica que o jogador alcança seu objetivo e ainda obtém uma vantagem sobre o adversário; 2 indica que o objetivo é preservado, mas sem vantagem adicional (um empate); 1 indica uma perda parcial, em que o objetivo é comprometido apenas em parte; e 0 indica o pior resultado, em que o objetivo é perdido por completo. Como a tentativa de resgate termina apenas de duas formas, com o benefício obtido ou impedido, a matriz utiliza somente alguns desses níveis. Em cada célula da matriz, a ordem dos valores é (payoff do Fraudador, payoff do Sistema Antifraude).

### 2.4 Justificativa dos payoffs

Os valores da matriz representam os benefícios e prejuízos relativos de cada resultado para os dois jogadores.

- (3, 0): o Fraudador consegue reutilizar o benefício diante de uma validação básica. Esse é o melhor resultado para o Fraudador, pois a tentativa é bem-sucedida e ele obtém uma vantagem. Para o Sistema Antifraude, é o pior resultado, pois a reutilização indevida não foi identificada.

- (0, 2): o Sistema Antifraude utiliza uma validação reforçada e impede a reutilização do benefício. O Fraudador não consegue obter o desconto e recebe o menor payoff. Para o Sistema, o resultado é positivo, mas não máximo: ao bloquear a tentativa, ele apenas empata com o adversário, isto é, evita o prejuízo e mantém a situação esperada, sem obter uma vantagem adicional sobre o Fraudador. Por isso o payoff é 2 e não 3. O valor 3 ficaria reservado a um resultado em que o Sistema, além de bloquear, obtivesse um ganho extra (como desarticular uma rede de contas fraudulentas), o que não ocorre neste cenário.

A mesma estrutura de payoffs é aplicada às tentativas simples e adaptativas porque, neste cenário, o resultado considerado é a obtenção ou não do benefício.

### 2.5 Melhores respostas

As melhores respostas dependem da estratégia escolhida pelo outro jogador.

Para o Fraudador:

- Se o Sistema Antifraude escolher B1, tanto A1 quanto A2 geram payoff 3 para o Fraudador. Portanto, o Fraudador é indiferente entre as duas estratégias.
- Se o Sistema Antifraude escolher B2, tanto A1 quanto A2 geram payoff 0 para o Fraudador. Portanto, o Fraudador continua indiferente entre as duas estratégias.

Para o Sistema Antifraude:

- Se o Fraudador escolher A1, o Sistema prefere B2, pois recebe 2, enquanto B1 gera 0.
- Se o Fraudador escolher A2, o Sistema também prefere B2, pois recebe 2, enquanto B1 gera 0.

Assim, B2 é a melhor resposta do Sistema a qualquer estratégia do Fraudador. Para o Fraudador, A1 e A2 são igualmente boas em cada situação.

### 2.6 Estratégias dominantes

Uma estratégia é estritamente dominante quando proporciona ao jogador um resultado melhor do que qualquer outra estratégia, independentemente da escolha do adversário.

O Sistema Antifraude possui uma estratégia estritamente dominante: B2 gera payoff 2 tanto contra A1 quanto contra A2, enquanto B1 gera payoff 0 nos dois casos.

Para o Fraudador, não existe estratégia estritamente dominante, pois A1 e A2 produzem exatamente os mesmos payoffs diante de cada escolha do Sistema.

### 2.7 Equilíbrio de Nash

Um equilíbrio de Nash ocorre quando nenhum dos jogadores consegue melhorar seu payoff alterando sua estratégia individualmente, mantendo a estratégia do outro fixa.

Na matriz proposta, existem dois equilíbrios de Nash em estratégias puras:

- (A1, B2) = (0, 2)
- (A2, B2) = (0, 2)

No equilíbrio (A1, B2), o Fraudador recebe payoff 0 e não melhora ao mudar para A2, pois continuaria recebendo 0. O Sistema recebe payoff 2 e reduziria seu resultado para 0 caso mudasse de B2 para B1.

No equilíbrio (A2, B2), ocorre o mesmo: o Fraudador continua com payoff 0 ao mudar para A1, enquanto o Sistema reduziria seu payoff de 2 para 0 caso escolhesse B1.

Os resultados com B1 não são equilíbrios, pois nessas células o Sistema melhoraria ao mudar para B2. Assim, em ambos os equilíbrios o Sistema utiliza B2, enquanto o Fraudador pode escolher entre A1 e A2 sem alterar seu payoff.

### 2.8 Conclusão do modelo estratégico estático

Considerando os payoffs definidos, a validação reforçada (B2) é a estratégia dominante do Sistema Antifraude: independentemente de o Fraudador realizar uma tentativa simples (A1) ou adaptativa (A2), B2 proporciona ao Sistema um payoff maior. Para o Fraudador, A1 e A2 são equivalentes, pois produzem o mesmo resultado diante de cada estratégia do Sistema.

Os equilíbrios de Nash são (A1, B2) e (A2, B2), nos quais o Sistema utiliza a validação reforçada e o Fraudador não obtém o benefício.

A seguir, a interação é analisada em múltiplas rodadas, nas quais os jogadores observam os resultados anteriores e adaptam suas estratégias.

---

## 3. Modelo Estratégico Dinâmico

O modelo estático representa uma decisão em um único momento. No entanto, no sistema analisado, Fraudador e Sistema Antifraude podem observar resultados anteriores e adaptar suas estratégias ao longo de novas tentativas.

Esse comportamento é compatível com jogos entre atacante e defensor em múltiplos períodos, nos quais decisões anteriores podem influenciar ações posteriores (HAUSKEN; WELBURN; ZHUANG, 2024).

No sistema proposto, o objetivo do Fraudador permanece o mesmo: reutilizar o cupom `PRIMEIRACOMPRA10`. O que muda é a estratégia utilizada para tentar contornar os controles.

A interação segue o ciclo:

**ação → resposta → observação → adaptação**

### 3.1 Rodadas adversariais

| Rodada | Ação do Fraudador | Resposta do Sistema | O que se torna observável? | Adaptação seguinte |
|---|---|---|---|---|
| **1** | Realiza uma **tentativa simples (A1)** de reutilização do cupom | O Sistema aplica os controles disponíveis e aceita ou recusa a tentativa | O Fraudador observa o resultado e os sinais que parecem influenciar a decisão | Caso a tentativa seja identificada, o Fraudador pode passar para uma abordagem mais adaptativa |
| **2** | Realiza uma **tentativa adaptativa (A2)**, modificando múltiplos sinais | O Sistema correlaciona diferentes sinais e responde à nova tentativa | O Sistema observa novos padrões de comportamento | O Sistema pode reforçar ou ajustar seus controles |
| **3** | O Fraudador realiza uma nova tentativa considerando os resultados anteriores | O Sistema utiliza o histórico acumulado e os controles ajustados | Ambos os jogadores possuem mais informações sobre o comportamento do adversário | Cada lado pode adaptar novamente sua estratégia |

A criação de múltiplas contas para obter repetidamente um benefício é um exemplo de abuso de lógica de negócio. A OWASP recomenda que sistemas de promoções não dependam de um único identificador e considerem diferentes sinais, como dispositivo, endereço IP, telefone e meio de pagamento (OWASP FOUNDATION, 2026).

### 3.2 Quem observa quem?

A observação ocorre nos dois sentidos e é fundamental para a dinâmica do jogo.

O **Fraudador** observa a resposta do Sistema Antifraude após cada tentativa, como aceitação, rejeição ou bloqueio. A partir dessas informações, pode avaliar se sua estratégia foi eficaz e decidir se deve mantê-la ou adaptá-la na rodada seguinte.

O **Sistema Antifraude** observa os cadastros, as tentativas de resgate, o histórico de utilização e os padrões de comportamento. Essas informações podem ser utilizadas para identificar comportamentos suspeitos e ajustar os controles aplicados nas rodadas seguintes.

Assim, cada rodada pode gerar novas informações para ambos os jogadores, permitindo que suas estratégias sejam modificadas ao longo do tempo.

### 3.3 O que cada lado consegue modificar?

Em cada rodada, os jogadores podem modificar diferentes elementos de suas estratégias.

O **Fraudador** pode modificar os elementos utilizados em sua tentativa de reutilização do cupom, como dados da conta, informações de contato, dispositivo, endereço IP ou outros sinais considerados relevantes pelo sistema.

O **Sistema Antifraude** pode modificar seus mecanismos de validação, como as regras utilizadas, os limites de tentativas e a quantidade ou combinação de sinais analisados.

Dessa forma, a adaptação de cada jogador ocorre sobre elementos que estão sob seu controle. O Fraudador modifica a forma como realiza a tentativa, enquanto o Sistema modifica a forma como realiza a validação.

### 3.4 O que dispara uma adaptação?

A adaptação ocorre quando um jogador obtém novas informações a partir do comportamento do adversário ou do resultado de uma rodada.

Para o **Fraudador**, uma rejeição ou bloqueio pode indicar que os controles utilizados pelo Sistema foram suficientes para identificar a tentativa. A partir dessa informação, o Fraudador pode modificar sua estratégia na rodada seguinte.

Para o **Sistema Antifraude**, o surgimento de novos padrões de abuso ou a identificação de tentativas que não foram detectadas pelos controles existentes pode indicar a necessidade de ajustar as regras de validação.

Assim, o resultado de uma rodada pode alterar as estratégias utilizadas na rodada seguinte, caracterizando o processo de adaptação do jogo dinâmico.

### 3.5 Custo da adaptação

A adaptação possui custos para os dois jogadores.

Para o **Fraudador**, modificar sua estratégia pode exigir maior esforço, novos dados ou utilização de diferentes recursos para realizar a tentativa.

Para o **Sistema Antifraude**, aumentar a quantidade de sinais analisados e aplicar controles adicionais pode elevar a complexidade da validação e aumentar o risco de falsos positivos ou de dificuldades para usuários legítimos.

Assim, cada jogador precisa considerar não apenas a possibilidade de obter um resultado favorável, mas também o custo associado à adaptação de sua estratégia.


### 3.6 Diagrama do ciclo adaptativo

```mermaid
flowchart LR
    A["Fraudador realiza tentativa"]
    B["Sistema avalia"]
    C["Sistema responde"]
    D["Fraudador observa"]
    E["Fraudador adapta"]
    F["Sistema identifica padrão"]
    G["Sistema adapta controles"]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> A
    C --> F
    F --> G
    G --> B
```
---


## 4. Ameaças e Riscos

Nesta seção, os identificadores A1, A2 e A3 representam cenários de ameaça e não devem ser confundidos com as estratégias A1 – Tentativa simples e A2 – Tentativa adaptativa utilizadas no modelo estratégico das Partes 2 e 3.

### 4.1 Pontos de Exploração

A interação analisada — _cadastro → aplicação do cupom → checkout_ — possui quatro pontos principais de exploração, onde regras, interfaces ou pressupostos podem ser contornados:

|  | Ponto de Exploração | Descrição | Pressuposto ou Fraqueza Associada |
|---|---|---|---|
| P1 | Interface de Cadastro | Canal por onde o fraudador cria contas e insere dados (e-mail, CPF, telefone) | Sistema assume que e-mail/telefone válidos implicam pessoa real e distinta |
| P2 | Regra "Um cupom por CPF" | Validação de unicidade do benefício por pessoa física | Verificação e marcação de uso não são atômicas — janela de race condition |
| P3 | Validação de Identidade (CPF) | Camada que verifica formato e dígito verificador do CPF | Assume que CPF válido = titular autêntico, ignorando CPFs de fachada ou vazados |
| P4 | Regra de Negócio do Cupom | Lógica de aplicação do desconto no checkout | Ausência de correlação entre múltiplos sinais (dispositivo, IP, pagamento) |

### 4.2 Diagrama de Superfície de Ataque

O diagrama abaixo representa visualmente os pontos de exploração (P1-P4), os componentes do sistema envolvidos e o ativo a preservar.

```mermaid
flowchart TD
    subgraph Ator["Ator Adversarial"]
        F["Fraudador"]
    end

    subgraph Sistema["Sistema de Resgate de Cupom"]
        I1["P1 - Interface de Cadastro"]
        C1["P3 - Validação de Identidade"]
        R1["P2 - Regra: Um cupom por CPF"]
        C2["P4 - Regra de Negócio do Cupom"]
        DB[("Base de Dados")]
    end

    subgraph Ativo["Ativo a Preservar"]
        A1["Integridade Financeira do Programa"]
        A2["Justiça na Distribuição do Benefício"]
    end

    F  -- "1. Cria múltiplas contas"      --> I1
    F  -- "2. Insere CPFs de terceiros"   --> C1
    F  -- "3. Explora race condition"     --> R1
    F  -- "4. Mascara IP/dispositivo"     --> C2

    I1 --> C1
    C1 --> R1
    R1 --> C2
    C2 --> DB
    DB --> A1
    DB --> A2
```

### 4.3 Análise de Ameaças com STRIDE

Após a identificação dos pontos de exploração da superfície de ataque, foi utilizado o modelo **STRIDE** como apoio para classificar possíveis ameaças relacionadas à interação analisada: **cadastro → aplicação do cupom → checkout**.

O STRIDE organiza as ameaças em seis categorias:

- **Spoofing (Falsificação de identidade):** tentativa de se passar por outra identidade;
- **Tampering (Adulteração):** alteração indevida de dados ou do estado do sistema;
- **Repudiation (Repúdio):** dificuldade de comprovar posteriormente que determinada ação foi realizada;
- **Information Disclosure (Divulgação de informação):** exposição indevida de informações;
- **Denial of Service (Negação de serviço):** comprometimento da disponibilidade de um serviço;
- **Elevation of Privilege (Elevação de privilégio):** obtenção de uma capacidade ou benefício que o participante não deveria possuir.

Neste trabalho, o STRIDE não substitui os cenários de ameaça ou a avaliação de riscos. Ele é utilizado como uma etapa intermediária entre a **superfície de ataque** e os **cenários concretos de ameaça**, ajudando a verificar sistematicamente quais tipos de ameaça podem estar relacionados aos pontos P1-P4.

| Categoria STRIDE | Aplicação no sistema analisado | Pontos relacionados |
|---|---|---|
| **Spoofing** | O fraudador pode tentar aparentar ser um novo cliente utilizando contas distintas ou dados de terceiros para obter novamente o benefício | P1 e P3 |
| **Tampering** | Uma tentativa pode explorar inconsistências no estado da aplicação do cupom, principalmente quando validação e atualização não ocorrem de maneira atômica | P2 e P4 |
| **Repudiation** | Registros insuficientes podem dificultar a reconstrução das tentativas e a associação de diferentes ações a uma mesma origem | P1 e P4 |
| **Information Disclosure** | As respostas do Sistema Antifraude podem revelar indiretamente quais sinais influenciam a aceitação ou rejeição do benefício | P3 e P4 |
| **Denial of Service** | Um grande volume de tentativas pode consumir recursos dos serviços de cadastro, validação ou aplicação do cupom e afetar usuários legítimos | P1, P2 e P4 |
| **Elevation of Privilege** | O fraudador pode obter um benefício para o qual não deveria ser elegível ao conseguir ser tratado como cliente de primeira compra | P2 e P4 |

Uma mesma superfície pode estar relacionada a mais de uma categoria STRIDE. Da mesma forma, nem todas as categorias precisam resultar em um cenário prioritário de ameaça.

A utilização do STRIDE estabelece a seguinte relação dentro da análise:

**Ponto de exploração → Categoria STRIDE → Cenário de ameaça → Ativo afetado → Impacto → Risco**

A partir dessa classificação, são detalhados a seguir os cenários considerados mais relevantes para a interação analisada.

---

### 4.4 Cenários de Ameaça

##### A1 - Race Condition no Resgate do Cupom

Um fraudador pode disparar dezenas de requisições simultâneas de resgate do mesmo cupom por meio da regra "um cupom por CPF" (P2), aproveitando a separação entre "CPF ainda não usou" e a marcação "cupom utilizado", causando consumo múltiplo do benefício e perda financeira direta sobre a integridade financeira do programa promocional.

A OWASP classifica esse tipo de falha como uma _race condition_ onde o resultado depende do timing das operações concorrentes, permitindo que uma lógica que deveria ser "apenas uma vez" seja executada múltiplas vezes (OWASP FOUNDATION, 2026). Estudos recentes sobre fraude em promoções de e-commerce confirmam que operações de resgate de valor — cupons, cashback, subsídios — são alvos recorrentes desse tipo de abuso, especialmente porque cada requisição individual é sintaticamente válida (LI et al., 2025)

##### A2 - Uso de CPFs de Terceiros

Um fraudador pode utilizar CPFs reais de terceiros obtidos em vazamentos de dados por meio da validação de identidade (P3), aproveitando o pressuposto de que "CPF válido = pessoa autêntica" e que a mera validação de formato/dígito verificador é suficiente, causando resgate indevido do benefício por agluém que não é o titular legítimo do CPF sobre a justiça na distribuição do benefício e a confiança no programa.

A OWASP recomenda que sistemas que dispensam valor não dependam de um único identificador e considerem sinais como dispositivo, endereço IP, telefone e meio de pagamento (OWASP FOUNDATION, 2026). O estudo de Li et. al (2025) sobre fraude em promoções na plataforma Meituan documenta que os fraudadores frequentemente usam identidades sintéticas ou de terceiros e organizam-se em grupos para diluir o comportamento fraudulento entre transações legítimas.

##### A3 - Multi-accounting com E-mails Descartáveis

Um fraudador pode criar múltiplas contas utilizando serviços de e-mail descartáveis e SIMs virtuais por meio da interface de cadastro (P1), aproveitando a fraqueza da verificação por e-mail/telefone que não garante que uma pessoa real e distinta está por trás de cada cadastro, causando esgotamento prematuro do orçamento promocional e exclusão de clientes legítimos sobre a integridade financeira e a disponibilidade do benefício.

A OWASP documenta que _multi-accounting_ é um padrão de abuso comum onde uma pessoa cria muitas contas para reivindicar recompensas múltiplas vezes, e que sinais de identidade além do e-mail — como fingerprint de dispositivo, verificação de telefone e KYC —são necessários para mitigar esse vetor (OWASP FOUNDATION, 2026). Li et. al (2025) observam que 82% dos usuários envolvidos em fraudes de promoção eram usuários comuns que também realizavam transações legítimas, o que torna o multi-accounting especialmente difícil de detectar por métodos tradicionais baseados apenas em comportamento individual.

### 4.5 Avaliações de Riscos

| ID | Cenário de Ameaça | Ponto de Exploração | Pressuposto ou Fraqueza | Ativo Afetado | Probabilidade | Impacto | Risco |
|---|---|---|---|---|---|---|---|
| A1 | Race condition no resgate do cupom | P2 | Verificação e marcação não são atômicas | Integridade financeira | 3 | 3 | 9 |
| A2 | Uso de CPFs de terceiros | P3 | CPF válido = pessoa autêntica | Justiça na distribuição | 2 | 3 | 6 |
| A3 | Multi-accounting com e-mails descartáveis | P1 | E-mail/telefone = pessoa real | Integridade financeira | 3 | 2 | 6 |

Escala utilizada:

- Probabilidade: 1 = baixa, 2 = média, 3 = alta
- Impacto: 1 = baixo, 2 = médio, 3 = alto
- Risco = Probabilidade × Impacto

### 4.6 Ameaça Prioritária: A1 - Race Condition

A ameaça A1 é a de maior prioridade (risco 9). A race condition é explorável com ferramentas simples, não requer identidades falsas ou dados vazados, e o impacto é direto sobre o orçamento promocional. A OWASP classifica _race conditions_ como uma das falhas de lógica de negócio mais críticas porque os controles tradicionais (WAF, autenticação) não as detectam — cada requisição individual é "válida" do ponto de vista sintático (OWASP FOUNDATION, 2026).

##### Como o sistema poderia responder:

A correção fundamental é tornar a operação de resgate atômica — uma única declaração de banco de dados, uma unique constraint, um row lock ou uma transação — de modo que requisições concorrentes não possam se intercalar (SecureLayer7, 2026). Em vez de ler o estado do cupom, verificar se está disponível, e depois atualizar (padrão read-then-write), o sistema deve executar uma operação condicional única:

```
UPDATE cupons SET usado = 1 WHERE codigo = 'PRIMEIRACOMPRA10' AND cpf = ? AND usado = 0;
```

Se rowcount for 0, o cupom já foi usado ou o CPF não é elegível. Se for 1, a operação é bem-sucedida. O banco garante a atomicidade — nenhuma outra requisição pode intercalar entre o check e o update. A SecureLayer7 (2026) recomenda ainda idempotency keys para operações que devem acontecer uma única vez e testes com requisições concorrentes (não apenas sequenciais) em endpoints sensíveis.

##### Que informação esta resposta revelaria:

O sistema passaria a registrar tentativas de resgate concorrentes. Requisições simultâneas com o mesmo CPF ou código de cupom gerariam logs com padrões distintos: timestamp collapse (múltiplas requisições no mesmo segundo), bursts de conexões concorrentes e repeated success on one-shot operation (o mesmo cupom retornando sucesso múltiplas vezes antes da correção). Esses sinais indicam a presença de um agente automatizado — não de um usuário humano, cujo comportamento típico é sequencial e espaçado no tempo.

##### Como o adversario poderia se adaptar na rodada seguinte:

Após a correção atômica, o fraudador observaria que requisições simultâneas não funcionam mais. A adaptação natural seria:

- Aumentar a variabilidade de CPFs por tentativa, em vez de repetir o mesmo — mas isso esbarra no custo de obter CPFs válidos.
- Distribuir as tentativas ao longo do tempo para evitar detecção por burst, mas isso reduz a eficiência da automação.
- Mudar para exploração de outros pontos (A2 ou A3), buscando identidades que o sistema ainda não consegue correlacionar.
- Fragmentar grupos: Li et al. (2025) observam que fraudadores podem fragmentar grupos para esconder padrões de coesão espacial e temporal, ou usar identidades sintéticas/roubadas para reduzir a frequência de transações por conta. Isso eleva o custo operacional do adversário, mas é uma adaptação plausível.
- Testar variantes da race condition em outras operações: a SecureLayer7 (2026) lista explicitamente "overdraw de saldo", "bypass de limite de taxa ou quantidade" e "bypass do contador" como alvos análogos. O fraudador pode migrar para cashback, gift cards ou outras operações que dispensam valor.

##### Quais efeitos colaterais poderiam atingir usuários legítimos:

- **Falsos positivos por CPF compartilhado:** se a validação usar combinações de sinais muito restritivas (CPF + dispositivo + IP), um usuário legítimo que acessa de um dispositivo novo pode ser bloqueado injustamente.
- **Bloqueio de famílias ou residências:** se o sistema usar IP ou dispositivo como sinal de correlação, moradores de uma mesma casa podem ser erroneamente identificados como multi-accounting.
- **Falhas de idempotência:** um usuário legítimo que clicar duas vezes no botão "Aplicar cupom" por latência pode receber erro confuso ou ter a compra abortada — a menos que o sistema use idempotency keys (SecureLayer7, 2026).
- **Sobreposição legítima de padrões:** Li et al. (2025) mostram que usuários normais também podem exibir padrões que se assemelham a fraude — por exemplo, comprar produtos populares promocionais no mesmo período ou na mesma loja — o que gera falsos positivos mesmo em sistemas sofisticados.

##### Qual risco continuaria existindo após a resposta:

- **A2 e A3 permanecem:** a race condition é apenas um vetor. O uso de CPFs de terceiros e multi-accounting com e-mails descartáveis continuam viáveis se não houver verificação de identidade mais robusta.
- **Race conditions em outras operações:** conforme a SecureLayer7 (2026), o mesmo padrão pode ser testado em qualquer operação que envolva um recurso limitado. O fraudador pode migrar para cashback, gift cards ou subsídios.
- **Complexidade do controle:** cada nova camada de validação adiciona latência e pontos de falha que podem degradar a experiência do usuário. Li et al. (2025) apontam que mesmo detectores sofisticados geram falsos positivos e falsos negativos — a fraude é um problema em aberto.

##### O que o sistema precisa continuar preservando:

- **Conversão de clientes legítimos:** a fricção adicionada não pode ser tão alta que usuários genuínos abandonem a compra. A OWASP recomenda que ações que dispensam valor sejam "mais difíceis do que ações que não dispensam", mas a assimetria deve ser calibrada (OWASP FOUNDATION, 2026).
- **Transparência e reparabilidade:** usuários legítimos falsamente bloqueados precisam de um canal claro para contestar.
- **Justiça na distribuição:** o objetivo final é garantir que o benefício chegue a quem realmente é um novo cliente.

## 5. Contribuições dos Integrantes

O desenvolvimento do trabalho foi dividido entre os cinco integrantes do grupo, buscando distribuir as principais etapas da análise adversarial e manter a integração entre as diferentes partes do relatório.

| Integrante | Contribuição principal |
|---|---|
| **Bruno Canto** | Definição da ideia central e escolha do tema do trabalho. Desenvolvimento da **Parte 1 — Descrição do Sistema Adversarial**, incluindo delimitação do sistema, atores, objetivos, ativos, pressupostos e caracterização do cenário adversarial. |
| **Benjamin Rios** | Desenvolvimento da **Parte 2 — Modelo Estratégico Estático**, incluindo definição dos jogadores e estratégias, matriz de payoffs, melhores respostas, estratégias dominantes e análise dos equilíbrios. |
| **Paula Erdmann** | Desenvolvimento da **Parte 3 — Modelo Estratégico Dinâmico**, incluindo construção das rodadas adversariais e análise do ciclo de ação, resposta, observação e adaptação. |
| **Mariana Rodriges** | Desenvolvimento da **Parte 4 — Ameaças e Riscos**, incluindo identificação dos pontos de exploração, cenários de ameaça, classificação STRIDE, avaliação de riscos e análise da ameaça prioritária. |
| **Cassiano Henrique** | Colaboração no desenvolvimento da **Parte 4 — Ameaças e Riscos** e realização da **revisão geral do README**, verificando organização, clareza, coerência e integração entre as diferentes partes do trabalho. |

Embora as seções tenham sido divididas entre os integrantes, o grupo realizou discussões conjuntas sobre o cenário analisado e revisou a versão final do trabalho, buscando manter consistência entre a descrição do sistema, os modelos estratégicos, as ameaças identificadas e os mecanismos de resposta.

## 6. Declaração de Uso de IA Generativa

Foi utilizada IA generativa como ferramenta de apoio durante a elaboração e revisão deste trabalho.

Seu uso esteve restrito principalmente a:
- apoio na revisão e organização da documentação;
- sugestões de melhoria na clareza e coerência do texto;
- apoio na identificação de inconsistências durante a revisão do modelo apresentado;
- correção gramatical e de estilo do README.md.

As decisões de projeto, a definição dos modelos, a análise dos resultados e a versão final do trabalho foram realizadas e validadas pelos integrantes do grupo.

## 7. Referências

Ver [`Fontes/referencias.md`](Fontes/referencias.md).

## 8. Nota sobre os diagramas

Os arquivos-fonte editáveis (`.mmd`) estão em `diagramas/`. Para gerar os `.png` exigidos na estrutura de entrega, foi usado:

- [Mermaid Live Editor](https://mermaid.live);

Os diagramas também estão embutidos como blocos `mermaid` diretamente neste README, renderizados automaticamente pelo GitHub.


---
