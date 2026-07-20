---
layout: page
title: "Artigos"
permalink: /artigos/
---

<section class="paper-card p-4">
  <p class="section-label mb-3">Arquivo</p>
  <p class="mb-4">Os artigos entram como peças de leitura e interpretação. Cada texto deve explicitar contexto, método e implicações, sem perder a precisão do dado nem a clareza da conclusão.</p>
  {% if site.posts.size > 0 %}
  <ul class="article-list">
    {% for post in site.posts %}
    <li>
      <a class="article-link" href="{{ post.url | relative_url }}">
        <span>
          <strong>{{ post.title }}</strong><br />
          <span class="text-muted">{{ post.excerpt | strip_html | truncate: 160 }}</span>
        </span>
        <span class="meta-line">{{ post.date | date: "%d %b %Y" }}</span>
      </a>
    </li>
    {% endfor %}
  </ul>
  {% else %}
  <p class="mb-0">PLACEHOLDER - Ainda não há artigos publicados.</p>
  {% endif %}
</section>
