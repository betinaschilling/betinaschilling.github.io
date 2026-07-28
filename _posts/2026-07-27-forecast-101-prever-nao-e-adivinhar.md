---
layout: post
title: "Forecast 101: avaliação temporal, incerteza e decisão"
description: "Formulação, backtesting, baselines, métricas, previsão probabilística e decisão em séries temporais."
date: 2026-07-27 12:00:00 -0300
category: Método
read_time: 32 min
series: Forecast 101
featured_order: 2
laboratory: /laboratorio/forecast-101/
---

Forecasting consiste em estimar valores futuros de uma variável a partir das
informações disponíveis em uma origem de previsão. A definição é simples, mas
impõe quatro condições que frequentemente desaparecem durante a modelagem: a
origem deve ser explícita, o horizonte deve corresponder ao uso operacional, o
conjunto de informação deve respeitar o que existia naquele instante e a
avaliação deve representar a consequência do erro.

Este artigo examina essas condições em um experimento reproduzível de previsão
de demanda diária. O exemplo usa dados sintéticos e um modelo deliberadamente
simples. O interesse não está em maximizar desempenho em uma competição, mas em
estabelecer um procedimento de avaliação que continue válido quando o modelo for
levado para uma decisão real.

## Visão geral do experimento

O laboratório compara três métodos em oito origens móveis de previsão:

- **naive:** repete o último valor observado;
- **seasonal naive:** repete recursivamente a última semana conhecida;
- **regressão de calendário:** combina tendência, dia da semana e ciclo anual.

Cada origem prevê 28 dias. Nenhum método pode consultar o período de teste. A
avaliação combina magnitude do erro, escala, direção, estabilidade, incerteza e
um custo assimétrico no qual faltar demanda custa três vezes mais do que
excedê-la.

Na série sintética, a regressão apresentou o menor WAPE médio: **4,05%**, contra
**4,93%** do seasonal naive e **6,70%** do naive. Mas ela também apresentou
subprevisão e custo assimétrico superior ao naive. Portanto, o modelo que mais
acertou em erro absoluto não foi o que melhor serviu à decisão escolhida.

O resultado não é paradoxal. Acurácia pontual e valor decisório são critérios
distintos. A expressão “melhor forecast” só é tecnicamente completa quando
declara a decisão, o custo e o horizonte aos quais se refere.

## 1. Formulação do problema

“Prever vendas” não é uma formulação analítica completa. Vendas podem significar
receita, unidades, pedidos ou demanda não censurada. Podem ser previstas para a
companhia, uma loja, uma categoria ou um SKU. Podem orientar escala, orçamento,
capacidade, sortimento ou abastecimento.

Cada escolha muda o problema estatístico.

Considere duas equipes. A primeira precisa dimensionar pessoas para amanhã. A
segunda planeja capacidade para as próximas quatro semanas. Mesmo que observem a
mesma série diária, não estão pedindo o mesmo forecast. A primeira pode depender
fortemente do erro de um passo à frente. A segunda precisa compreender como o
erro se acumula ao longo de 28 dias.

Uma especificação mínima deve declarar:

| Elemento | Pergunta |
|---|---|
| Alvo | O que exatamente será previsto e em qual unidade? |
| Frequência | A cada hora, dia, semana ou mês? |
| Origem | Em que instante a informação é congelada? |
| Horizonte | Quantos passos futuros devem ser estimados? |
| Cadência | Com que frequência o forecast será atualizado? |
| Unidade | Companhia, loja, produto, região ou combinação? |
| Decisão | Qual ação será alterada pelo resultado? |
| Custo | O que acontece quando erramos para cima ou para baixo? |

No laboratório, a pergunta é se, em uma série diária sintética, uma regressão
de calendário produz previsões de 28 dias mais úteis do que baselines simples
quando avaliada em oito origens temporais.

A palavra “úteis” exige mais do que acurácia. Por isso, mediremos também viés,
estabilidade, calibração e custo.

## 2. Origem, horizonte e conjunto de informação

Toda previsão é condicional:

\[
\hat y_{T+h|T} = E(y_{T+h} \mid \mathcal{I}_T)
\]

Aqui, \(T\) é a origem da previsão, \(h\) é o passo à frente e
\(\mathcal{I}_T\) representa tudo que estava disponível em \(T\).

O detalhe mais importante não é a notação. É o limite: informações que surgem
depois de \(T\) não pertencem a \(\mathcal{I}_T\).

