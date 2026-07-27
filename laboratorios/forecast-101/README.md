# Forecast 101: prever não é adivinhar

Laboratório didático para o artigo [Forecast 101: prever não é adivinhar](/2026/07/27/forecast-101-prever-nao-e-adivinhar/).

## O que existe aqui

`forecast_101.py` gera uma demanda diária sintética e reproduz um backtest com três folds, janela expansiva e horizonte de 28 dias. A série tem tendência, sazonalidade semanal, ciclo anual e ruído. Ela não representa uma empresa, mercado ou processo real.

O experimento compara:

- `seasonal naive`, que repete o valor de sete dias atrás;
- regressão linear de calendário, com tendência, dia da semana, seno e cosseno anuais.

O script calcula MAE, WAPE, viés e cobertura de um intervalo empírico de 80%. Também escreve `assets/images/forecast-101-backtest.svg`, a figura usada no artigo.

## Executar

```bash
python3 forecast_101.py
```

O resultado deve ser idêntico entre execuções. Não há dados externos nem arquivos de entrada; a semente é fixada em `42`. O código usa somente a biblioteca padrão do Python.

## Limites

O objetivo é explicar o desenho de uma avaliação, não produzir uma previsão operacional. A demanda é sintética, a regressão é intencionalmente simples, o intervalo é empírico e não há tratamento de feriados, mudanças de regime, dados faltantes ou custos de decisão. Nenhum resultado deve ser interpretado como causalidade ou como prontidão para produção.
