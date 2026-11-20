const path = require("node:path");

module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });
  eleventyConfig.addPassthroughCopy({ "src/admin": "admin" });
  eleventyConfig.addPassthroughCopy({ "images": "images" });

  eleventyConfig.addFilter("readableDate", (value) => {
    if (!value) return "";
    return new Intl.DateTimeFormat("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
      timeZone: "UTC"
    }).format(new Date(value));
  });

  eleventyConfig.addFilter("previousComic", (comics, number) => {
    const index = comics.findIndex((comic) => String(comic.number) === String(number));
    return index > 0 ? comics[index - 1] : null;
  });

  eleventyConfig.addFilter("nextComic", (comics, number) => {
    const index = comics.findIndex((comic) => String(comic.number) === String(number));
    return index >= 0 && index < comics.length - 1 ? comics[index + 1] : null;
  });

  return {
    pathPrefix: "/dotti-and-skratchi/",
    dir: {
      input: "src",
      includes: "_includes",
      data: "_data",
      output: "_site"
    },
    templateFormats: ["njk", "html", "md"]
  };
};

