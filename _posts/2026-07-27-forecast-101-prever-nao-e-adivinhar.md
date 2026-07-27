---
layout: post
title: "Forecast 101: prever não é adivinhar"
description: "Um primeiro tutorial sobre previsão, backtesting e decisões de negócio — com dados sintéticos e código reproduzível."
date: 2026-07-27 12:00:00 -0300
category: Método
read_time: 12 min
---

Prever não é adivinhar o futuro. É construir uma estimativa sobre um alvo definido, em um horizonte definido, usando apenas a informação que estaria disponível no momento da decisão — e medir o quanto essa estimativa ajuda.

Neste primeiro tutorial técnico do ComuniDados, vamos acompanhar uma demanda diária didática. O objetivo não é encontrar “o melhor modelo”, mas tornar visível o percurso entre uma pergunta de negócio e uma evidência que pode orientar uma decisão.

## 1. Previsão é apoio à decisão

Imagine uma operação que precisa decidir quanto de um produto deixar disponível nas próximas quatro semanas. A previsão não responde sozinha “quanto comprar”. Ela oferece um cenário quantitativo para comparar com capacidade, estoque, custo de falta e custo de excesso.

Uma previsão útil, portanto, começa pela decisão: qual ação será tomada, quando, com que margem de erro e com quais consequências? Sem isso, uma métrica menor pode ser apenas um número bonito.

O fluxo deste tutorial é:

> problema → dados confiáveis → modelo → evidência → decisão → feedback para o problema

## 2. Alvo, frequência e horizonte

Antes de escolher um algoritmo, precisamos definir três coisas:

- **alvo:** a quantidade que queremos prever — aqui, demanda diária;
- **frequência:** a unidade de tempo — aqui, um valor por dia;
- **horizonte:** quantos passos à frente — aqui, 28 dias.

Essas escolhas são de negócio tanto quanto estatísticas. Prever vendas por hora para decidir compras mensais pode adicionar detalhe sem melhorar a decisão. Prever um mês inteiro com um único número pode esconder picos importantes.

O laboratório usa 730 observações de uma série **sintética**, criada apenas para fins didáticos. Ela contém tendência, sazonalidade semanal, um ciclo anual e ruído aleatório. Não há uma empresa ou processo real por trás dos dados.

## 3. Séries temporais têm memória

Em uma tabela comum, embaralhar linhas pode ser aceitável durante uma validação. Em uma série temporal, o tempo é parte da informação. O valor de amanhã não pode influenciar uma previsão feita hoje.

Isso também muda a pergunta estatística. Não queremos saber apenas se o modelo explica bem dados que já viu; queremos simular como ele se comporta quando chega uma data futura. Por isso, separamos treino e teste respeitando a ordem cronológica.

## 4. O risco de vazamento temporal

Há vazamento temporal quando uma informação do futuro entra, direta ou indiretamente, no treinamento ou na preparação do passado. Alguns exemplos:

- calcular uma média móvel usando valores posteriores à data de previsão;
- normalizar toda a série antes da separação temporal;
- usar uma variável publicada somente depois do evento;
- embaralhar observações e fazer uma validação aleatória.

O resultado pode parecer excelente e falhar justamente no dia em que a previsão for necessária. A regra prática é simples: para cada origem do backtest, treino, transformações e seleção de parâmetros devem usar somente o passado daquela origem.

## 5. O baseline obrigatório: seasonal naive

Um modelo sofisticado precisa superar uma referência plausível. Para dados diários com comportamento semanal, o **seasonal naive** prevê o próximo valor repetindo o valor de sete dias atrás:

\[
\hat y_{t+h} = y_{t+h-7}
\]

Ele é simples, transparente e difícil de “enganar”. Se um candidato não melhora essa referência fora da amostra, talvez não esteja aprendendo algo útil — ou talvez a melhoria não compense sua complexidade e seu custo operacional.

## 6. Backtesting com origem móvel

O laboratório usa três folds, horizonte de 28 dias e janela expansiva. Em cada fold, o modelo treina em tudo que aconteceu até uma origem, prevê os 28 dias seguintes, registra o erro e avança a origem. O treino cresce, mas nunca inclui o futuro do teste.

<div class="table-wrap">
<table>
<thead><tr><th>Fold</th><th>Treino</th><th>Teste</th><th>O que simula</th></tr></thead>
<tbody>
<tr><td>1</td><td>passado inicial</td><td>28 dias</td><td>primeira implantação</td></tr>
<tr><td>2</td><td>+28 dias</td><td>28 dias</td><td>recalibração com dados novos</td></tr>
<tr><td>3</td><td>+56 dias</td><td>28 dias</td><td>operação mais recente</td></tr>
</tbody>
</table>
</div>

![Backtest do último fold: observado, baseline, modelo e intervalo empírico de 80%.]({{ '/assets/images/forecast-101-backtest.svg' | relative_url }})

*A faixa amarela é um intervalo empírico, não uma garantia de que o futuro estará contido nele.*

## 7. Um modelo candidato interpretável

O candidato é uma regressão linear de calendário. Suas variáveis são:

