# Forecast 101 — laboratório reproduzível

Laboratório técnico do artigo “Forecast 101: prever não é adivinhar”.

## O que ele demonstra

- origem móvel com oito folds e horizonte de 28 dias;
- baselines naive e seasonal naive sem acesso ao teste;
- regressão de calendário deliberadamente interpretável;
- MAE, RMSE, WAPE, viés, MASE e custo assimétrico;
- erro por fold e bloco de horizonte;
- intervalo de 80% com calibração temporal;
- cobertura, largura, interval score e autocorrelação dos erros.

## Dados

A série é sintética e reproduzível. Contém tendência, sazonalidade semanal,
ciclo anual, ruído, eventos pontuais e mudança de nível. Eventos e mudança não
entram no candidato para permitir diagnóstico de especificação incompleta.

Não há empresa, mercado ou processo real representado.

## Executar

Requer apenas Python 3.10 ou superior:

```bash
python3 forecast_101.py
```

O script imprime todas as métricas usadas no artigo e atualiza
`assets/images/forecast-101-backtest.svg`.

Execute também os testes de segurança metodológica:

```bash
python3 -m unittest test_forecast_101.py
```

## Convenções

- erro = previsão − observado;
- viés negativo = subprevisão;
- custo de falta = 3;
- custo de excesso = 1;
- o seasonal naive repete somente a última semana disponível na origem;
- resultados são preditivos, não causais.

## Revisão

O parecer independente está em [`REVIEW.md`](REVIEW.md). A versão anterior
continha leakage no baseline sazonal; os números antigos foram invalidados e
substituídos após correção e reteste.
