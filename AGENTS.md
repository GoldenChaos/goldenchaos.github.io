# Local preview

Before beginning website work, check whether the local site is responding at `http://localhost:8080/`. If it is not running, start the Eleventy development server on port 8080 and confirm the site responds before making changes.

# Comic thumbnails

When adding a comic, inspect its panel layout before generating the archive entry. Two-panel comics with panels stacked vertically should set `thumbPosition` to `top` in their `src/comics-data` record so the archive thumbnail is cropped from the top rather than the center. Do not apply this treatment to two-panel comics whose panels are arranged side by side.
