# Dotti & Skratchi

A standalone Eleventy comic site with a browser-based Decap CMS, automatic comic derivatives, and GitHub Pages deployment.

This folder is intentionally self-contained. It can be moved wholesale into its own GitHub repository when it is ready.

## Local setup

```bash
npm install
npm run setup:images
```

Run the site and admin proxy in separate terminals:

```bash
npm run dev
```

```bash
npm run admin
```

- Site: <http://localhost:8082/dotti-and-skratchi/>
- Admin: <http://localhost:8082/dotti-and-skratchi/admin/>

## Publishing a comic locally

1. Open the admin URL and choose **Comics → New Comic**.
2. Enter the comic number, ID, URL name, title, date, image description, and main image.
3. Choose the panel layout. Vertically stacked two-panel comics automatically use a top-aligned archive crop.
4. Add optional hover text or a caption.
5. Publish the entry.

The sync step creates:

- A square archive thumbnail in `images/comics/thumb/`.
- A 1200×630 social preview in `images/comics/og/`.
- The aggregate Eleventy data file at `src/_data/comics.json`.

Embedded ICC color profiles are retained in generated PNGs.

## Moving to Shelley’s repository

1. Move the contents of this folder to the root of a new repository.
2. Run `npm install` so `package-lock.json` is committed.
3. Replace `REPLACE_WITH_OWNER/REPLACE_WITH_REPOSITORY` in `src/admin/config.yml`.
4. Replace the placeholder URL and description in `src/_data/site.json`.
5. In the repository’s **Settings → Pages**, choose **GitHub Actions** as the source.
6. Configure production CMS authentication. Decap Turbo is the lowest-maintenance option; Netlify Identity with Git Gateway or a GitHub OAuth proxy also work.
7. Add the production authentication fields to `src/admin/config.yml`.

The CMS is configured for `editorial_workflow`: Shelley can submit a comic for review, and publishing merges its pull request before Pages deploys it.

## Important files

- `src/admin/config.yml`: fields Shelley sees in the CMS.
- `src/_data/site.json`: site name, description, URL, and future brand settings.
- `src/assets/style.css`: the visual system.
- `scripts/sync-comics.mjs`: comic records and derivative paths.
- `scripts/generate-images.py`: thumbnail/social-image generation.
- `.github/workflows/deploy-pages.yml`: cloud build and deployment.