Calendário costuma ser conhecido antecipadamente. O dia da semana de daqui a
20 dias já existe. Uma promoção pode ser conhecida, se estiver aprovada e
registrada na origem. A temperatura observada daqui a 20 dias não está
disponível; no máximo, existe uma previsão meteorológica produzida em \(T\).

Isso cria três classes úteis de atributos:

1. **conhecidos antecipadamente:** calendário, feriados e eventos planejados;
2. **observados apenas no passado:** demanda, preço realizado e clima medido;
3. **futuros estimados:** clima previsto, cenário macroeconômico ou plano ainda
   sujeito a revisão.

Misturar essas classes produz um modelo que funciona no laboratório e não pode
ser executado na operação.

Se a avaliação usa o clima futuro observado e o modelo operacional receberá uma
previsão meteorológica, o experimento mediu o valor da observação perfeita, não
o valor da informação realmente disponível em produção.

## 3. Série sintética e processo gerador

Uma série temporal não é uma tabela que por acaso possui datas. A ordem carrega
dependência. Tendência, sazonalidade, ciclos, eventos, intervenções e mudanças
de regime fazem com que observações próximas possam compartilhar estrutura.

Por isso, uma divisão aleatória de treino e teste costuma ser inadequada. Ao
embaralhar as linhas, permitimos que o modelo aprenda com janeiro de 2026 e seja
avaliado em janeiro de 2025. Mesmo sem uma coluna explicitamente futura, o
processamento pode incorporar padrões que ainda não existiam na origem
simulada.

O laboratório cria 730 dias de demanda com:

- tendência gradual;
- efeito por dia da semana;
- ciclo anual;
- ruído;
- quatro eventos pontuais;
- uma mudança moderada de nível.

Os eventos e a mudança não entram na regressão. Isso é intencional. Um gerador
perfeitamente alinhado ao candidato faria o experimento parecer limpo demais. A
vida operacional contém mecanismos omitidos, registros incompletos e períodos
que não se parecem com a média.

Dados sintéticos têm duas vantagens: não expõem informações privadas e tornam o
processo reproduzível. Mas têm uma limitação decisiva: resultados sintéticos
ensinam o método, não estimam desempenho em uma empresa real.

## 4. Leakage: quando o futuro entra pela porta dos fundos

Leakage temporal ocorre quando qualquer etapa usa informação que não existia na
origem da previsão. Pode aparecer no modelo, mas também na preparação:

- média móvel calculada antes de deslocar o alvo;
- normalização ajustada em toda a série;
- imputação aprendida com o período de teste;
- seleção de atributos feita antes do backtesting;
- variável revisada retroativamente;
- baseline construído com valores futuros;
- hiperparâmetros escolhidos olhando repetidamente o teste final.

A primeira versão deste laboratório continha justamente um desses problemas. O
seasonal naive funcionava corretamente nos primeiros sete passos, mas, do
oitavo ao vigésimo oitavo, acessava valores pertencentes ao teste.

Em vez de esconder a falha, ela merece virar conteúdo. O erro mostra por que
baselines também precisam de revisão. Um método simples não é automaticamente
um método honesto.

A correção usa apenas a última semana disponível na origem:

\[
\hat y_{T+h|T} = y_{T-7 + ((h-1) \bmod 7)}
\]

A semana conhecida é repetida recursivamente durante todo o horizonte. Nenhum
valor realizado depois de \(T\) entra na previsão.

Uma auditoria temporal deve reconstruir, para cada linha prevista, a data de
origem e a disponibilidade de todas as entradas usadas pelo modelo.

## 5. Baselines são hipóteses mínimas

Um baseline não é um adversário decorativo. Ele representa uma estratégia
plausível que a organização poderia usar sem o candidato.

O **naive** repete o último valor:

\[
\hat y_{T+h|T} = y_T
\]

Ele pergunta se o processo muda pouco o suficiente para que o presente seja uma
boa aproximação do futuro.

O **seasonal naive** repete o valor da mesma posição sazonal. Em dados diários
com período semanal, repete a última semana. Ele pergunta se a sazonalidade
recente já contém quase tudo de que precisamos.

A regressão de calendário adiciona estrutura:

\[
\hat y_t =
\beta_0 + \beta_1 t
+ \sum_d \gamma_d I(\text{weekday}_t=d)
+ \alpha \sin(2\pi t/365{,}25)
+ \delta \cos(2\pi t/365{,}25)
\]

