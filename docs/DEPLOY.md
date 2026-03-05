# Deployment Guide — BivalvePlus Website

## Prerequisites

- GitHub account: `maoxiaopeng1991-source`
- Node.js >= 20 installed locally
- Git installed

## Step 1 — Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `BivalvePlus_web`
3. Visibility: Public (required for free GitHub Pages)
4. Do NOT initialize with README (we will push existing code)
5. Click "Create repository"

## Step 2 — Initialize Local Git and Push

```bash
cd /mnt/d/AI_projects/BivalvePlus_project_webpage/bivalveplus-site

# Initialize git (if not already)
git init
git branch -M main

# Add remote
git remote add origin https://github.com/maoxiaopeng1991-source/BivalvePlus_web.git

# Stage all files
git add .
git commit -m "feat: BivalvePlus website Phase 1-7"

# Push
git push -u origin main
```

## Step 3 — Enable GitHub Pages

1. Go to https://github.com/maoxiaopeng1991-source/BivalvePlus_web/settings/pages
2. Under "Build and deployment":
   - Source: **GitHub Actions**
3. The `deploy.yml` workflow will auto-trigger on push to `main`

## Step 4 — Verify Deployment

1. Go to repo > Actions tab — check the "Deploy to GitHub Pages" workflow completes
2. Visit: `https://maoxiaopeng1991-source.github.io/BivalvePlus_web/en/`
3. Verify all pages load: Homepage, About, Events, Release, Genetic Resources

## Step 5 — Enable Genetic Resources Auto-Update

The `update-genetic-data.yml` workflow runs weekly (Monday 06:00 UTC).

To verify it works:
1. Go to repo > Actions > "Update Genetic Resources Data"
2. Click "Run workflow" > "Run workflow" (manual trigger)
3. Check that `src/data/genetic-*.json` files get updated and committed

## Step 6 — Set Up Decap CMS (Optional)

See `docs/MAINTAIN.md` section "Decap CMS Setup" for OAuth configuration.

## Configuration Reference

| File | Purpose |
|------|---------|
| `astro.config.mjs` | `site` and `base` URL settings |
| `.github/workflows/deploy.yml` | Auto-deploy on push to main |
| `.github/workflows/update-genetic-data.yml` | Weekly genetic data collector |
| `public/admin/config.yml` | Decap CMS configuration |

## Troubleshooting

### Build fails in GitHub Actions
- Check Actions tab for error logs
- Most common: Node version mismatch — workflow uses Node 20
- Run `npm run build` locally first to catch errors

### Pages shows 404
- Confirm Settings > Pages > Source is "GitHub Actions" (not "Deploy from branch")
- Confirm `astro.config.mjs` has correct `site` and `base`
- Wait 2-3 minutes after deploy for propagation

### Genetic data workflow fails
- Check if NCBI/ENA APIs are temporarily down
- The script has built-in retry logic and graceful error handling
- Manual trigger: Actions > "Update Genetic Resources Data" > Run workflow