- tendência, para representar uma mudança gradual;
- indicadores de dia da semana, para representar o padrão semanal;
- seno e cosseno do ciclo anual, para representar uma oscilação contínua.

Uma representação simplificada é:

\[
\hat y_t = \beta_0 + \beta_1 t + \sum_d \gamma_d I(weekday_t=d) + \alpha\sin(2\pi t/365{,}25) + \delta\cos(2\pi t/365{,}25)
\]

O modelo é candidato, não “a verdade” sobre a demanda. Seus coeficientes ajudam a auditar o que entrou na previsão, mas não provam que os calendários causam a demanda. Associação preditiva não é causalidade.

## 8. MAE, WAPE e viés

Usamos três leituras complementares:

| Métrica | Pergunta | Cuidado |
| --- | --- | --- |
| MAE | Em média, quantas unidades erramos? | Depende da escala do alvo. |
| WAPE | Qual é o erro absoluto em relação ao volume observado? | Pode ser instável quando o volume é muito baixo. |
| Viés | Estamos sistematicamente acima ou abaixo? | Erros positivos e negativos podem se cancelar. |

O MAE é a média de \(|\hat y-y|\). O WAPE é a soma dos erros absolutos dividida pela soma dos valores observados. Neste artigo, viés é o erro médio (previsão menos observado); viés negativo indica subprevisão.

O laboratório imprime os resultados efetivamente obtidos ao ser executado. Eles podem ser comparados com os números deste tutorial, mas não devem ser copiados sem rodar o código.

Nesta implementação, a média dos três folds foi:

| Modelo | MAE | WAPE | Viés | Cobertura 80% |
| --- | ---: | ---: | ---: | ---: |
| Seasonal naive | 13,22 | 4,45% | -0,99% | — |
| Regressão de calendário | 10,26 | 3,46% | -0,33% | 83,33% |

O WAPE caiu 22,25% em relação ao baseline. Essa é uma evidência sobre esta série sintética, neste desenho de backtest; não é uma garantia de ganho em outra operação.

## 9. Previsão pontual e intervalo

A previsão pontual responde “qual é o valor central esperado?”. Para decisões, isso costuma ser insuficiente. Um estoque pode ser dimensionado para o centro, para um limite superior ou para uma regra de custo específica.

Neste exemplo, o intervalo empírico de 80% é construído a partir do percentil dos valores absolutos dos resíduos de treino da regressão. Ele é uma aproximação didática: não incorpora toda a incerteza de estimação, pode não funcionar sob mudança de regime e não deve ser tratado como uma promessa probabilística universal.

## 10. Como isso chega ao negócio

Suponha que o candidato reduza o erro em relação ao seasonal naive. Isso pode justificar uma investigação sobre estoque, escala de equipe ou capacidade logística. Não justifica automaticamente uma compra maior.

Uma decisão responsável pergunta:

1. Qual é o custo de errar para cima e para baixo?
2. O ganho aparece nos três folds ou em apenas um período?
3. O intervalo é largo demais para a operação?
4. O calendário futuro estará disponível no momento da previsão?
5. O processo de monitoramento detectará deterioração?

O valor da previsão está na combinação entre desempenho fora da amostra, incerteza explícita e uma regra de ação. Sem a última parte, o modelo ainda não é uma solução de negócio.

## 11. Limites metodológicos

Este é um laboratório pequeno e intencionalmente controlado. A série é sintética; o padrão semanal e anual foi colocado no gerador; o modelo não trata feriados, promoções, rupturas, dados ausentes, mudanças de regime ou covariáveis externas. Três folds não descrevem todos os futuros possíveis.

Também não há aqui uma análise de causalidade, experimento de intervenção ou avaliação financeira. O resultado é uma demonstração de desenho de validação e de comunicação de incerteza. O modelo não está pronto para produção.

## 12. Reproduza no laboratório

O código completo está em [`laboratorios/forecast-101/`](https://github.com/betinaschilling/betinaschilling.github.io/tree/master/laboratorios/forecast-101). Ele documenta objetivo, entradas, processamento, saídas e interpretação, gera a figura deste artigo e usa a semente aleatória 42.

```bash
cd laboratorios/forecast-101
python3 forecast_101.py
```

Se você alterar o gerador, o horizonte, os folds ou a definição das métricas, registre a mudança. Reprodutibilidade não é apenas obter o mesmo número: é conseguir explicar de onde ele veio.

## Referências

- Hyndman, R. J.; Athanasopoulos, G. **Forecasting: Principles and Practice**. 3. ed. OTexts, 2021. [Livro online](https://otexts.com/fpp3/).
- Makridakis, S.; Spiliotis, E.; Assimakopoulos, V. **The M4 Competition: Results, findings, conclusion and way forward**. *International Journal of Forecasting*, 2018, 34(4), 802–808. [DOI: 10.1016/j.ijforecast.2018.06.001](https://doi.org/10.1016/j.ijforecast.2018.06.001).

Prever não é adivinhar. É explicitar uma pergunta, respeitar o tempo, comparar com uma referência e devolver à decisão tanto uma estimativa quanto seus limites.
