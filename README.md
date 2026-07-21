# ComuniDados

Site pessoal e publicação editorial de Cheila Betina, construído com Jekyll e publicado no GitHub Pages.

> Compreender dados é uma forma de participar.

## Estrutura

- `/` — página inicial
- `/artigos/` — índice de publicações
- `/laboratorio/` — projetos e investigações
- `/manifesto/` — princípios editoriais
- `/sobre/` — trajetória profissional e acadêmica
- `/cv/` — currículo resumido e PDF

## Publicar um novo artigo

Crie um arquivo em `_posts` com o padrão `AAAA-MM-DD-titulo.md`:

```yaml
---
layout: post
title: "Título do artigo"
description: "Resumo para mecanismos de busca."
date: 2026-07-20 12:00:00 -0300
category: Método
read_time: 8 min
---

Texto do artigo em Markdown.
```

## Executar localmente

Requisitos: Ruby e Bundler.

```bash
bundle install
bundle exec jekyll serve
```

Acesse `http://localhost:4000`.

## Publicação

O GitHub Pages publica o conteúdo do branch configurado no repositório. Antes de enviar alterações, execute `bundle exec jekyll build`.

Revise os textos marcados como provisórios antes da publicação definitiva.
