<!-- DOC_TYPE: LANDING -->

# codex-django

<div class="cdx-hero">
  <p class="cdx-eyebrow">Codex Django Runtime</p>
  <h1>Reusable Django runtime modules for Codex-shaped projects.</h1>
  <p class="cdx-lead">
    <code>codex-django</code> contains the installable runtime layer: shared Django apps, adapters,
    selectors, cabinet UI primitives, booking integrations, and system helpers. Project generation
    and scaffolding now live in the companion package <code>codex-django-cli</code>.
  </p>
  <div class="cdx-actions">
    <a class="md-button md-button--primary" href="./en/getting-started/">Getting Started</a>
    <a class="md-button" href="./en/guides/runtime-vs-cli/">Runtime vs CLI</a>
    <a class="md-button" href="./en/api/README/">API Reference</a>
  </div>
</div>

## Start Here

<div class="cdx-grid cdx-grid-3">
  <div class="cdx-card">
    <h3>Use runtime modules</h3>
    <p>Install reusable Django runtime code for an existing project.</p>
    <pre><code>pip install codex-django</code></pre>
    <p><a href="./en/guides/installation-modes/">Open installation modes</a></p>
  </div>
  <div class="cdx-card">
    <h3>Add the companion CLI</h3>
    <p>Install runtime plus the published scaffolding companion package.</p>
    <pre><code>pip install "codex-django[cli]"</code></pre>
    <p><a href="./en/guides/runtime-vs-cli/">See the split</a></p>
  </div>
  <div class="cdx-card">
    <h3>Read the API</h3>
    <p>Jump directly into the Python-level reference generated from source docstrings.</p>
    <pre><code>core / system / booking / cabinet</code></pre>
    <p><a href="./en/api/README/">Browse API reference</a></p>
  </div>
</div>

## Choose A Path

<div class="cdx-grid cdx-grid-2">
  <div class="cdx-card">
    <h3>For application teams</h3>
    <ul>
      <li><a href="./en/getting-started/">Getting Started</a></li>
      <li><a href="./en/guides/installation-modes/">Installation Modes</a></li>
      <li><a href="./en/guides/project-structure/">Project Structure</a></li>
      <li><a href="./en/guides/blueprints-and-scaffolding/">Blueprint Workflow</a></li>
    </ul>
  </div>
  <div class="cdx-card">
    <h3>For maintainers</h3>
    <ul>
      <li><a href="./en/architecture/README/">Architecture Overview</a></li>
      <li><a href="./en/architecture/core/">Core Architecture</a></li>
      <li><a href="./en/architecture/system/">System Architecture</a></li>
      <li><a href="./en/api/README/">API Reference</a></li>
    </ul>
  </div>
</div>

## Runtime Modules

<div class="cdx-grid cdx-grid-3">
  <div class="cdx-card">
    <h3><code>core</code></h3>
    <p>Shared Django infrastructure: Redis managers, sitemaps, i18n helpers, context processors, and model mixins.</p>
    <p><a href="./en/architecture/core/">Architecture</a> · <a href="./en/api/core/">API</a></p>
  </div>
  <div class="cdx-card">
    <h3><code>system</code></h3>
    <p>Project-state models, static content, SEO data, fixtures, and operational settings patterns.</p>
    <p><a href="./en/architecture/system/">Architecture</a> · <a href="./en/api/system/">API</a></p>
  </div>
  <div class="cdx-card">
    <h3><code>booking</code></h3>
    <p>Django adapters over the booking engine, model mixins, cache helpers, and availability selectors.</p>
    <p><a href="./en/architecture/booking/">Architecture</a> · <a href="./en/api/booking/">API</a></p>
  </div>
  <div class="cdx-card">
    <h3><code>cabinet</code></h3>
    <p>Reusable dashboard and cabinet layer with registry-driven navigation, widgets, and site settings views.</p>
    <p><a href="./en/architecture/cabinet/">Architecture</a> · <a href="./en/api/cabinet/">API</a></p>
  </div>
  <div class="cdx-card">
    <h3><code>notifications</code></h3>
    <p>Notification payload building, selector orchestration, and queue or direct delivery adapters.</p>
    <p><a href="./en/architecture/notifications/">Architecture</a> · <a href="./en/api/notifications/">API</a></p>
  </div>
  <div class="cdx-card">
    <h3><code>showcase</code></h3>
    <p>Debug-only reference implementation for demo screens, mock data, and generated project previews.</p>
    <p><a href="./en/architecture/showcase/">Architecture</a></p>
  </div>
</div>

## Language And Reference Layers

<div class="cdx-grid cdx-grid-3">
  <div class="cdx-card">
    <h3>English guides</h3>
    <p>Task-oriented documentation for installation, runtime usage, and scaffolded-project workflows.</p>
    <p><a href="./en/README/">Open English guide</a></p>
  </div>
  <div class="cdx-card">
    <h3>Russian guides</h3>
    <p>Bilingual guide layer for the same runtime and generated-project scenarios.</p>
    <p><a href="./ru/README/">Open Russian guide</a></p>
  </div>
  <div class="cdx-card">
    <h3>Technical reference</h3>
    <p>English-only source-driven reference for public imports and internal modules.</p>
    <p><a href="./en/api/README/">Open API reference</a></p>
  </div>
</div>

## Ecosystem Direction

This site currently lives under GitHub Pages for the runtime repository. The longer-term direction is
to move Codex libraries under a shared documentation entrypoint with cross-links between runtime,
CLI, platform, services, and other package docs. The current landing structure is intentionally
organized so it can be moved into a shared docs hub without changing the user path model.
