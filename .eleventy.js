module.exports = function(eleventyConfig) {
  // Static assets passthrough
  eleventyConfig.addPassthroughCopy("images");
  eleventyConfig.addPassthroughCopy("fonts");
  eleventyConfig.addPassthroughCopy("*.css");
  eleventyConfig.addPassthroughCopy("*.scss");
  eleventyConfig.addPassthroughCopy("og-image.png");
  eleventyConfig.addPassthroughCopy("CNAME");
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
