# ComuniDados

Site pessoal e publicação editorial de Cheila Betina, construído com Jekyll e publicado no GitHub Pages.

> Compreender dados é uma forma de participar.

## Estrutura

- `/` — página inicial
- `/artigos/` — índice de publicações
- `/dossies/` — linhas de investigação que surgirão com o conteúdo
- `/investigacoes/` — ponte entre perguntas públicas e cadernos técnicos
- `/manifesto/` — princípios editoriais
- `/sobre/` — trajetória profissional e acadêmica
- `/curriculo/` — página canônica do currículo

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

## Publicar o currículo

O único caminho aceito para o PDF é:

```text
assets/documents/curriculo-cheila-betina-schilling.pdf
```

Antes da publicação:

1. confirme que o arquivo é um PDF válido;
2. revise telefone, endereço e demais dados pessoais;
3. atualize data, tamanho e status em `curriculo.md`;
4. habilite os links de visualização e download somente depois da revisão.

Não mantenha PDFs provisórios com extensão falsa nem cópias adicionais do currículo.
