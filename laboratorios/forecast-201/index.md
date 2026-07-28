---
layout: page
title: "Forecast 201"
description: "Caderno técnico reproduzível sobre janelas, gaps, sobreposição, refit, validação aninhada e teste final."
permalink: /laboratorio/forecast-201/
---

<p class="lab-status"><span>LAB 02 · V1</span><span>EXECUTADO · TESTADO</span></p>

## Pergunta

Mantidos os dados, os modelos, o horizonte e as métricas, em que medida o
protocolo de validação temporal altera a estimativa de desempenho e o ranking?

## Desenho

| Elemento | Definição |
|---|---|
| Série | sintética, diária, 1.460 observações, semente 201 |
| Desenvolvimento | 1.292 dias |
| Teste final | 168 dias bloqueados, seis origens não sobrepostas |
| Horizonte | 28 dias |
| Modelos | seasonal naive, média sazonal e regressão de calendário |
| Janelas | expansiva, 365 dias e 180 dias |
| Gaps | 0, 7 e 14 dias |
| Passos | 28, 14 e 7 dias |
| Refit | toda origem, a cada 2 ou a cada 4 origens |
| Seleção | validação temporal aninhada de 180, 365 ou 730 dias |
| Métricas | MAE, WAPE e viés |

## Sensibilidade no desenvolvimento

| Protocolo | Seasonal naive | Média sazonal | Regressão | Vencedor |
|---|---:|---:|---:|---|
| Expansiva | 5,34% | 8,49% | 8,89% | Seasonal naive |
| Deslizante 365d | 5,34% | 5,30% | 4,63% | Regressão |
| Deslizante 180d | 5,34% | 6,56% | 5,36% | Seasonal naive |
| Gap 7d | 5,65% | 5,36% | 4,91% | Regressão |
| Gap 14d | 5,86% | 5,43% | 5,31% | Regressão |
| Sobreposição 50% | 6,05% | 6,93% | 5,40% | Regressão |
| Sobreposição 75% | 5,51% | 7,40% | 4,89% | Regressão |
| Refit a cada 2 origens | 5,34% | 5,30% | 5,31% | Média sazonal |
| Refit a cada 4 origens | 5,34% | 5,30% | 5,41% | Média sazonal |

<figure class="article-figure">
  <img src="{{ '/assets/images/forecast-201-validation.svg' | relative_url }}" alt="Sensibilidade do WAPE dos modelos aos protocolos temporais.">
  <figcaption>O protocolo altera o erro estimado e, em quatro configurações, o modelo com menor WAPE no desenho de referência.</figcaption>
</figure>

## Validação aninhada e teste final

A janela foi selecionada apenas em folds internos. A mediana das quatro
seleções externas foi 180 dias, configuração congelada antes da abertura do
teste final.

| Modelo | MAE final | WAPE final | Viés final |
|---|---:|---:|---:|
| Seasonal naive | 13,97 | 5,77% | -1,14% |
| Média sazonal | 17,02 | 7,06% | 3,88% |
| Regressão de calendário | **12,66** | **5,23%** | **-0,02%** |

## Interpretação

A regressão apresentou o menor WAPE no teste final, mas não foi invariavelmente
superior no desenvolvimento. Janela, gap e refit representam políticas de uso, e não
detalhes neutros de implementação. Folds sobrepostos aumentam a cobertura de
origens, mas não geram evidência independente na mesma proporção.

## Reprodução

- [`forecast_201.py`](https://github.com/betinaschilling/betinaschilling.github.io/blob/master/laboratorios/forecast-201/forecast_201.py)
- [`test_forecast_201.py`](https://github.com/betinaschilling/betinaschilling.github.io/blob/master/laboratorios/forecast-201/test_forecast_201.py)
- [Parecer de integridade](https://github.com/betinaschilling/betinaschilling.github.io/blob/master/laboratorios/forecast-201/REVIEW.md)
- [README técnico](https://github.com/betinaschilling/betinaschilling.github.io/tree/master/laboratorios/forecast-201)

```bash
cd laboratorios/forecast-201
python3 forecast_201.py
python3 -m unittest -v test_forecast_201.py
```

## Limitações

Os resultados são sintéticos. A comparação não estima intervalos para
diferenças entre modelos e não representa hierarquias, demanda intermitente ou
custos de produção. A política de refit foi simplificada.

[Ler o artigo público →]({% post_url 2026-07-28-forecast-201-validacao-temporal %})