Ela combina uma tendência linear, efeitos de dia da semana e uma base harmônica
anual. Não utiliza lags do alvo, promoções ou eventos.

Esse candidato é propositalmente interpretável. Modelos mais sofisticados —
ETS, ARIMA, boosting, redes neurais ou modelos fundacionais — só fazem sentido
depois que o desenho de avaliação consegue distingui-los de uma repetição
honesta do passado.

Competições como a M5 mostram a complexidade do varejo real: milhares de séries
hierárquicas, demanda intermitente, variáveis exógenas e avaliação conjunta de
acurácia e incerteza. O salto de uma série didática para esse contexto não é
apenas trocar o algoritmo. É mudar a escala do problema.

## 6. Backtesting: reconstruir decisões que já aconteceram

Um único holdout responde: “como o método funcionou neste período?”. Rolling
origin responde algo mais forte: “como teria funcionado se fosse executado em
diversas datas históricas?”.

O procedimento foi sistematizado na literatura de avaliação fora da amostra e
continua sendo uma referência para forecast. Em cada fold:

1. congelamos uma origem \(T\);
2. treinamos apenas no passado;
3. produzimos 28 previsões;
4. comparamos com o que ocorreu;
5. avançamos a origem;
6. reajustamos o método e repetimos.

O laboratório usa oito folds e janela expansiva. Isso produz 224 erros por
modelo — oito previsões para cada posição do horizonte.

| Elemento | Escolha |
|---|---|
| Frequência | diária |
| Horizonte | 28 dias |
| Origens | 8 |
| Passo entre origens | 28 dias |
| Janela | expansiva |
| Refit | a cada origem |
| Sazonalidade do baseline | 7 dias |
| Calibração do intervalo | últimos 56 dias anteriores ao teste |

Uma janela expansiva pressupõe que a história antiga ainda ajuda. Em ambientes
com mudança rápida de regime, uma janela deslizante pode ser melhor. Um *gap*
também pode ser necessário quando existe atraso de publicação, revisão do alvo
ou contaminação perto da fronteira.

Não há quantidade universal de folds. Poucas origens tornam a comparação
dependente de eventos particulares. Muitas origens com treino curto podem
impedir que o modelo aprenda sazonalidades longas. O desenho é um compromisso
entre representatividade do teste e quantidade de história disponível.

![Backtest do último fold: observado, baseline sazonal, regressão e intervalo calibrado.]({{ '/assets/images/forecast-101-backtest.svg' | relative_url }})

*A figura mostra apenas o último fold. As conclusões usam os oito.*

## 7. Métricas não são sinônimos

Um único número raramente descreve toda a qualidade de uma previsão.

### MAE: erro na unidade do problema

\[
MAE = \frac{1}{n}\sum_{i=1}^{n}|y_i-\hat y_i|
\]

O MAE diz quantas unidades erramos, em média. É interpretável, mas depende da
escala. Um MAE de 10 pode ser excelente para uma série de mil unidades e ruim
para outra de vinte.

### RMSE: peso adicional para erros grandes

\[
RMSE = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat y_i)^2}
\]

O RMSE penaliza erros grandes com maior intensidade. Isso pode ser desejável se
grandes falhas forem desproporcionalmente perigosas, mas também o torna sensível
a eventos extremos.

### WAPE: erro relativo ao volume

\[
WAPE = \frac{\sum |y_i-\hat y_i|}{\sum |y_i|}
\]

O WAPE é comum em varejo porque agrega erro absoluto em relação ao volume. Ele
evita algumas patologias do MAPE diante de zeros, mas continua dependente do
volume do conjunto avaliado. Em séries de baixo volume ou comparações entre
grupos muito diferentes, precisa ser lido com cuidado.

### Viés: direção do erro

Definimos erro como previsão menos observado:

\[
Bias = \frac{\sum(\hat y_i-y_i)}{\sum y_i}
\]

Viés positivo indica superprevisão; negativo, subprevisão. Um viés próximo de
zero não implica acurácia: erros positivos e negativos podem se cancelar.

### MASE: erro escalado por uma referência sazonal

O MASE divide o MAE pela média das diferenças sazonais do treino. Foi proposto
como uma medida escalável e comparável entre séries:

\[
MASE =
\frac{MAE}
{\frac{1}{T-m}\sum_{t=m+1}^{T}|y_t-y_{t-m}|}
\]

