# Maintenance Guide — BivalvePlus Website

## Content Structure Overview

| Content Type | Location | Format | How to Update |
|---|---|---|---|
| Events (sampling/experiment/etc.) | `src/content/events/*.md` | Markdown + frontmatter | Manual or Decap CMS |
| Release data (genome/population/etc.) | `src/data/release-*.json` | JSON | Manual edit |
| Genetic Resources | `src/data/genetic-*.json` | JSON | Automatic (GitHub Actions) |
| Sampling map markers | `src/data/sampling-markers.json` | JSON | Manual edit |
| Translations | `src/i18n/{en,pt}.json` | JSON | Manual edit |

---

## 1. Adding a New Event

Events use Astro Content Collections. Each event needs **two files** (EN + PT).

### File naming convention
```
src/content/events/{category}-{slug}-{locale}.md
```
Example: `sampling-tavira-en.md` and `sampling-tavira-pt.md`

### Template (copy and edit)
```yaml
---
title: "Sampling at Tavira, Algarve"
date: "2026-03-15"
category: sampling          # sampling | experiment | dissemination | conference | workshop
locale: en                  # en | pt
description: "R. decussatus: 30 farm individuals"
image: "/BivalvePlus_web/images/events/tavira.jpg"   # optional
lat: 37.1275                # required for sampling events (map marker)
lng: -7.6506
siteLabel: "Tavira, Algarve"
---

Event details here in Markdown.
```

### For sampling events — also add map marker
Edit `src/data/sampling-markers.json` and add:
```json
{
  "lat": 37.1275,
  "lng": -7.6506,
  "species": "r_decussatus",
  "label": "Tavira, Algarve",
  "region": "Algarve",
  "count": "30",
  "date": "2026-03-15"
}
```

Species keys: `ostreidae`, `mytilus`, `r_decussatus`, `r_philippinarum`

### After adding
```bash
npm run build    # verify no errors
git add src/content/events/ src/data/sampling-markers.json
git commit -m "feat: add Tavira sampling event"
git push
```

---

## 2. Adding Release Data

Release data is stored in `src/data/release-*.json`. Each file has a `rows` array.

### Genome / Population Genome / Other Genetic Resources
Edit the corresponding JSON file and add rows to the `rows` array.

### Publications
Edit `src/data/release-publications.json`:
```json
{
  "title": "Paper title here",
  "authors": "Author A, Author B",
  "journal": "Journal Name",
  "year": "2026",
  "doi": "10.1234/example",
  "link": "https://doi.org/10.1234/example"
}
```

### Suggestions & Strategy
Edit `src/data/release-suggestions.json`:
```json
{
  "title": "Strategy document title",
  "description": "Brief description",
  "pdf": "/BivalvePlus_web/files/strategy-doc.pdf"
}
```
Place PDF files in `public/files/`.

---

## 3. Genetic Resources (Automatic)

Handled by GitHub Actions — runs every Monday at 06:00 UTC.

### Manual trigger
1. Go to repo > Actions > "Update Genetic Resources Data"
2. Click "Run workflow"

### Modifying the collector
Edit `scripts/collect_genetic_data.py`:
- Add species: update `SPECIES` dict with new TaxID
- Add markers: update `MARKERS` dict
- Change APIs: modify the `collect_*` functions

After changes:
```bash
# Test locally first
cd /mnt/d/AI_projects/BivalvePlus_project_webpage/bivalveplus-site
pip install -r scripts/requirements.txt
python scripts/collect_genetic_data.py

# Verify output
ls -la src/data/genetic-*.json

# Commit and push
git add scripts/ src/data/genetic-*.json
git commit -m "chore: update genetic data collector"
git push
```

---

## 4. Updating Translations

Edit `src/i18n/en.json` and `src/i18n/pt.json`.

Both files must have identical key structure. If you add a key to `en.json`, add the Portuguese translation to `pt.json`.

---

## 5. Updating Images

Place images in `public/images/` with appropriate subdirectories:
- `public/images/events/` — event photos
- `public/images/team/` — team member photos
- `public/images/backgrounds/` — page backgrounds
- `public/images/species/` — species illustrations

Reference in code as: `/BivalvePlus_web/images/events/photo.jpg`

---

## 6. Decap CMS Setup

Decap CMS provides a browser-based editor at `/admin/` for managing Events content.

### Prerequisites
- Site deployed to GitHub Pages
- GitHub OAuth App registered

### Step 1 — Register GitHub OAuth App

1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - Application name: `BivalvePlus CMS`
   - Homepage URL: `https://maoxiaopeng1991-source.github.io/BivalvePlus_web/`
   - Authorization callback URL: `https://api.netlify.com/auth/done`
4. Click "Register application"
5. Copy the **Client ID**
6. Generate and copy the **Client Secret**

### Step 2 — Set Up Netlify for OAuth Proxy

Decap CMS needs an OAuth proxy. The simplest free option is Netlify:

1. Go to https://app.netlify.com/ and sign up (free)
2. Create a new site (can be an empty placeholder site)
3. Go to Site settings > Access control > OAuth
4. Under "Authentication Providers", click "Install provider"
5. Select GitHub, paste your **Client ID** and **Client Secret**
6. Save

### Step 3 — Update CMS Config

Edit `public/admin/config.yml` line 4:
```yaml
  site_domain: your-netlify-site.netlify.app
```
Replace `your-netlify-site` with your actual Netlify site subdomain.

### Step 4 — Test

1. Push changes and wait for deploy
2. Visit `https://maoxiaopeng1991-source.github.io/BivalvePlus_web/admin/`
3. Click "Login with GitHub"
4. Authorize the app
5. You should see the Events content editor

### Using the CMS

- **Create**: Click "New Event" > fill in fields > Save > Publish
- **Edit**: Click an existing event > modify > Save
- **Delete**: Open event > click "Delete" in menu
- Each save creates a git commit in your repo automatically

---

## 7. Local Development

```bash
cd /mnt/d/AI_projects/BivalvePlus_project_webpage/bivalveplus-site

# Install dependencies
npm install

# Start dev server
npx astro dev --host 0.0.0.0

# Open in browser
# http://localhost:4321/BivalvePlus_web/en/

# Build for production
npm run build

# Preview production build
npm run preview
```

### Clear cache (if pages don't update)
```bash
rm -rf node_modules/.vite .astro dist
npx astro dev --host 0.0.0.0
```
Then hard-refresh browser: `Ctrl+Shift+R`
