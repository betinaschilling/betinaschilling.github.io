---
layout: page
title: "Artigos"
description: "Textos sobre dados, inteligência artificial, decisões e sociedade."
permalink: /artigos/
---

<div class="article-index">
{% for post in site.posts %}
  <article>
    <p class="meta">{{ post.category | default: 'ARTIGO' }} · {{ post.date | date: '%d.%m.%Y' }} · {{ post.read_time | default: '8 min' }}</p>
    <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
    <p>{{ post.excerpt | strip_html | truncate: 220 }}</p>
    <a class="read-link" href="{{ post.url | relative_url }}">Ler artigo →</a>
  </article>
{% else %}
  <div class="empty-state">
    <p class="eyebrow">Caderno em branco —</p>
    <h2>Os próximos textos ainda serão escritos.</h2>
    <p>O arquivo crescerá conforme novas perguntas, investigações e evidências forem produzidas.</p>
  </div>
{% endfor %}
</div>
