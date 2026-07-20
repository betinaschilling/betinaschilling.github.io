---
layout: home
title: "Início"
---

<section class="mb-5">
  <p class="section-label mb-3">ComuniDados</p>
  <div class="row g-4 align-items-end">
    <div class="col-lg-8">
      <h1 class="display-1 mb-3">Compreender dados é uma forma de participar.</h1>
      <p class="lead-slab mb-4">ComuniDados é uma revista-laboratório independente sobre dados, estatística, inteligência artificial, comportamento, negócios e sociedade. A publicação combina leitura editorial, método e interpretação pública para transformar evidência em compreensão.</p>
      <div class="d-flex flex-wrap gap-2">
        <a class="btn btn-primary" href="{{ '/artigos/' | relative_url }}">Ver artigos</a>
        <a class="btn btn-outline-dark" href="{{ '/laboratorio/' | relative_url }}">Explorar o laboratório</a>
      </div>
    </div>
    <div class="col-lg-4">
      <div class="note-callout">
        <p class="meta-line mb-2">Publicação independente</p>
        <p class="mb-0">Um espaço de investigação sobre dados e sociedade, com foco em leitura crítica, rigor analítico e utilidade pública.</p>
      </div>
    </div>
  </div>
</section>

<section class="mb-5">
  <div class="row g-4">
    <div class="col-lg-7">
      <div class="paper-card p-4">
        <p class="section-label mb-3">Artigos recentes</p>
        {% if site.posts.size > 0 %}
        <ul class="article-list">
          {% for post in site.posts limit: 5 %}
          <li>
            <a class="article-link" href="{{ post.url | relative_url }}">
              <span>
                <strong>{{ post.title }}</strong><br />
                <span class="text-muted">{{ post.excerpt | strip_html | truncate: 140 }}</span>
              </span>
              <span class="meta-line">{{ post.date | date: "%d %b %Y" }}</span>
            </a>
          </li>
          {% endfor %}
        </ul>
        {% else %}
        <p class="mb-0">PLACEHOLDER - Publique o primeiro artigo em <code>_posts/</code>.</p>
        {% endif %}
      </div>
    </div>
    <div class="col-lg-5">
      <div class="paper-card p-4 h-100">
        <p class="section-label mb-3">Investigações em destaque</p>
        <div class="d-grid gap-3">
          <article class="feature-card">
            <p class="meta-line mb-1">Investigação 01</p>
            <h2 class="h4">PLACEHOLDER - Título do projeto</h2>
            <p class="mb-2"><strong>Problema.</strong> PLACEHOLDER - Descreva o problema.</p>
            <p class="mb-2"><strong>Pergunta.</strong> PLACEHOLDER - Formular a pergunta.</p>
            <p class="mb-2"><strong>Dados.</strong> PLACEHOLDER - Fonte, período e recorte.</p>
            <p class="mb-0"><strong>Método.</strong> PLACEHOLDER - Método, métricas e abordagem.</p>
          </article>
          <article class="feature-card">
            <p class="meta-line mb-1">Investigação 02</p>
            <h2 class="h4">PLACEHOLDER - Título do projeto</h2>
            <p class="mb-2"><strong>Problema.</strong> PLACEHOLDER - Descreva o problema.</p>
            <p class="mb-2"><strong>Pergunta.</strong> PLACEHOLDER - Formular a pergunta.</p>
            <p class="mb-2"><strong>Dados.</strong> PLACEHOLDER - Fonte, período e recorte.</p>
            <p class="mb-0"><strong>Método.</strong> PLACEHOLDER - Método, métricas e abordagem.</p>
          </article>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="mb-5">
  <div class="row g-4">
    <div class="col-lg-7">
      <div class="paper-card p-4">
        <p class="section-label mb-3">Trecho do manifesto</p>
        <p class="pull-quote mb-0">Democratizar dados não é apenas entregar números. É distribuir capacidade de interpretação.</p>
      </div>
    </div>
    <div class="col-lg-5">
      <div class="paper-card p-4">
        <p class="section-label mb-3">Sobre a autora</p>
        <p class="mb-3">Cheila Betina Schilling dos Santos assina o ComuniDados e conduz a publicação como um espaço de escrita, método e organização de conhecimento sobre dados e sociedade.</p>
        <a class="btn btn-outline-dark" href="{{ '/sobre-mim/' | relative_url }}">Ler a apresentação completa</a>
      </div>
    </div>
  </div>
</section>
