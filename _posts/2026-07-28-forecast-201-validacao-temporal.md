---
layout: post
title: "Forecast 201: como a validação temporal altera a conclusão"
description: Janelas expansivas e deslizantes, gaps, sobreposição, refit,
  validação aninhada e teste final em um experimento controlado.
date: 2026-07-28 15:00:00 +0000
category: Método
read_time: 27 min
series: Forecast 201
featured_order: 3
laboratory: /laboratorio/forecast-201/
---
Uma estimativa de desempenho não depende apenas do modelo e dos dados. Ela
depende também das datas escolhidas para treinamento e teste, da distância
entre esses períodos, da frequência com que o modelo é reajustado e do número
de vezes em que uma mesma observação participa da avaliação. Em séries
temporais, essas escolhas descrevem uma situação de uso. Alterá-las pode mudar
o erro estimado e o modelo que ocupa a primeira posição.

Este artigo investiga esse problema em um experimento controlado. A série, os
modelos, o horizonte e as métricas permanecem constantes, enquanto uma dimensão
do protocolo é modificada por vez. São comparadas janelas expansiva e
deslizantes, gaps de 0, 7 e 14 dias, folds com diferentes graus de sobreposição
e cadências distintas de *refit* da regressão. A seleção do tamanho da janela
desse modelo é então executada em uma validação temporal aninhada, antes da
consulta a um teste final de 168 dias mantido bloqueado durante o
desenvolvimento.

A pergunta central é:

> Mantidos os dados, os modelos, o horizonte e as métricas, em que medida o
> desenho de avaliação temporal altera a estimativa de desempenho e o ranking
> dos modelos?

No experimento, as diferenças foram suficientes para alterar o ranking. A
regressão de calendário registrou
WAPE de **8,89%** sob janela expansiva e de **4,63%** sob janela deslizante de
365 dias. O seasonal naive apresentou o menor valor no primeiro protocolo; a
regressão, no segundo. Quando o *refit* da regressão passou a ocorrer a cada
duas ou quatro origens, a média sazonal assumiu a primeira posição. No teste final
bloqueado, a regressão com janela selecionada pela validação aninhada apresentou
o menor WAPE observado, **5,23%**, contra **5,77%** do seasonal naive. A
conclusão descritiva sobre o modelo dependeu do protocolo porque cada
configuração representava uma condição operacional diferente.

## 1. O objeto estimado pela validação

Considere uma origem T_k, um horizonte H, um gap g e uma janela de
treinamento de tamanho W_k. O conjunto usado para ajustar o modelo no fold
k pode ser escrito como:

# 
\mathcal{D}^{(k)}_{\text{train}}

y_t:t\in[T_k-W_k,T_k-1]


O período de teste começa depois do gap:

# 
\mathcal{D}^{(k)}_{\text{test}}

y_t:t\in[T_k+g,T_k+g+H-1]


O risco estimado pelo backtest é uma agregação das perdas observadas nas
origens:

# 
\widehat{R}_{P}(f)

\frac{1}{K}
\sum_{k=1}^{K}
\frac{1}{H}
\sum_{h=0}^{H-1}
L\left(y_{T_k+g+h},\hat y_{T_k+g+h\mid T_k}\right)