Valores abaixo de 1 indicam que o método superou, naquela escala, a referência
sazonal usada no denominador. Isso não elimina a necessidade de avaliar o
baseline diretamente, mas ajuda quando há muitas séries.

## 8. Resultado pontual: o candidato ganhou?

As médias dos oito folds foram:

| Modelo | MAE | RMSE | WAPE | Faixa de WAPE | Viés | MASE |
|---|---:|---:|---:|---:|---:|---:|
| Naive | 20,33 | 24,85 | 6,70% | 4,22–10,27% | 3,98% | 1,36 |
| Seasonal naive | 15,12 | 18,71 | 4,93% | 3,72–8,12% | -1,20% | 1,02 |
| Regressão de calendário | 12,34 | 15,33 | 4,05% | 2,94–5,69% | -2,53% | 0,83 |

Pelo WAPE médio, a regressão reduz o erro em aproximadamente **17,8%** contra o
seasonal naive e **39,6%** contra o naive.

Mas a faixa entre folds importa. O WAPE do candidato varia de 2,94% a 5,69%.
Isso significa que a média de 4,05% não deve ser lida como uma propriedade fixa
do modelo. O desempenho depende da origem, dos eventos e do regime encontrado.

O MASE de 0,83 é coerente com ganho sobre a escala sazonal. O viés de -2,53%,
porém, mostra subprevisão persistente. A regressão captura a estrutura média,
mas reage lentamente à mudança de nível que não foi explicitamente modelada.

Os resultados sustentam uma conclusão restrita: neste experimento e nestas oito
origens, a regressão apresentou menor erro absoluto que os dois baselines. Eles
não sustentam a afirmação de que regressão de calendário seja o melhor método
para demanda diária em geral.

## 9. O horizonte também é uma dimensão do erro

Médias agregadas podem esconder degradação conforme nos afastamos da origem. O
laboratório separa os 28 passos em quatro blocos:

| Horizonte | MAE do candidato | Erro médio |
|---|---:|---:|
| dias 1–7 | 11,77 | -7,32 |
| dias 8–14 | 12,49 | -8,07 |
| dias 15–21 | 12,97 | -8,13 |
| dias 22–28 | 12,15 | -7,37 |

Não há explosão monotônica do MAE, porque o candidato utiliza apenas calendário
conhecido e não propaga lags previstos. A subprevisão, contudo, aparece em todos
os blocos. Isso sugere uma falha de nível, não um problema restrito aos passos
distantes.

Em modelos autorregressivos, o comportamento pode ser diferente: erros de
previsões anteriores alimentam passos posteriores. Em modelos com covariáveis
futuras estimadas, a incerteza dessas covariáveis também cresce com o horizonte.

Avaliar apenas o total de 28 dias seria adequado se a decisão dependesse somente
do volume agregado. Para escala diária, calendário de capacidade ou reposição,
o caminho dentro do horizonte importa.

## 10. Acurácia não define a melhor decisão

Até aqui, cada unidade de erro para cima ou para baixo recebeu o mesmo peso
absoluto. Negócios raramente são tão simétricos.

Suponha:

- custo de falta = 3;
- custo de excesso = 1.

Definimos um índice didático:

\[
L =
\frac{
3\sum\max(y-\hat y,0)
+ 1\sum\max(\hat y-y,0)
}{
\sum y
}\times 100
\]

Os resultados são:

| Modelo | Índice de custo |
|---|---:|
| Naive | 9,42 |
| Regressão de calendário | 10,63 |
| Seasonal naive | 11,06 |

Agora o naive, apesar do maior WAPE, produz o menor custo. Seu viés positivo
protege contra a penalidade maior da falta. A regressão otimizada para o centro
da distribuição subestima o novo nível e paga caro por isso.

Não significa que devemos escolher o naive. Significa que a previsão pontual e
a regra de decisão estão desalinhadas. Sob perda assimétrica, a média
condicional pode não ser o ponto ótimo. Dependendo da função de perda, um
quantil superior pode ser a decisão correta.

Essa distinção separa **previsão** de **otimização**:

- o modelo estima uma distribuição ou conjunto de cenários;
- a decisão escolhe uma ação com base em custos e restrições.

Modificar silenciosamente a previsão para “colocar uma gordura” mistura os dois
processos. Melhor é declarar a distribuição e aplicar uma política explícita.

## 11. Previsão pontual não é suficiente

Uma previsão de 300 unidades parece precisa porque tem um único número. Mas o
futuro pode ser 270 ou 350 e ainda ser compatível com a informação disponível.

