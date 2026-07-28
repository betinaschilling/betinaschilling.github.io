---
layout: page
title: "Forecast 101"
description: "Caderno técnico reproduzível: backtesting, baselines, métricas, custo, incerteza e diagnóstico."
permalink: /laboratorio/forecast-101/
---

<p class="lab-status"><span>LAB 01 · V2</span><span>EXECUTADO · REVISADO COM RESSALVAS</span></p>

## Pergunta

Em uma série diária sintética, uma regressão de calendário produz previsões de
28 dias mais úteis do que baselines simples quando avaliada em oito origens
temporais?

“Mais útil” é avaliado por magnitude, escala, direção, estabilidade, incerteza e
um custo assimétrico de decisão.

## Fundamento acadêmico

Forecast é uma estimativa condicionada à informação disponível na origem. A
avaliação deve preservar a ordem temporal, comparar métodos em múltiplas
origens, usar baselines sem acesso ao teste e alinhar a função de perda à
decisão.

## Procedimento técnico

| Elemento | Definição |
|---|---|
| Frequência | diária |
| Horizonte | 28 dias |
| Validação | 8 folds de origem móvel, janela expansiva |
| Baselines | naive e seasonal naive recursivo, período 7 |
| Candidato | regressão com tendência, dia da semana e harmônicos anuais |
| Métricas | MAE, RMSE, WAPE, viés, MASE e custo assimétrico |
| Incerteza | intervalo de 80% com calibração temporal de 56 dias |
| Diagnósticos | faixa entre folds, horizonte, cobertura, largura, interval score e ACF dos erros |
| Dados | sintéticos, semente 42, com eventos e mudança de nível omitidos do modelo |

## Evidências pontuais

| Modelo | MAE | RMSE | WAPE | Faixa WAPE | Viés | MASE |
|---|---:|---:|---:|---:|---:|---:|
| Naive | 20,33 | 24,85 | 6,70% | 4,22–10,27% | 3,98% | 1,36 |
| Seasonal naive | 15,12 | 18,71 | 4,93% | 3,72–8,12% | -1,20% | 1,02 |
| Regressão de calendário | 12,34 | 15,33 | 4,05% | 2,94–5,69% | -2,53% | 0,83 |

A regressão reduziu o WAPE médio em 17,8% contra o seasonal naive. O ganho não
foi estável o suficiente para ser generalizado além do experimento, e o viés
negativo permanece relevante.

## Evidência de decisão

Para uma perda didática em que falta custa três vezes mais que excesso:

| Modelo | Índice de custo |
|---|---:|
| Naive | 9,42 |
| Regressão de calendário | 10,63 |
| Seasonal naive | 11,06 |

O candidato mais acurado não foi o de menor custo. O resultado indica
desalinhamento entre previsão central e função de decisão, não superioridade
operacional automática do naive.

## Incerteza e resíduos

| Diagnóstico | Resultado |
|---|---:|
| Cobertura nominal | 80% |
| Cobertura observada | 82,14% |
| Largura média | 40,64 |
| Interval score | 57,76 |
| ACF dos erros, lag 1 | 0,115 |
| ACF dos erros, lag 7 | 0,041 |

<figure class="article-figure">
  <img src="{{ '/assets/images/forecast-101-backtest.svg' | relative_url }}" alt="Último fold do backtesting com valores observados, seasonal naive, regressão e intervalo com calibração temporal.">
  <figcaption>Último fold. A conclusão utiliza os oito folds, não apenas esta figura.</figcaption>
</figure>

## Interpretação

O candidato demonstrou ganho preditivo neste desenho, mas não prontidão para
implantação. A subprevisão diante da mudança de nível compromete a função de
custo escolhida. O próximo experimento deveria comparar uma política quantílica
ou otimização explícita, além de testar janelas deslizantes e modelos capazes de
adaptar nível.

## Código e reprodução

- [`forecast_101.py`](https://github.com/betinaschilling/betinaschilling.github.io/blob/master/laboratorios/forecast-101/forecast_101.py)
- [README técnico](https://github.com/betinaschilling/betinaschilling.github.io/tree/master/laboratorios/forecast-101)
- [Parecer de revisão](https://github.com/betinaschilling/betinaschilling.github.io/blob/master/laboratorios/forecast-101/REVIEW.md)

```bash
cd laboratorios/forecast-101
python3 forecast_101.py
```

O laboratório usa somente a biblioteca padrão do Python 3.10 ou superior.

## Limites

Uma série sintética não representa heterogeneidade, intermitência, censura,
hierarquias ou restrições operacionais reais. O custo 3:1 é ilustrativo. O
intervalo é calibrado temporalmente, mas não oferece garantia conformal geral
sob dependência e mudança de regime.

[Ler o artigo público →]({% post_url 2026-07-27-forecast-101-prever-nao-e-adivinhar %})
