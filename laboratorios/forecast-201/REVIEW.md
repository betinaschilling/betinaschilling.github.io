# Parecer de integridade — Forecast 201

## Escopo

Revisão cruzada entre manuscrito, código, testes e saída reproduzida. O parecer
verifica correspondência factual, alcance das conclusões, rastreabilidade das
referências e distinção entre seleção, avaliação e interpretação.

## Correções realizadas antes da publicação

- explicitado que a validação aninhada seleciona a janela da regressão, não o
  modelo entre os três candidatos;
- reformulado o teste final como comparação externa de candidatos congelados;
- corrigida a redução relativa do WAPE de 9,4% para 9,3%;
- incorporado o gap à fórmula do WAPE por fold;
- esclarecido que os protocolos formam análise de sensibilidade, não produto
  cartesiano;
- rebaixadas explicações mecanísticas sobre regimes a hipóteses compatíveis com
  o desenho;
- removidas declarações categóricas de superioridade em diferenças sem análise
  de variabilidade;
- adicionadas citações no corpo para avaliação fora da amostra, validação
  temporal, dependência e viés de seleção.

## Verificações

- os valores das nove comparações coincidem com a execução;
- os quatro resultados externos da validação aninhada coincidem com a execução;
- a janela final de 180 dias corresponde à regra implementada;
- MAE, WAPE e viés dos três candidatos no teste final coincidem com a execução;
- as origens de desenvolvimento não alcançam o teste final;
- os seis folds finais não se sobrepõem;
- os cinco testes automatizados foram aprovados.

## Ressalvas remanescentes

- não há inferência para diferenciais de perda entre modelos;
- folds sobrepostos são dependentes e não equivalem a replicações independentes;
- o teste final contém somente seis origens;
- a série e as mudanças de regime são sintéticas;
- a política de refit foi simplificada;
- o estudo estima sensibilidade do protocolo, não desempenho empresarial.

## Parecer

Publicável como experimento metodológico reproduzível. As conclusões devem
permanecer restritas ao processo simulado e às configurações executadas.