Previsões probabilísticas procuram representar essa dispersão. Podem aparecer
como:

- intervalos;
- quantis, como P10, P50 e P90;
- amostras de cenários;
- distribuição preditiva completa.

Neste laboratório, o intervalo de 80% usa um bloco de calibração temporal de 56
dias. O modelo é ajustado antes desse bloco, seus erros absolutos são medidos
fora do ajuste e um quantil desses erros define o raio ao redor da previsão
pontual.

O procedimento se aproxima da lógica de *split conformal*, mas não oferece uma
garantia universal para séries temporais. Dependência serial e mudança de regime
violam a permutabilidade usual. Métodos como EnbPI foram desenvolvidos
especificamente para intervalos conformais dinâmicos.

Dois conceitos precisam ser avaliados juntos:

- **calibração:** a frequência observada de cobertura corresponde ao nível
  anunciado?
- **sharpness:** os intervalos são estreitos o suficiente para serem úteis?

No experimento:

| Diagnóstico | Resultado |
|---|---:|
| Cobertura nominal | 80% |
| Cobertura observada | 82,14% |
| Largura média | 40,64 unidades |
| Interval score | 57,76 |

A cobertura está próxima do nível nominal. Isso não basta para aprovar o
intervalo. Uma faixa extremamente larga cobriria quase tudo e ainda poderia ser
inútil. O interval score combina largura com penalidade quando o observado fica
fora da faixa.

Comparar intervalos apenas por cobertura é insuficiente. Calibração sem
*sharpness* pode premiar incerteza inflada.

## 12. Resíduos: o que o modelo ainda não aprendeu

Um erro não é apenas falha; é informação sobre a especificação.

Se os resíduos preservam autocorrelação, existe estrutura temporal que o modelo
não capturou. Se o viés muda por dia da semana, o calendário está incompleto. Se
os erros aumentam depois de uma quebra, a janela ou a dinâmica de nível precisa
ser revista.

Nos 224 erros fora da amostra da regressão:

| Diagnóstico | Resultado |
|---|---:|
| Autocorrelação lag 1 | 0,115 |
| Autocorrelação lag 7 | 0,041 |

Os valores são baixos, embora não constituam um teste formal de ruído branco. A
subprevisão persistente é mais relevante: a mudança de nível gerada na série
não foi representada pelo candidato.

Em um estudo real, ampliaríamos a análise com:

- ACF dos resíduos por fold;
- viés por horizonte, dia da semana e evento;
- estabilidade dos coeficientes;
- análise de quebras estruturais;
- erro por volume, produto, loja e regime;
- cobertura e largura por horizonte;
- testes de sensibilidade à janela de treino.

Um modelo pode ter resíduos pouco autocorrelacionados e ainda ser inadequado
para a decisão. Diagnóstico estatístico é necessário, não suficiente.

## 13. O que mudaria em dados reais

O laboratório contém uma série. Varejo real costuma conter centenas ou milhares
de séries relacionadas.

Nesse contexto aparecem novos problemas:

### Hierarquia

Loja, região e companhia precisam ser coerentes. Categoria, produto e total
também. Prever cada série isoladamente pode fazer com que as partes não somem o
todo. Métodos de reconciliação e hierarquias temporais tratam explicitamente
essa coerência.

### Demanda intermitente

Produtos de baixo giro têm muitos zeros. WAPE, MAPE e modelos gaussianos podem
se comportar mal. A diferença entre zero de demanda e zero causado por ruptura
precisa ser compreendida antes da modelagem.

### Censura por disponibilidade

Venda observada não é necessariamente demanda. Quando o produto não estava
disponível, o alvo pode estar censurado. Um modelo treinado sem essa distinção
aprende que indisponibilidade significa baixa preferência.

### Eventos e covariáveis

Preço, promoção, feriado, coleção e clima podem ajudar — se forem conhecidos ou
previstos na origem. Seu valor deve ser medido por ablação temporal: comparar o
mesmo desenho com e sem a informação adicional.

### Mudança de regime

Novas lojas, alterações de canal, mudanças de política comercial e crises
quebram a continuidade histórica. Janela, ponderação e frequência de refit
precisam refletir a velocidade da mudança.

### Forecast hierárquico e global

Modelos globais aprendem em várias séries e podem compartilhar informação.
Modelos locais preservam especificidades. A escolha depende de volume, número
de séries, heterogeneidade e infraestrutura.

