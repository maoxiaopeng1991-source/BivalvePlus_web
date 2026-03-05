# Project State - BivalvePlus Project Webpage

## Goal
- Build a bilingual (EN/PT) static website for BivalvePlus using Astro + GitHub Pages (free)

## Current status
- Phase 1-2 complete: Astro skeleton, GitHub Actions, Header/Nav/Footer, Homepage, pixel art theme
- Phase 3 complete: About Us page (EN+PT)
- Phase 4 complete: Events page (EN+PT) — 5-tab, Leaflet map, 4-color species markers, content collections
- Phase 5 complete: Release page (EN+PT) — 5-tab, DataTable/PublicationCard/SuggestionCard, all Coming Soon
- Phase 6 complete: Genetic Resources (EN+PT) — 3-tab, Python collector, GitHub Actions cron
- Phase 7 complete: Deployment docs, maintenance guide, Decap CMS, config finalized

## Completed milestones
- [x] M1 - Astro skeleton + GitHub Pages deploy + docs + images
- [x] M2 - Header/Nav + Footer + Homepage + pixel art theme
- [x] M3 - About Us (aims, basic info, project info, team, stakeholders)
- [x] M4 - Events (5-tab, Leaflet map 34 markers, content collections)
- [x] M5 - Release (5-tab, DataTable searchable+CSV, PublicationCard, SuggestionCard, utterances placeholder)
- [x] M6 - Genetic Resources (3-tab: Genome/Population/Markers, Python collector, NCBI+ENA+BOLD APIs, GitHub Actions weekly cron)
- [x] M7 - Deployment docs + maintenance guide + Decap CMS + config finalized

## Next actions
- [ ] M8 - PPT slides for each module

## Key files (Phase 7)
- docs/DEPLOY.md — Full deployment guide (GitHub Pages + OAuth)
- docs/MAINTAIN.md — Content management manual (events, releases, genetic data, CMS setup)
- docs/REPRODUCE.md — Updated with all reproduction steps
- public/admin/index.html — Decap CMS entry point
- public/admin/config.yml — CMS configuration (events collection)
- astro.config.mjs — Updated: site=maoxiaopeng1991-source.github.io, base=/BivalvePlus_web

## GitHub
- Repo: maoxiaopeng1991-source/BivalvePlus_web
- URL: https://maoxiaopeng1991-source.github.io/BivalvePlus_web/en/

## Blockers / Risks
- .md file Write blocked by hook (use Python/Bash)
- Browser caching: clear Vite cache + restart dev server
- BOLD v5 transition: only v4 stats endpoint works, specimen/sequence endpoints offline
- Decap CMS OAuth: requires Netlify account for free auth proxy (see MAINTAIN.md)
