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

## Tasks

| ID | Spec | Route | Status | Evidence |
| --- | --- | --- | --- | --- |
| T1 | S1, S2 | inline | done | deps installed, project + apps created |
| T2 | S3 | inline | done | settings, host middleware |
| T3 | S4, S5 | inline | done | base.html, manifest, sw.js, assets |
| T4 | S6 | inline | done | home.html |
| T5 | S7 | inline | done | model + migration |
| T6 | S8, S9 | inline | done | views, urls, fragments |
| T7 | S10 | inline | done | check + tests |
| T8 | S11 | inline | done | gate report |

## Log

- **L1** Verbatim request: Phase 1 of "Dashboard Personal Autoalojado" — environment and base structure, master design with design-taste-frontend plus PWA, complete `tareas` module with HTMX, and validation of the server plus the visual gate with `CHROME_PATH`.
- **L2** Repo root is `Sistema_autoalojado` inside `Implementacion`; the skill, Chrome for Testing and `.taste-skill` live one level up, so the gate runs from `Implementacion` against `http://127.0.0.1:8765/`.
- **L3** Design deal: palette `cool-white-slate` (#f7f9fa ground, #0d7480 accent), type Mona Sans + Geist Mono, radius soft, hero `split`, one moment `word-highlight`. Fonts self-hosted so the PWA works offline.
- **L4** Tailwind is compiled locally (v4 CLI, theme + utilities, no preflight so the skill's system.css keeps its reset); the skill's own system/layout/motion/cards CSS is vendored unchanged under `static/vendor/taste/`.
