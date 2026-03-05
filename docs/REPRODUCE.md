# Reproduce

## Environment
- OS: WSL Ubuntu-20.04 (also works on Windows/macOS)
- Node: v20.20.0
- npm: 10.8.2
- Framework: Astro 5.17+
- Python: 3.8+ (for genetic data collector)

## Quick start
```bash
cd /mnt/d/AI_projects/BivalvePlus_project_webpage/bivalveplus-site
npm install
npx astro dev --host 0.0.0.0
```
Open http://localhost:4321/BivalvePlus_web/en/

## Build
```bash
npm run build
npm run preview
```

## Deploy (GitHub Pages)
1. Create GitHub repo: `maoxiaopeng1991-source/BivalvePlus_web`
2. Push code to main branch
3. In repo Settings > Pages > Source: GitHub Actions
4. Push triggers automatic build and deploy via `.github/workflows/deploy.yml`
5. Site URL: `https://maoxiaopeng1991-source.github.io/BivalvePlus_web/en/`

See `docs/DEPLOY.md` for full step-by-step guide.

## Run Genetic Data Collector Locally
```bash
pip install -r scripts/requirements.txt
python scripts/collect_genetic_data.py
```
Output: `src/data/genetic-{genome,population,markers}.json`

## Decap CMS Admin
After deployment: `https://maoxiaopeng1991-source.github.io/BivalvePlus_web/admin/`
See `docs/MAINTAIN.md` section "Decap CMS Setup" for OAuth configuration.