O subscrito P explicita algo frequentemente omitido: o risco é condicionado
ao protocolo P. Esse protocolo inclui a regra de formação das janelas, o
gap, o espaçamento entre origens, a política de atualização, o processo de
seleção e a função de perda. Portanto, dois valores de WAPE obtidos sobre a
mesma série podem estimar desempenhos sob situações de uso diferentes, como
mostra a literatura sobre avaliação fora da amostra e estimação de desempenho
temporal ([Tashman, 2000](https://doi.org/10.1016/S0169-2070(00)00065-0);
[Cerqueira, Torgo e Mozetič, 2020](https://doi.org/10.1007/s10994-020-05910-7)).

Uma janela expansiva responde como o modelo se comportaria se todo o histórico
fosse preservado. Uma janela deslizante representa uma política que descarta
dados antigos. Um gap de 14 dias avalia uma previsão feita com duas semanas de
antecedência. Um protocolo com *refit* a cada quatro origens não estima o mesmo
sistema que outro reajustado em toda origem. A comparação só é operacionalmente
útil quando a política simulada é compatível com a política que será executada.

Essa formulação também esclarece o papel do teste final. O backtest de
desenvolvimento é usado para comparar especificações e escolher o protocolo. No
experimento, os três candidatos e suas regras são congelados antes do teste
final, que fornece uma comparação externa entre eles. Quando o mesmo período é
usado para selecionar configurações e estimar seu desempenho, a estimativa tende
a incorporar o otimismo da busca
([Varma e Simon, 2006](https://doi.org/10.1186/1471-2105-7-91)).

## 2. Série, modelos e controle experimental

O laboratório utiliza 1.460 observações diárias sintéticas, geradas com semente
201. O processo contém tendência, sazonalidade semanal, ciclo anual, eventos
pontuais e duas mudanças de regime. Os eventos e os regimes não são fornecidos
explicitamente aos modelos. Essa omissão produz um ambiente no qual a relevância
do histórico varia ao longo do tempo.

Os primeiros 1.292 dias formam o conjunto de desenvolvimento. Os 168 dias
restantes, equivalentes a seis horizontes não sobrepostos de 28 dias, compõem o
teste final. Nenhuma escolha de janela, gap, passo ou modelo utiliza esse bloco.

Três previsores são comparados:

1. **seasonal naive**, que repete recursivamente a última semana disponível;
2. **média sazonal**, que estima uma média por dia da semana dentro da janela;
3. **regressão de calendário**, com tendência linear, indicadores de dia da

  semana e termos harmônicos anuais.

A simplicidade é intencional. O objetivo não é demonstrar superioridade de uma
arquitetura, mas identificar o efeito isolado do protocolo. Modelos complexos
adicionariam hiperparâmetros, estocasticidade e custo de ajuste que dificultariam
a atribuição das diferenças.

O horizonte permanece fixado em 28 dias. O erro é definido como previsão menos
observado. O WAPE de cada fold é:

# 
\operatorname{WAPE}_k

100
\frac{\sum_{h=0}^{H-1}|y_{T_k+g+h}-\hat y_{T_k+g+h\mid T_k}|}
{\sum_{h=0}^{H-1}|y_{T_k+g+h}|}


Também são registrados MAE e viés. O ranking principal usa a média dos WAPEs
calculados separadamente em cada fold, não um WAPE global sobre todas as
observações. Essa convenção atribui o mesmo peso às origens e não deve ser
interpretada como se cada fold fornecesse evidência independente, sobretudo nos
protocolos com sobreposição.

## 3. Janela expansiva e memória do processo

Na janela expansiva, o início do treinamento permanece fixo e o fim avança com
a origem:

# 
\mathcal{D}^{(k)}_{\text{train}}

y_0,\ldots,y_{T_k-1}


O procedimento aumenta a amostra a cada fold. Se os parâmetros do processo
forem aproximadamente estáveis, essa acumulação tende a reduzir a variância da
estimação e permite representar ciclos longos. Se o processo muda, entretanto,
observações antigas podem introduzir viés ao descrever relações que deixaram de
vigorar.

Na janela deslizante, apenas as W observações imediatamente anteriores à
origem são preservadas:

# 
\mathcal{D}^{(k)}_{\text{train}}

y_{T_k-W},\ldots,y_{T_k-1}


O tamanho W estabelece um compromisso entre memória e adaptação. Uma janela
longa oferece mais observações e maior cobertura sazonal, mas reage lentamente.
Uma janela curta reduz a influência de regimes anteriores, ao custo de aumentar
a variância e possivelmente eliminar ciclos necessários à identificação do
modelo.

Os resultados mostram esse compromisso:


| Protocolo | Seasonal naive | Média sazonal | Regressão |
| -------------------- | -------------- | ------------- | --------- |
| Expansiva | **5,34%** | 8,49% | 8,89% |
| Deslizante, 365 dias | 5,34% | 5,30% | **4,63%** |
| Deslizante, 180 dias | **5,34%** | 6,56% | 5,36% |


A regressão de calendário apresentou o maior WAPE entre os três métodos na
janela expansiva.
A janela de 365 dias reduziu seu WAPE em 4,26 pontos percentuais e alterou a
primeira posição. Como o processo gerador contém mudanças de nível e inclinação, a
regressão expansiva é estimada sobre observações produzidas antes e depois das
mudanças simuladas. A janela de 365 dias reduz a presença dos regimes antigos;
o experimento não isola esse mecanismo como causa do ganho.

Reduzir a janela para 180 dias não produziu ganho adicional. A regressão passou
a estimar os termos harmônicos anuais com cobertura parcial do ciclo e registrou
WAPE de 5,36%, próximo aos 5,34% do seasonal naive. O experimento não sustenta a
regra “dados recentes são melhores”. Ele mostra que a quantidade adequada de
memória depende simultaneamente da mudança de regime e da estrutura que o
modelo precisa identificar.

O seasonal naive apresenta exatamente o mesmo WAPE nos três protocolos porque
usa somente a última semana. Alterar o início da janela não muda sua informação.
Essa invariância funciona como controle: as diferenças observadas nos outros
modelos decorrem da forma como eles utilizam o histórico, não de uma mudança nas
datas de teste.

## 4. Gap: antecedência, latência e embargo

O gap desloca em g dias o início do período avaliado.
No laboratório, são testados g=0, g=7 e g=14, mantendo a janela de
365 dias e origens não sobrepostas.


| Gap | Seasonal naive | Média sazonal | Regressão |
| ------- | -------------- | ------------- | --------- |
| 0 dias | 5,34% | 5,30% | **4,63%** |
| 7 dias | 5,65% | 5,36% | **4,91%** |
| 14 dias | 5,86% | 5,43% | **5,31%** |


O aumento do gap tornou a tarefa progressivamente mais difícil para os três
métodos. Na regressão, o WAPE passou de 4,63% para 5,31%. O modelo permaneceu
com o menor valor, mas sua vantagem sobre a média sazonal caiu de 0,67 para
0,12 ponto percentual. Sem uma margem de equivalência ou análise de incerteza,
essa diferença não sustenta uma conclusão operacional categórica.

Neste artigo, gap e embargo designam mecanismos diferentes. Um gap operacional
representa o tempo entre o
fechamento da informação e o início do uso da previsão: atraso de ingestão,
processamento, negociação, fabricação ou preparação da decisão. Um embargo
estatístico procura reduzir contaminação quando exemplos próximos compartilham
informações ou rótulos. Os mecanismos podem produzir a mesma geometria na
partição, mas justificam tamanhos diferentes.

Se uma área precisa aprovar um plano duas semanas antes da execução, avaliar
com g=0 responde à pergunta errada, mesmo na ausência de leakage. O modelo
estaria recebendo quatorze dias de informação que a operação não terá. Nesse
caso, o gap não é uma precaução opcional; ele faz parte do horizonte efetivo da
decisão.

## 5. Folds sobrepostos e dependência

Com horizonte de 28 dias e passo de 28, os períodos de teste não se sobrepõem.
Com passo de 14, cada fold compartilha metade do período com o fold seguinte.
Com passo de 7, a sobreposição chega a 75%.

O aumento da frequência de origens oferece duas vantagens. Ele avalia o modelo
em mais estados do processo e aproxima uma operação que publica previsões
semanalmente. No entanto, as novas medições não equivalem ao mesmo número de
replicações independentes. Uma data difícil pode afetar quatro folds quando o
passo é de sete dias, e os erros de horizontes diferentes passam a compartilhar
o mesmo valor observado.

No experimento:


| Passo entre origens | Sobreposição | Seasonal naive | Média sazonal | Regressão |
| ------------------- | ------------ | -------------- | ------------- | --------- |
| 28 dias | 0% | 5,34% | 5,30% | **4,63%** |
| 14 dias | 50% | 6,05% | 6,93% | **5,40%** |
| 7 dias | 75% | 5,51% | 7,40% | **4,89%** |


O menor WAPE permaneceu com a regressão, mas a magnitude não foi monotônica.
Alterar o passo também altera as origens amostradas. Os resultados mostram que
as amostras de folds tiveram dificuldades distintas, mas o experimento não
identifica quais características de cada origem produziram essa diferença.

Não se deve concluir que a sobreposição causou aumento ou redução do erro. Ela
modificou a amostra de situações avaliadas e a dependência entre as perdas. A
inferência sobre diferenças entre modelos precisa considerar essa dependência,
por exemplo por reamostragem em blocos, comparação agregada por origem ou
modelos para a série de diferenciais de perda. Aplicar diretamente um erro
padrão baseado em observações independentes pode subestimar a incerteza. A
validade de procedimentos de validação cruzada em séries temporais depende das
propriedades do processo e dos erros
([Bergmeir, Hyndman e Koo, 2018](https://doi.org/10.1016/j.csda.2017.11.003)).

Uma decisão prática precede a técnica estatística: o backtest deve simular a
cadência real de emissão. Se previsões são publicadas semanalmente para 28 dias,
folds sobrepostos são parte do sistema. A resposta não é removê-los apenas para
facilitar a inferência, mas representar sua dependência corretamente.

![WAPE dos três modelos sob nove protocolos de validação temporal.](<{{ '/assets/images/forecast-201-validation.svg' | relative_url }}>)

O WAPE e o ranking variam com janela, gap, sobreposição e cadência de refit. A comparação controla série, modelos, horizonte e métrica.

## 6. Refit: desempenho do modelo ou da política de atualização?

Um modelo pode ser executado várias vezes sem ser reajustado. A distinção é
relevante para sistemas nos quais o treino é caro, depende de aprovação ou
ocorre em cadência diferente da geração de previsões.

No protocolo de referência, a regressão é reajustada em toda origem. Em seguida,
o mesmo ajuste é reutilizado por duas ou quatro origens. Calendário futuro
continua disponível, mas os coeficientes não incorporam as observações surgidas
depois do último *refit*.


| Política | Seasonal naive | Média sazonal | Regressão |
| ---------------------- | -------------- | ------------- | --------- |
| Refit em toda origem | 5,34% | 5,30% | **4,63%** |
| Refit a cada 2 origens | 5,34% | **5,30%** | 5,31% |
| Refit a cada 4 origens | 5,34% | **5,30%** | 5,41% |


A regressão deixa de apresentar o menor valor quando sua atualização é menos
frequente. Sob *refit* a cada duas origens, sua diferença para a média sazonal é
de apenas 0,01 ponto percentual — pequena demais para sustentar superioridade
sem uma análise de variabilidade. A cada quatro origens, o WAPE chega a 5,41%.

O seasonal naive e a média sazonal foram mantidos com atualização própria em
cada origem; o congelamento foi aplicado à regressão para isolar sua política de
treino. Em uma comparação de sistemas completos, todas as políticas precisariam
ser especificadas de acordo com a operação.

O resultado demonstra por que a cadência deve constar na documentação do
experimento. Parte do ganho atribuído ao modelo pode ser, na realidade, ganho
da atualização. Se duas soluções possuem políticas de *refit* diferentes, uma
comparação justa deve reportar acurácia, custo computacional, latência,
estabilidade e frequência de treinamento.

## 7. Seleção sem reutilizar a avaliação

Escolher uma janela depois de observar o WAPE de todos os protocolos usa o
backtest como conjunto de seleção. Relatar o menor desses valores como
estimativa imparcial de desempenho ignora que o menor valor foi selecionado
entre várias alternativas.

A validação aninhada introduz dois níveis. Para cada origem externa T_k,
folds internos anteriores a T_k selecionam:

# 
\widehat{W}_k

\arg\min_{W\in180,365,730}
\frac{1}{J_k}
\sum_{j=1}^{J_k}
\operatorname{WAPE}_{k,j}(W)


Depois, a regressão é reajustada na janela \widehat{W}_k e avaliada uma vez
no fold externo. Os resultados externos não voltam para a seleção daquela
origem. A estrutura aninhada separa escolha de configuração e estimação externa,
reduzindo o viés associado à reutilização da mesma avaliação
([Varma e Simon, 2006](https://doi.org/10.1186/1471-2105-7-91)).


| Origem externa | Janela selecionada | WAPE externo |
| -------------- | ------------------ | ------------ |
| 1.068 | 180 dias | 3,08% |
| 1.124 | 180 dias | 3,27% |
| 1.180 | 180 dias | 11,57% |
| 1.236 | 365 dias | 4,11% |


Os três primeiros folds selecionaram 180 dias. No terceiro, essa janela
encontrou uma transição de regime e o WAPE externo atingiu 11,57%. O resultado
não invalida a seleção interna: mostra que uma escolha baseada no passado pode
falhar quando o futuro muda. Na última origem, os folds internos já continham
mais evidência do novo regime e selecionaram 365 dias.

A mediana das escolhas internas foi 180 dias, configuração congelada antes do
teste final. Essa regra é simples e previamente especificada. Outra regra seria
possível, como escolher a janela mais frequente ou refazer a seleção em cada
origem operacional. O ponto metodológico é registrar a regra antes de consultar
o bloco reservado.

Validação aninhada não elimina mudança de regime nem garante que o
hiperparâmetro escolhido continuará adequado. Sua função é separar o erro do
procedimento de seleção do erro usado para avaliar o procedimento já
selecionado.

## 8. O teste final bloqueado

Os 168 dias finais são divididos em seis origens não sobrepostas. A regressão
usa janela de 180 dias, escolhida no desenvolvimento, e é reajustada em cada
origem. Nenhum resultado desse bloco altera a especificação.


| Modelo | MAE | WAPE | Viés |
| ----------------------- | --------- | --------- | ---------- |
| Seasonal naive | 13,97 | 5,77% | -1,14% |
| Média sazonal | 17,02 | 7,06% | 3,88% |
| Regressão de calendário | **12,66** | **5,23%** | **-0,02%** |


A regressão apresentou o menor erro e viés praticamente nulo. A redução relativa
do WAPE em comparação ao seasonal naive foi de aproximadamente 9,3%. O ganho é
menor que aquele observado para a janela de 365 dias no backtest de
desenvolvimento e não deve ser interpretado como garantia de estabilidade.

O teste final contém apenas seis horizontes. Ele fornece uma avaliação externa
dos candidatos congelados, mas continua sendo uma amostra temporal limitada.
Bloquear o período reduz sua reutilização durante a seleção; não elimina outras
fontes de otimismo nem a incerteza associada ao regime que ocorreu nele.

Depois da consulta, qualquer modificação orientada por esses resultados muda o
status do bloco. Se a janela for alterada porque a média sazonal teve viés
positivo, por exemplo, os 168 dias passam a integrar o desenvolvimento. Uma
nova estimativa final exigiria dados posteriores ou avaliação prospectiva.

## 9. O ranking como variável do experimento

O seasonal naive apresentou o menor WAPE em dois dos nove protocolos de
desenvolvimento. A regressão apresentou o menor valor em cinco. A média sazonal
ocupou essa posição nos dois protocolos com *refit* menos frequente da
regressão. Nenhum modelo foi invariavelmente superior.

Uma medida descritiva de estabilidade pode ser definida como:

# 
S_m

\frac{1}{P}
\sum_{p=1}^{P}
\mathbb{1}\operatorname{rank}_{m,p}=1


em que P é o número de protocolos e S_m é a proporção em que o modelo
m ocupa a primeira posição. No conjunto avaliado, a regressão apresenta
S=5/9, o seasonal naive S=2/9 e a média sazonal S=2/9.

Essa medida não constitui probabilidade de vitória em produção. Os protocolos
não são uma amostra aleatória de cenários e diferem em mais do que dificuldade.
Ela serve para revelar fragilidade: uma recomendação baseada apenas no melhor
WAPE de uma configuração omite que o ranking se inverte sob condições
operacionais plausíveis.

Uma decisão de implantação deveria considerar ao menos três dimensões:
desempenho no protocolo que representa a operação, estabilidade em análises de
sensibilidade e resultado no teste bloqueado. O protocolo operacional tem
prioridade; não se deve escolher retrospectivamente aquele que favorece o
modelo preferido.

## 10. O que pode e o que não pode ser concluído

O experimento sustenta quatro conclusões restritas.

Primeiro, a quantidade de histórico alterou substancialmente a regressão em um
processo que continha mudanças de regime. Segundo, aumentar o gap reduziu a
vantagem descritiva do candidato, mostrando que a antecedência operacional faz
parte da dificuldade avaliada. Terceiro, folds sobrepostos alteraram as origens avaliadas e
introduziram dependência, sem produzir uma relação monotônica com o erro.
Quarto, reduzir a frequência de *refit* foi suficiente para inverter o ranking.

Não se conclui que janelas deslizantes sejam geralmente superiores, que 180 ou
365 dias sejam tamanhos recomendados para dados reais, nem que regressão de
calendário seja o melhor modelo de demanda. A série é sintética, os eventos são
controlados e existem apenas três previsores simples.

Também não foi estimado um intervalo de confiança para a diferença entre os
modelos. A dependência entre folds, sobretudo nos protocolos sobrepostos,
exigiria um procedimento inferencial compatível. O objetivo aqui é estudar a
sensibilidade do estimador de desempenho, não produzir uma declaração
populacional sobre superioridade.

O refit foi simplificado. Em sistemas reais, reprocessar features, retreinar,
selecionar hiperparâmetros, calibrar intervalos e publicar previsões podem ter
cadências distintas. A política completa precisa ser reconstruída no backtest.

## 11. Implicações para projetos de forecast

Um protocolo temporal deve ser tratado como parte versionada do produto
analítico. Além do modelo e das features, a documentação precisa registrar:

- origem e horizonte;
- regra de formação da janela;
- gap e sua justificativa;
- passo entre origens;
- grau de sobreposição;
- cadência de refit;
- elementos reajustados em cada fold;
- nível interno e externo de seleção;
- localização e governança do teste final.

Esses parâmetros devem derivar do processo decisório. Se o planejamento é
mensal, o passo entre origens pode ser mensal. Se a previsão é republicada
semanalmente para um horizonte de quatro semanas, a sobreposição deve aparecer.
Se dados levam sete dias para fechar, o gap precisa representar essa latência.
Se o treinamento ocorre trimestralmente, um backtest com *refit* diário
superestima o sistema disponível.

Análises de sensibilidade continuam úteis, mas têm função diferente. Elas
mostram quanto a conclusão depende de escolhas plausíveis. Não autorizam a
seleção oportunista do protocolo que produz a narrativa desejada.

## Conclusão

O desenho de validação alterou tanto a magnitude do erro quanto o ranking dos
modelos. A regressão de calendário apresentou o maior WAPE sob janela expansiva,
o menor sob janela deslizante de 365 dias e deixou a primeira posição quando seu
*refit* se tornou menos frequente. Gaps maiores reduziram sua vantagem, enquanto
folds sobrepostos mudaram a composição e a dependência das avaliações.

A validação aninhada selecionou uma janela de 180 dias para a regressão antes da
abertura do teste final. Nesse bloco, ela registrou WAPE de 5,23%, valor menor
que o seasonal naive, mas menos favorável que algumas estimativas do
desenvolvimento. O bloco forneceu uma comparação externa sem reutilizar o
período que orientou a seleção da janela.

Em forecast, avaliar não significa apenas separar passado e futuro. Significa
reconstruir uma política de uso: quanto histórico estará disponível, qual será
a antecedência, quando o modelo será atualizado e quantas previsões coexistirão
para as mesmas datas. O ranking é condicionado a essa política. Sem declará-la,
sua utilidade operacional é limitada.

## Caderno técnico

O código, os testes e a reprodução integral estão disponíveis no
[Laboratório Forecast 201]({{ page.laboratory | relative_url }}).

## Referências

- Tashman, L. J. (2000). [Out-of-sample tests of forecasting accuracy: an
analysis and review](https://doi.org/10.1016/S0169-2070(00)00065-0).
*International Journal of Forecasting*, 16(4), 437–450.
- Bergmeir, C.; Hyndman, R. J.; Koo, B. (2018). [A note on the validity of
cross-validation for evaluating autoregressive time series
prediction](https://doi.org/10.1016/j.csda.2017.11.003).
*Computational Statistics & Data Analysis*, 120, 70–83.
- Cerqueira, V.; Torgo, L.; Mozetič, I. (2020). [Evaluating time series
forecasting models: an empirical study on performance estimation
methods](https://doi.org/10.1007/s10994-020-05910-7).
*Machine Learning*, 109, 1997–2028.
- Varma, S.; Simon, R. (2006). [Bias in error estimation when using
cross-validation for model selection](https://doi.org/10.1186/1471-2105-7-91).
*BMC Bioinformatics*, 7, 91.
- Hyndman, R. J.; Athanasopoulos, G. (2021). [Forecasting: Principles and
Practice](https://otexts.com/fpp3/), 3ª ed. OTexts.

