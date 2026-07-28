# Padrão editorial do ComuniDados

## Estrutura mínima de um artigo técnico

1. **A pergunta** — o problema em linguagem verificável.
2. **Por que importa** — decisão, pessoas afetadas e valor esperado.
3. **O que os dados permitem observar** — população, período e limites.
4. **Método** — baseline, desenho, pressupostos e alternativas.
5. **Evidências** — resultados, magnitude, incerteza e estabilidade.
6. **Limitações** — o que não foi medido ou não pode ser concluído.
7. **Implicações** — decisões proporcionais à força da evidência.
8. **Caderno técnico** — código, dados permitidos e reprodução.
9. **Referências** — fontes primárias e literatura necessária.

## Quatro camadas

Quando o conteúdo for analítico, distribuir sem repetição:

- fundamento acadêmico;
- procedimento técnico;
- interpretação de negócio;
- código documentado com objetivo, entradas, processamento, saída esperada e
  interpretação.

## Metadados obrigatórios

```yaml
---
layout: post
title: "Título"
description: "Resumo específico para busca e compartilhamento."
date: AAAA-MM-DD HH:MM:SS -0300
category: "Categoria"
series: "Série, quando aplicável"
read_time: "N min"
laboratory: "/laboratorio/nome/"
---
```

`laboratory` só deve existir quando houver caderno publicado.

## Gate editorial

Antes da publicação:

- título e descrição representam o conteúdo;
- afirmações quantitativas apontam para evidências;
- associação não é descrita como causalidade;
- baseline, período e unidade estão explícitos;
- links e caminhos foram testados;
- linguagem não promete mais do que o método entrega;
- o texto informa limites relevantes para a decisão;
- o build do site e a reprodução técnica foram verificados.
