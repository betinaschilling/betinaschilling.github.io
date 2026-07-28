# Forecast 201 — validação temporal

Laboratório reproduzível do artigo “Forecast 201: como a validação temporal
altera a conclusão”.

## O que demonstra

- separação entre desenvolvimento e teste final bloqueado;
- janelas expansiva e deslizantes;
- gaps de 7 e 14 dias;
- folds não sobrepostos e sobrepostos;
- diferentes cadências de refit;
- seleção de janela por validação temporal aninhada;
- sensibilidade do WAPE e do ranking ao protocolo.

## Executar

```bash
python3 forecast_201.py
python3 -m unittest -v test_forecast_201.py
```

O laboratório usa somente a biblioteca padrão do Python 3.10 ou superior.

O parecer de integridade que confronta manuscrito, código e resultados está em
[`REVIEW.md`](REVIEW.md).

## Convenções

- origem é o primeiro índice ainda não utilizado no treinamento;
- gap começa imediatamente após a origem;
- horizonte é sempre de 28 dias;
- o teste final contém 168 dias e não participa da seleção;
- folds sobrepostos são tratados como medições dependentes;
- erro é previsão menos observado;
- resultados sintéticos demonstram método, não desempenho operacional.
