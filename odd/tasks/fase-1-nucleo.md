# Fase 1 — Núcleo Django, diseño base y módulo de tareas

Branch: `fase-1-nucleo` · Delivery: work-unit commits, review slices by module · Test runner: `python manage.py test`
Design system: design-taste-frontend 2.5.1 (software kind), dealt palette `cool-white-slate`, type `mona`, hero `split`, moment `word-highlight`.

## Specs

- **S1** `requirements.txt` lists `django`, `requests`, `websocket-client`, `python-dotenv`; `.env.example` holds `SECRET_KEY`, `DEBUG=True`, `FINNHUB_API_KEY` and `ALLOWED_HOSTS=localhost,127.0.0.1,100.*`.
- **S2** Django project package `config`, apps `portafolio`, `tareas`, `horarios`, `nube`, and the physical folder `almacenamiento_nube/`.
- **S3** `config/settings.py` loads `.env` via python-dotenv, registers the four apps, sets the time zone, defines `NUBE_ROOT_DIR`, and accepts local network plus Tailscale (`100.*` / 100.64.0.0/10) hosts.
- **S4** `templates/base.html` loads Tailwind CSS and HTMX; desktop (md+) shows a fixed sidebar with Resumen, Portafolio, Tareas, Horarios, Nube; mobile (<md) shows a fixed bottom navigation (`fixed bottom-0 md:hidden`) with the same five links.
- **S5** `static/manifest.json` plus `static/sw.js` make the app installable as a PWA from the phone.
- **S6** `templates/home.html` shows a clean overview with widgets that link to the four modules.
- **S7** `tareas.Tarea` has `titulo`, `completada`, `prioridad` (`B` Baja, `M` Media, `A` Alta), `fecha_limite` (optional), `creada_en`; migrations run on SQLite.
- **S8** `tareas/urls.py` + views list, create, toggle completed/pending and delete tasks.
- **S9** `tareas/templates/tareas/index.html`, `partials/_form_tarea.html` and `partials/_item_tarea.html`: every mutation returns only the fragment, swapped by `hx-post`/`hx-delete` with `hx-target`/`hx-swap`, no full page reload.
- **S10** `python manage.py check` and `runserver` start without errors; `python manage.py test` passes.
- **S11** Visual gate: `node .agents/skills/design-taste-frontend/scripts/gate.mjs` runs against the live dev server with `CHROME_PATH` exported and its findings are fixed or reported.
- **S13** Tareas refresh: the list re-fetches `GET /tareas/lista/` every 5 s, sending the last `ETag`; `304` leaves the DOM untouched, a change replaces only the list container. The form is never part of the swap, so a draft in the input survives; polling pauses when the tab is hidden and while a local HTMX request is in flight.
- **S12** Tareas, phone (<768px): the inline create form is hidden so the list starts right under the counters; a circular "+" above the bottom bar opens a bottom sheet with Título, Prioridad, Fecha límite and Añadir tarea, which closes on create or on a tap outside. From 768px the form stays horizontal and inline, unchanged.

## Tasks

| ID | Spec | Route | Status | Evidence |
| --- | --- | --- | --- | --- |
| T1 | S1, S2 | inline | done | 92944d0: venv, requirements, config + 4 apps, almacenamiento_nube/ |
| T2 | S3 | inline | done | 92944d0: dotenv, PrefixHostMiddleware (100.* + 100.64/10), NUBE_ROOT_DIR |
| T3 | S4, S5 | inline | done | ad9d771: base.html rail + bottom bar, manifest.json, sw.js, self-hosted fonts |
| T4 | S6 | inline | done | ad9d771: home.html with live task window, module cards, word-highlight moment |
| T5 | S7 | inline | done | 92944d0: Tarea + 0001_initial on SQLite |
| T6 | S8, S9 | inline | done | 92944d0: views, urls, _form_tarea/_item_tarea/_contadores, HTMX |
| T7 | S10 | inline | done | `manage.py check` clean; 18 tests OK; scripts/e2e.mjs 15/15 in Chrome |
| T8 | S11 | inline | done | GATE: FAIL 1 (round 2 of 3) — only `nav`, see L6 |
| T9 | S12 | inline | done | bottom sheet + FAB; 19 tests OK; e2e (desktop and phone) OK |
| T10 | S13 | inline | done | GET /tareas/lista/ + ETag/304, polling in tareas.js; 25 tests OK; e2e: 0 mutations idle, remote task arrives with the draft intact |

## Log

- **L1** Verbatim request: Phase 1 of "Dashboard Personal Autoalojado" — environment and base structure, master design with design-taste-frontend plus PWA, complete `tareas` module with HTMX, and validation of the server plus the visual gate with `CHROME_PATH`.
- **L2** Repo root is `Sistema_autoalojado` inside `Implementacion`; the skill, Chrome for Testing and `.taste-skill` live one level up, so the gate runs from `Implementacion` against `http://127.0.0.1:8765/`.
- **L3** Design deal: palette `cool-white-slate` (#f7f9fa ground, #0d7480 accent), type Mona Sans + Geist Mono, radius soft, hero `split`, one moment `word-highlight`. Fonts self-hosted so the PWA works offline.
- **L4** Tailwind is compiled locally (v4 CLI, theme + utilities, no preflight so the skill's system.css keeps its reset); the skill's own system/layout/motion/cards CSS is vendored unchanged under `static/vendor/taste/`.
- **L5** The app shell keeps the brief's fixed 248px rail (desktop) and 64px bottom bar (phone). The gate's `nav` rule wants a top marketing bar instead, so it is the one open FAIL; the five `container-edges` findings caused by the rail offset are waived with reasons in `.taste-skill/waivers.json`. Layout check: no findings at 1440x900, 1024x768, 820x1180, 768x1024 and 390x844.
- **L6** Gate run on the final page: `GATE: FAIL 1 (round 2 of 3)`, 1 FAIL (`nav`), 5 waivers, 3 WARN (`scroll-reveal` and `split-pair` inside the dealt moment, `fade-cut` on a mock row). Rounds were not forced to OPEN because no legal fix exists for `nav` without dropping the required sidebar.
- **L7** Phone compose (2026-11-13): on a phone the form became a bottom sheet behind a round "+" button above the tab bar, so the list sits right under the counters. One form element serves both layouts (inline from 768px, sheet below), the create response carries `HX-Trigger: tarea-creada` to close the sheet, and the service worker cache version moved to `panel-v2` so the phone picks up the new CSS.
- **L8** Stale PWA cache (2026-11-13): after the phone-sheet deploy the browser kept the old `app.css` (service worker, cache-first), so the new markup rendered unstyled. Fixed for good: the worker registers only with `DEBUG=False` (or `PWA_ENABLED=True`), the page unregisters any old worker, clears its caches and reloads once, and every CSS/JS URL carries a `?v=` mtime stamp.
- **L10** Background refresh (2026-11-14): the list polls `GET /tareas/lista/` every 5 s with `If-None-Match`; the server answers 304 on an unchanged fingerprint, so an idle list produces zero DOM mutations (measured in e2e). A change replaces `#lista-tareas` and `htmx.process()` binds the injected rows; the form is outside the swap. Polling stops when the tab is hidden and skips a tick while an HTMX request is in flight.
- **L9** Verification: `python manage.py check` clean; `python manage.py test` 18 tests OK; `node scripts/e2e.mjs` passes create/toggle/delete in a real Chrome with no page reload; screenshots at 1440 and 390 reviewed.
