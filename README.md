# GoldenChaos Portfolio Site

Static portfolio site built with [Eleventy](https://www.11ty.dev/) using Nunjucks templates.

## Development

### Prerequisites
- Node.js and npm installed

### Commands

```bash
# Build the site
npm run build

# Start development server with live reload
npm run dev
```

The dev server runs at `http://localhost:8080/`

## Project Structure

```
src/
  _data/           # Global data files
    site.json      # Site metadata, social links
    redirects.json # URL redirect mappings
  _includes/       # Templates and partials
    layouts/
      base.njk     # Base HTML layout
      project.njk  # Project page layout with hero/meta
    head.njk       # Shared <head> partial
    nav.njk        # Shared navigation partial
  *.njk            # Page templates
_site/             # Generated output (git-ignored)
```

## Templating

### Pages Migrated to Eleventy (17/17)

✅ **Fully Templated:**
- Home page (`index.njk`)
- Squareknot (`squareknot.njk`)
- Crossbeam (`crossbeam.njk`)
- GoodSemester (`goodsemester.njk`)  
- CollX (`collx.njk`)
- Zelda Universe (`zelda-universe.njk`)
- Zelda Wiki (`zelda-wiki.njk`)
- Zelda Maps (`zelda-maps.njk`)
- ZodTTD Icons (`zodttd-icons.njk`)
- FacePorts (`faceports.njk`)
- GoldenChaos-BTT (`goldenchaos-btt.njk`)
- Compare (`compare.njk`)
- Desktop Icons (`desktop-icons.njk`)
- Master Sword (`master-sword.njk`)
- The Jason Effect (`the-jason-effect.njk`)
- Venti (`venti.njk`)
- GoldenChaos-BTT Docs (`goldenchaos-btt-docs.njk`)
- GoldenChaos-BTT SDK (`goldenchaos-btt-sdk.njk`)

These pages use the templating system with shared nav/head partials and have clean folder URLs (e.g., `/squareknot/`). Old `.html` URLs automatically redirect to folder URLs.

## URL Structure

- **Templated pages:** `/project-name/` (e.g., `/squareknot/`)
- **Legacy pages:** none
- **Redirects:** Old URLs automatically redirect to new ones

## Future Migrations

To migrate remaining pages to templates:

1. Create `src/pagename.njk` using `project.njk` layout
2. Add front matter (title, slug, permalink, heroMeta, etc.)
3. Copy page content (no head/nav/footer - handled by layout)
4. Update image paths to be absolute (`/images/...`)
5. Remove page from `.eleventy.js` passthrough
6. Update `redirects.json` to redirect `.html` → `/folder/`
7. Rebuild and test

## Deployment

Build output is in `_site/` directory. Deploy this folder to your web host.

---

*Site built with ❤️ by Jess Rappaport*