O resultado de uma competição ou benchmark público não transfere
automaticamente para esse sistema. O desenho operacional — dados, latência,
reconciliação, explicação e ação — pode dominar a diferença entre algoritmos.

## 14. Comparar modelos não é apenas ordenar uma tabela

Quando dois modelos produzem WAPE de 4,05% e 4,18%, é tentador declarar um
vencedor. Mas a diferença pode depender de poucas datas, de uma origem
favorável ou da métrica escolhida.

Previsões comparadas sobre os mesmos períodos geram perdas pareadas. Isso é
útil: podemos observar, em cada data, quanto um método melhorou ou piorou em
relação ao outro. Também cria dependência. Previsões de horizontes
sobrepostos compartilham observações e erros, portanto uma aplicação ingênua de
testes independentes subestima incerteza.

O teste de Diebold–Mariano foi proposto para avaliar a hipótese de igualdade de
acurácia preditiva a partir do diferencial de perda. Ele admite funções de
perda não quadráticas e considera dependência serial. Ainda assim, sua aplicação
não deve virar um ritual automático:

- a função de perda precisa ser definida antes da comparação;
- horizontes múltiplos exigem correção apropriada da variância;
- amostras pequenas apresentam aproximações frágeis;
- testar muitos modelos aumenta o risco de encontrar uma vitória por acaso;
- significância estatística não implica relevância operacional.

Neste Forecast 101 não aplicamos o teste. Oito origens e 224 erros correlacionados
servem para diagnóstico didático, não para uma alegação forte de superioridade.
Reportamos magnitude, faixa entre folds e comportamento por horizonte.

Em um processo de seleção maior, eu separaria três camadas:

1. **desenvolvimento:** escolher features e hiperparâmetros em backtesting
   temporal;
2. **comparação:** avaliar candidatos finalistas em origens não usadas na
   seleção;
3. **teste final:** congelar o processo e medir uma última janela intocada.

Depois disso, a implantação inicia outro experimento: desempenho prospectivo.
Um modelo aprovado historicamente ainda precisa demonstrar que dados, latência
e comportamento futuro permanecem compatíveis com o desenho.

Diferenças pequenas e instáveis devem ser tratadas como empate operacional até
que exista evidência para justificar a complexidade adicional.

## 15. Uma taxonomia útil de modelos

Forecast não é uma corrida linear entre “modelo simples” e “IA”. Famílias
diferentes representam hipóteses diferentes sobre a estrutura.

### Métodos de nível, tendência e sazonalidade

ETS e modelos estruturais descrevem componentes que evoluem no tempo. São
fortes quando nível, tendência e sazonalidade carregam grande parte do sinal.
Seu estado atualizado oferece adaptação que a regressão fixa deste laboratório
não possui.

### ARIMA, regressão dinâmica e espaço de estados

ARIMA representa dependência serial por termos autorregressivos, diferenças e
médias móveis. Com covariáveis, SARIMAX ou regressão dinâmica ligam estrutura
temporal e informação externa. A interpretação exige diagnóstico dos resíduos e
disponibilidade futura das covariáveis.

### Machine learning com features temporais

CatBoost, LightGBM e XGBoost podem combinar lags, janelas, calendário, preço e
eventos. São especialmente úteis como modelos globais em muitas séries. Não
entendem tempo automaticamente: lags, validação, disponibilidade e recursão
continuam sendo responsabilidade do desenho.

### Redes neurais e modelos globais

N-BEATS, N-HiTS, redes recorrentes e Transformers aprendem padrões
compartilhados. Podem ganhar escala e transferir sinal entre séries, mas elevam
o custo de tuning, monitoramento e interpretação. O baseline continua
obrigatório.

### Modelos fundacionais

Chronos, TimesFM e outros modelos pré-treinados introduzem previsão zero-shot ou
fine-tuning. Eles mudam o custo inicial de construção, mas não removem a
necessidade de backtesting local. Um modelo fundacional pode conhecer muitas
formas de série e ainda desconhecer o calendário comercial, a censura e a
função de custo da organização.

### Combinações

Combinar previsões pode reduzir risco de especificação. Uma média simples entre
métodos diversos frequentemente é competitiva. Pesos aprendidos precisam ser
estimados dentro da validação, ou o ensemble transforma o teste em treino.

A escolha não deveria começar por “qual tecnologia queremos usar?”, mas por:

- quantas séries existem;
- quanta história está disponível;
- quais sazonalidades e regimes aparecem;
- quais atributos futuros são conhecidos;
- qual nível de coerência é exigido;
- qual latência e custo operacional são aceitáveis;
- qual forma de incerteza a decisão precisa.

## 16. Linhas de aprofundamento depois do 101

Este artigo fecha um ciclo básico, mas abre uma trilha.

### Forecast 201 — validação temporal

Comparar janela expansiva e deslizante, gap, folds sobrepostos, refit,
validação aninhada e teste final. A pergunta central será como o desenho de
avaliação altera a conclusão.

### Forecast probabilístico

Trabalhar quantis, pinball loss, CRPS, interval score, calibração por horizonte
e métodos conformais adaptativos. O foco deixa de ser “acertar um ponto” e passa
a ser representar uma distribuição útil.

### Forecast e decisão

Derivar a ação ótima sob custos assimétricos, restrições de capacidade e níveis
de serviço. Quantis, simulação e otimização se encontram aqui.

### Forecast hierárquico

Prever companhia, região, loja, categoria e produto mantendo coerência.
Bottom-up, top-down, middle-out e MinT serão comparados não apenas por acurácia,
mas por estabilidade e uso.

### Forecast com covariáveis

Mensurar o ganho de calendário comercial, promoção, preço, clima e variáveis
macroeconômicas. Cada feature futura precisará de uma política explícita de
disponibilidade ou cenário.

### Forecast em escala

Discutir modelos locais e globais, demanda intermitente, séries novas,
clusterização, cold start, reconciliação e monitoramento de milhares de
entidades.

Essas linhas não precisam caber em um único artigo. Transformá-las em uma série
preserva profundidade sem converter o texto inicial em manual enciclopédico.

## 17. Da métrica ao produto de dados

Um forecast não termina quando o modelo retorna um vetor.

Para virar produto, precisa responder:

1. quando é executado;
2. quais dados precisam ter chegado;
3. o que acontece quando uma fonte falha;
4. como versões e origens são armazenadas;
5. como previsões são reconciliadas;
6. quem consome os resultados;
7. qual ação muda;
8. como erros são observados depois;
9. quando o modelo é recalibrado ou substituído.

O monitoramento deve distinguir:

- qualidade do dado;
- drift de atributos;
- mudança do alvo;
- acurácia por horizonte;
- viés;
- calibração probabilística;
- custo da decisão;
- adoção e overrides humanos.

Forecast Value Added amplia a pergunta: cada etapa do processo — modelo,
ajuste humano, regra operacional — melhora ou piora a previsão? Uma intervenção
manual pode incorporar contexto ausente, mas também introduzir viés político,
ancoragem ou dupla contagem.

O objetivo não é automatizar tudo. É produzir rastreabilidade suficiente para
saber onde o valor foi acrescentado.

## 18. Limitações deste experimento

Este estudo é didático e controlado.

- Os dados são sintéticos.
- O gerador contém estruturas conhecidas.
- Há somente uma série.
- O custo 3:1 é ilustrativo, não estimado.
- A regressão não passa por seleção de hiperparâmetros.
- O intervalo calibrado é pragmático e não uma garantia conformal geral.
- Oito origens ainda representam uma amostra limitada de regimes.
- Não há teste final intocado depois de seleção entre vários candidatos.
- Não estimamos significância da diferença de acurácia.
- Não há causalidade, intervenção ou avaliação econômica real.

Se diversos modelos fossem selecionados usando esses mesmos oito folds, seria
necessário reservar uma avaliação final ou adotar validação temporal aninhada.
Testes como Diebold–Mariano podem comparar perdas preditivas, mas exigem atenção
à dependência, ao horizonte e ao tamanho da amostra. Um p-valor não substitui a
magnitude nem o valor econômico da diferença.

## 19. Um checklist mínimo para forecast

Antes de aceitar um resultado:

### Problema

- alvo e unidade estão definidos?
- origem, horizonte e cadência correspondem à decisão?
- custos de excesso e falta foram discutidos?

### Dados

- datas ausentes e duplicidades foram auditadas?
- zeros têm significado conhecido?
- mudanças de definição foram registradas?
- cada atributo existia na origem simulada?

### Validação

- a ordem temporal foi preservada?
- o baseline está livre de leakage?
- existem origens suficientes?
- o desempenho é mostrado por horizonte e período crítico?

### Métricas

