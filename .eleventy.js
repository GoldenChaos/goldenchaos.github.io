const sass = require('sass');
const fs = require('fs');

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

// Initial compilation
compileSass();

module.exports = function(eleventyConfig) {
  // Watch SCSS files for changes and recompile
  eleventyConfig.addWatchTarget("*.scss");
  eleventyConfig.on("eleventy.before", () => {
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
  eleventyConfig.addPassthroughCopy("CNAME");
  eleventyConfig.addPassthroughCopy({ "src/manifest.webmanifest": "manifest.webmanifest" });
  eleventyConfig.addPassthroughCopy({ "src/OneSignalSDKWorker.js": "OneSignalSDKWorker.js" });
  eleventyConfig.addPassthroughCopy({ "src/OneSignalSDKUpdaterWorker.js": "OneSignalSDKUpdaterWorker.js" });
  eleventyConfig.addPassthroughCopy({
    "goldenchaos-btt-docs.html": "goldenchaos-btt-docs.html",
    "goldenchaos-btt-sdk.html": "goldenchaos-btt-sdk.html",
    "master-sword.html": "master-sword.html",
    "the-jason-effect.html": "the-jason-effect.html",
    "venti.html": "venti.html"
  });

  return {
    dir: {
      input: "src",
      includes: "_includes",
      data: "_data",
      output: "_site"
    }
  };
};
