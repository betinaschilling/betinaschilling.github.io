---
layout: page
title: "Artigos"
permalink: /articles/
---

## Artigos

Lista de posts publicados:

<ul>
{% raw %}{% for post in site.posts %}{% endraw %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> — {{ "{{ post.date | date: "%Y-%m-%d" }}" }}</li>
{% raw %}{% endfor %}{% endraw %}
</ul>

> Observação: crie posts em `_posts/` com a convenção `YYYY-MM-DD-titulo.md`.
