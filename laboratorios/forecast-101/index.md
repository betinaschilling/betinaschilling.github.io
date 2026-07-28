---
layout: page
title: "Forecast 101"
description: "Caderno técnico reproduzível: baseline, regressão temporal, backtesting e incerteza."
permalink: /laboratorio/forecast-101/
---

<p class="lab-status"><span>LAB 01</span><span>EXECUTADO E VERIFICADO</span></p>

## Pergunta

Para planejar os próximos 28 dias, uma regressão com informações de calendário
prevê uma demanda diária sintética melhor do que repetir o observado sete dias
antes?

## Fundamento acadêmico

Forecast é uma estimativa condicional à informação disponível na origem da
previsão. Por isso, a avaliação deve preservar a ordem temporal, comparar o
modelo com um baseline pertinente e simular o horizonte real da decisão.

## Procedimento técnico

| Elemento | Definição |
|---|---|
| Frequência | Diária |
| Horizonte | 28 dias |
| Validação | 3 folds, janela expansiva |
| Baseline | Seasonal naive, período 7 |
| Candidato | Regressão linear com tendência, dia da semana e ciclo anual |
| Métricas | MAE, WAPE, viés e cobertura do intervalo empírico de 80% |
| Dados | Sintéticos, semente 42 |

## Evidências

| Modelo | MAE médio | WAPE médio | Viés médio |
|---|---:|---:|---:|
| Seasonal naive | 13,22 | 4,45% | -0,99% |
| Regressão de calendário | 10,26 | 3,46% | -0,33% |

Neste desenho, a regressão reduziu o WAPE em 22,25% contra o baseline. A
cobertura média do intervalo empírico de 80% foi 83,33%.

Esses números descrevem este experimento sintético; não constituem evidência de
superioridade universal do modelo.

<figure class="article-figure">
  <img src="{{ '/assets/images/forecast-101-backtest.svg' | relative_url }}" alt="Último fold do backtesting com valores observados, baseline, regressão e intervalo empírico.">
  <figcaption>Último fold: comparação fora da amostra e intervalo empírico de 80%.</figcaption>
</figure>

## Interpretação para decisão

O modelo candidato justificaria avançar para validações mais próximas da
operação. Ainda não justificaria implantação. Em dados reais, seria necessário
avaliar qualidade, eventos, estabilidade, múltiplas séries, custos assimétricos
e desempenho por horizonte.

## Código e reprodução

O código documenta objetivo, entradas, processamento, saídas e interpretação:

- [`forecast_101.py`](https://github.com/betinaschilling/betinaschilling.github.io/blob/master/laboratorios/forecast-101/forecast_101.py)
- [`requirements.txt`](https://github.com/betinaschilling/betinaschilling.github.io/blob/master/laboratorios/forecast-101/requirements.txt)
- [README técnico](https://github.com/betinaschilling/betinaschilling.github.io/tree/master/laboratorios/forecast-101)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python forecast_101.py
```

## Limites

Não há promoções, ruptura, mudança de regime, múltiplas séries ou custos
assimétricos. O intervalo empírico é didático e não substitui uma solução
probabilística calibrada.

[Ler o artigo público →]({% post_url 2026-07-27-forecast-101-prever-nao-e-adivinhar %})
