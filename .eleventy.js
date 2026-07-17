const sass = require('sass');
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

// Compile SCSS before module exports
function compileSass() {
  try {
    const result = sass.renderSync({
      file: './style.scss',
      outputStyle: "expanded"
    });
    const css = result.css.toString();
    
    // Write to root
    fs.writeFileSync('./style.css', css, { encoding: 'utf-8' });
    
    // Write to _site only if it exists
    if (fs.existsSync('./_site')) {
      fs.writeFileSync('./_site/style.css', css, { encoding: 'utf-8' });
    }
    console.log('[11ty] SCSS compiled to style.css');
  } catch(err) {
    console.error('SCSS compilation error:', err);
  }
}

function syncComicsData() {
  if (process.env.ELEVENTY_AUTO_SYNC !== "true") {
    return;
  }

  const scriptPath = path.join(__dirname, "scripts", "sync-comics-cms.js");
  const result = spawnSync("node", [scriptPath], {
    cwd: __dirname,
    encoding: "utf8"
  });

  if (result.status !== 0) {
    const stderr = (result.stderr || "").trim();
    const stdout = (result.stdout || "").trim();
    throw new Error(`sync-comics-cms.js failed:\n${stderr || stdout}`);
  }
}

// Initial compilation
compileSass();

module.exports = function(eleventyConfig) {
  const includeAdmin = process.env.ELEVENTY_INCLUDE_ADMIN === "true";

  // Watch SCSS files for changes and recompile
  eleventyConfig.addWatchTarget("*.scss");
  eleventyConfig.addWatchTarget("src/comics-data");
  eleventyConfig.addWatchTarget("src/geckowo-comics-data");
  eleventyConfig.addWatchTarget("src/geckowo-doodles-data");
  eleventyConfig.on("eleventy.before", () => {
    syncComicsData();
    compileSass();
  });

  // RSS-friendly date filter using RFC-1123 format
  eleventyConfig.addFilter("rssDate", (value) => {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toUTCString();
  });

  // Static assets passthrough
  eleventyConfig.addPassthroughCopy("images");
  eleventyConfig.addPassthroughCopy("fonts");
  eleventyConfig.addPassthroughCopy("og-image.png");
  eleventyConfig.addPassthroughCopy("apple-touch-icon-precomposed.png");
  eleventyConfig.addPassthroughCopy("favicon.ico");
  eleventyConfig.addPassthroughCopy("favicon-light.ico");
  eleventyConfig.addPassthroughCopy("favicon-dark.ico");
  eleventyConfig.addPassthroughCopy("CNAME");
  eleventyConfig.addPassthroughCopy({ "src/manifest.webmanifest": "manifest.webmanifest" });
  eleventyConfig.addPassthroughCopy({ "src/OneSignalSDKWorker.js": "OneSignalSDKWorker.js" });
  eleventyConfig.addPassthroughCopy({ "src/OneSignalSDKUpdaterWorker.js": "OneSignalSDKUpdaterWorker.js" });
  if (includeAdmin) {
    eleventyConfig.addPassthroughCopy({ "src/admin": "admin" });
  }
  eleventyConfig.addPassthroughCopy({
    "goldenchaos-btt-docs.html": "goldenchaos-btt-docs.html",
    "goldenchaos-btt-sdk.html": "goldenchaos-btt-sdk.html",
    "master-sword.html": "master-sword.html",
    "the-jason-effect.html": "the-jason-effect.html",
    "venti.html": "venti.html"
  });

  return {
    cleanOutputDir: true,
    ignores: includeAdmin ? [] : ["admin/**"],
    dir: {
      input: "src",
      includes: "_includes",
      data: "_data",
      output: "_site"
    }
  };
};
