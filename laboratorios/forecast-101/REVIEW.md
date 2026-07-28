# Parecer metodológico — Forecast 101

Status: aprovado com ressalvas para finalidade didática.

Escopo revisado: artigo, código, geração sintética, backtesting, baselines,
métricas, intervalo, interpretação e reprodução.

## Achados

| ID | Severidade | Evidência e consequência | Correção e reteste | Status |
|---|---|---|---|---|
| F101-01 | bloqueador | O seasonal naive original acessava o teste depois do 7º passo; a comparação central era inválida. | Baseline recursivo usando apenas a última semana conhecida; oito folds reexecutados. | corrigido |
| F101-02 | alto | Três folds produziam evidência frágil e dependente de poucas origens. | Ampliação para oito origens e faixa de WAPE entre folds. | corrigido |
| F101-03 | alto | O viés percentual usava a média global da série, enquanto outras métricas usavam o teste. | Viés redefinido como erro agregado dividido pelo realizado de cada fold. | corrigido |
| F101-04 | alto | Intervalo baseado em resíduos do próprio ajuste favorecia cobertura otimista. | Bloco temporal de calibração com 56 dias; cobertura, largura e interval score reportados. | corrigido com risco residual |
| F101-05 | médio | Apenas MAE, WAPE e viés ocultavam escala, extremos e decisão. | Inclusão de RMSE, MASE e custo assimétrico. | corrigido |
| F101-06 | médio | A média agregada ocultava degradação por horizonte e origem. | Erros por bloco de horizonte e faixa de WAPE entre folds. | corrigido |
| F101-07 | médio | Não havia diagnóstico de estrutura remanescente nos erros. | ACF fora da amostra nos lags 1 e 7. | corrigido parcialmente |
| F101-08 | observação | A série sintética favorece mecanismos conhecidos e não representa múltiplas séries. | Eventos e mudança de nível foram omitidos do candidato; limitação mantida explícita. | risco aceito |

## Conclusões sustentadas

- A regressão possui menor erro absoluto médio neste experimento.
- O ganho varia entre origens.
- O candidato apresenta subprevisão.
- Sob custo de falta três vezes maior, menor WAPE não implica menor custo.
- A cobertura observada está próxima de 80%, com largura material.

## Conclusões não sustentadas

- Regressão de calendário é superior para demanda diária em geral.
- O intervalo possui garantia probabilística sob qualquer dependência temporal.
- O modelo está pronto para produção.
- As variáveis de calendário causam demanda.
- O ganho sintético representa valor financeiro real.

## Riscos residuais

- somente uma série e oito origens;
- custo de decisão hipotético;
- ajuste linear via implementação didática;
- ausência de holdout final após comparação;
- intervalo pragmático sob possível mudança de regime;
- sem avaliação hierárquica, intermitente ou de covariáveis futuras.

## Próximo gate

Para avançar de laboratório didático a estudo aplicado: auditar dados reais,
definir custo com stakeholders, separar seleção e teste final, avaliar múltiplas
séries e comparar modelos adaptativos e probabilísticos.
