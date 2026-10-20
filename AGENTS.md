# Local preview

Before beginning website work, check whether the local site is responding at `http://localhost:8080/`. If it is not running, start the Eleventy development server on port 8080 and confirm the site responds before making changes.

# UI styling

Follow the site's existing HTML and CSS component structure for UI changes unless the user explicitly requests a new treatment. Before adding or overriding styles, inspect the comparable existing UI and match its markup, selectors, dimensions, spacing, states, and responsive behavior. Avoid one-off component variants when an existing component already covers the requested design.

# Comic thumbnails

When adding a comic, inspect its panel layout before generating the archive entry. Two-panel comics with panels stacked vertically should set `thumbPosition` to `top` in their `src/comics-data` record so the archive thumbnail is cropped from the top rather than the center. Do not apply this treatment to two-panel comics whose panels are arranged side by side.