- magnitude e direção aparecem juntas?
- há escala comparável entre séries?
- custo ou utilidade da decisão foi considerado?
- intervalos são avaliados por cobertura e largura?

### Operação

- a previsão pode ser reproduzida?
- origem, versão e dados usados são armazenados?
- existe monitoramento de viés, calibração e custo?
- há uma política para mudança de regime?

## 20. Reproduza e questione

O [caderno técnico do Forecast 101]({{ '/laboratorio/forecast-101/' |
relative_url }}) contém o código, as métricas e o parecer de revisão.

```bash
cd laboratorios/forecast-101
python3 forecast_101.py
```

O programa usa apenas a biblioteca padrão do Python 3.10 ou superior. Ele
imprime as tabelas usadas neste artigo e atualiza a figura do último fold.

Experimente alterar:

- o custo de falta;
- o momento da mudança de nível;
- o número de folds;
- a janela de calibração;
- o horizonte;
- a intensidade da sazonalidade.

Observe que a pergunta “qual modelo ganhou?” muda quando a função de perda ou o
regime muda. Essa instabilidade não é um defeito do exercício. É parte do
problema que forecast tenta organizar.

## Conclusão

Prever não é eliminar a incerteza. Também não é escolher o algoritmo que produz
a menor média em uma tabela.

Um processo confiável:

1. começa pela decisão;
2. congela o conjunto de informação;
3. preserva a ordem temporal;
4. compara com baselines honestos;
5. avalia múltiplas origens;
6. separa magnitude, direção e custo;
7. representa incerteza;
8. diagnostica o que permaneceu nos erros;
9. declara limites;
10. retorna ao problema quando o regime muda.

Neste laboratório, a regressão foi mais acurada e menos alinhada ao custo
assimétrico. Esse resultado é mais interessante do que uma vitória simples.
Mostra que forecast e decisão são partes conectadas, mas não idênticas.

Prever não é adivinhar. É tornar explícito o que sabemos, o que não sabemos e o
que custa agir como se soubéssemos.

## Referências

- Tashman, L. J. (2000). [Out-of-sample tests of forecasting accuracy: an
  analysis and review](https://doi.org/10.1016/S0169-2070(00)00065-0).
  *International Journal of Forecasting*, 16(4), 437–450.
- Hyndman, R. J.; Koehler, A. B. (2006). [Another look at measures of forecast
  accuracy](https://doi.org/10.1016/j.ijforecast.2006.03.001).
  *International Journal of Forecasting*, 22(4), 679–688.
- Gneiting, T. (2011). [Making and evaluating point
  forecasts](https://doi.org/10.1198/jasa.2011.r10138). *Journal of the
  American Statistical Association*, 106(494), 746–762.
- Gneiting, T.; Raftery, A. E. (2007). [Strictly proper scoring rules,
  prediction, and estimation](https://doi.org/10.1198/016214506000001437).
  *Journal of the American Statistical Association*, 102(477), 359–378.
- Xu, C.; Xie, Y. (2021). [Conformal prediction interval for dynamic
  time-series](https://proceedings.mlr.press/v139/xu21h.html). *Proceedings of
  the 38th International Conference on Machine Learning*, 11559–11569.
- Diebold, F. X.; Mariano, R. S. (1995). [Comparing predictive
  accuracy](https://doi.org/10.1080/07350015.1995.10524599). *Journal of
  Business & Economic Statistics*, 13(3), 253–263.
- Makridakis, S.; Spiliotis, E.; Assimakopoulos, V. (2022). [M5 accuracy
  competition: results, findings, and
  conclusions](https://doi.org/10.1016/j.ijforecast.2021.11.013).
  *International Journal of Forecasting*, 38(4), 1346–1364.
- Athanasopoulos, G.; Hyndman, R. J.; Kourentzes, N.; Petropoulos, F. (2017).
  [Forecasting with temporal
  hierarchies](https://doi.org/10.1016/j.ejor.2017.02.046). *European Journal
  of Operational Research*, 262(1), 60–74.
- Hyndman, R. J.; Athanasopoulos, G. (2021). [Forecasting: Principles and
  Practice](https://otexts.com/fpp3/), 3ª ed. OTexts.
- Hewamalage, H.; Ackermann, K.; Bergmeir, C. (2023). [Forecast evaluation for
  data scientists: common pitfalls and best
  practices](https://doi.org/10.1007/s10462-022-10214-2). *Artificial
  Intelligence Review*, 56, 7883–7924.
