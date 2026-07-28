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

Os caminhos canônicos dos PDFs são:

```text
assets/documents/curriculo-cheila-betina-schilling.pdf
assets/documents/curriculo-cheila-betina-schilling-en.pdf
assets/documents/curriculo-cheila-betina-schilling-es.pdf
```

Antes da publicação:

1. confirme que o arquivo é um PDF válido;
2. revise telefone, endereço e demais dados pessoais;
3. atualize data, tamanho e status em `curriculo.md`;
4. habilite os links de visualização e download somente depois da revisão.

Não mantenha PDFs provisórios com extensão falsa nem cópias adicionais do currículo.

## Editar com Pages CMS

O repositório possui um `.pages.yml` na raiz. Ele configura o [Pages CMS](https://pagescms.org/) para editar artigos em `_posts`, páginas institucionais existentes e imagens em `assets/images`, preservando os nomes de front matter usados pelo Jekyll.

Para acessar:

1. abra [app.pagescms.org](https://app.pagescms.org/);
2. entre com GitHub e autorize o Pages CMS no repositório `betinaschilling/betinaschilling.github.io`;
3. selecione a branch que deseja editar — a configuração é lida por repositório e branch;
4. abra **Artigos** ou **Páginas institucionais**;
5. salve as alterações em uma branch de trabalho e revise a PR antes do merge.

Novos artigos recebem o formato de nome `AAAA-MM-DD-titulo.md`, usam `layout: post` e mantêm o conteúdo em Markdown. Imagens inseridas no rich text são salvas em `assets/images` e referenciadas como `/assets/images/...`, compatível com o Jekyll. O preview local consistente com os caminhos publicados é:

```bash
bundle exec jekyll serve
```

Depois, abra `http://localhost:4000/` ou a URL do post em `/categoria/AAAA/MM/DD/titulo/`, conforme o comportamento atual de `permalink: pretty` em `_config.yml` — por exemplo, `/método/2026/07/27/forecast-101-prever-nao-e-adivinhar/`. O Pages CMS não publica conteúdo por conta própria: ele grava alterações no GitHub; o build do GitHub Pages continua sendo a etapa de publicação.
