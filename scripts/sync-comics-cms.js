const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const repoDir = path.join(__dirname, "..");
const comicsDir = path.join(repoDir, "src", "comics-data");
const dataDir = path.join(__dirname, "..", "src", "_data");
const imageScript = path.join(__dirname, "sync_comic_images.py");

const tasks = [
  {
    cmsFile: "geckowo_comics.cms.json",
    cmsKey: "items",
    outputFile: "geckowo_comics.json",
  },
  {
    cmsFile: "geckowo_doodles.cms.json",
    cmsKey: "items",
    outputFile: "geckowo_doodles.json",
  },
];

const pythonCommand = process.platform === "win32" ? "py" : "python3";

function fail(message) {
  console.error(`[sync-cms-data] ${message}`);
  process.exit(1);
}

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (error) {
    fail(`Invalid JSON in ${path.basename(filePath)}: ${error.message}`);
  }
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

function runPy(args) {
  let result = spawnSync(pythonCommand, args, {
    cwd: repoDir,
    encoding: "utf8",
  });

  // Fallback for environments where python3 is not available but python is.
  if (process.platform !== "win32" && result.error && result.error.code === "ENOENT") {
    result = spawnSync("python", args, {
      cwd: repoDir,
      encoding: "utf8",
    });
  }

  if (result.status !== 0) {
    const stderr = (result.stderr || "").trim();
    const stdout = (result.stdout || "").trim();
    const usedCommand = process.platform === "win32" ? "py" : (result.error && result.error.code === "ENOENT" ? "python" : pythonCommand);
    fail(`Python command failed: ${usedCommand} ${args.join(" ")}\n${stderr || stdout}`);
  }
}

function toFsPath(publicPath) {
  return path.join(repoDir, publicPath.replace(/^\//, ""));
}

function cleanImagePath(value) {
  if (typeof value !== "string") {
    return value;
  }
  return value
    .replace(/[\u0000-\u001F\u007F-\u009F\u200B-\u200D\uFEFF]/g, "")
    .trim();
}

function cleanFileStem(stem) {
  if (typeof stem !== "string") {
    return stem;
  }
  return stem
    .replace(/[<>:"/\\|?*\u0000-\u001F]/g, "")
    .trim();
}

function deriveComicImagePaths(comic) {
  comic.image = cleanImagePath(comic.image);
  if (typeof comic.image !== "string" || !comic.image.startsWith("/images/comics/")) {
    return false;
  }

  const sourcePath = toFsPath(comic.image);
  if (!fs.existsSync(sourcePath)) {
    console.warn(`[sync-cms-data] Comic image not found on disk: ${comic.image}`);
    return false;
  }

  runPy([imageScript, "--mode", "normal", "--source", sourcePath]);

  const basename = cleanFileStem(path.parse(comic.image).name);
  const thumbImage = `/images/comics/thumb/${basename}-thumb.png`;
  const ogImage = `/images/comics/og/${basename}-og.png`;

  let changed = false;
  if (comic.thumbImage !== thumbImage) {
    comic.thumbImage = thumbImage;
    changed = true;
  }
  if (comic.ogImage !== ogImage) {
    comic.ogImage = ogImage;
    changed = true;
  }
  if (comic.twitterImage !== ogImage) {
    comic.twitterImage = ogImage;
    changed = true;
  }

  return changed;
}

function deriveBaldImagePaths(comic) {
  comic.baldImage = cleanImagePath(comic.baldImage);
  if (typeof comic.baldImage !== "string" || !comic.baldImage.startsWith("/images/comics/bald/")) {
    return false;
  }

  const sourcePath = toFsPath(comic.baldImage);
  if (!fs.existsSync(sourcePath)) {
    console.warn(`[sync-cms-data] Bald image not found on disk: ${comic.baldImage}`);
    return false;
  }

  runPy([imageScript, "--mode", "bald", "--source", sourcePath]);

  const basename = cleanFileStem(path.parse(comic.baldImage).name);
  const baldThumbImage = `/images/comics/bald/thumb/${basename}-thumb.png`;

  if (comic.baldThumbImage !== baldThumbImage) {
    comic.baldThumbImage = baldThumbImage;
    return true;
  }
  return false;
}

function syncComicDerivatives(parsed, recordsKey) {
  let changed = false;
  for (const comic of parsed[recordsKey]) {
    changed = deriveComicImagePaths(comic) || changed;
    changed = deriveBaldImagePaths(comic) || changed;
  }
  return changed;
}

function deriveGeckowoThumb(item, mode, prefix, thumbPrefix) {
  item.image = cleanImagePath(item.image);
  if (typeof item.image !== "string" || !item.image.startsWith(prefix)) {
    return false;
  }

  const sourcePath = toFsPath(item.image);
  if (!fs.existsSync(sourcePath)) {
    console.warn(`[sync-cms-data] Geckowo image not found on disk: ${item.image}`);
    return false;
  }

  runPy([imageScript, "--mode", mode, "--source", sourcePath]);
  const ext = path.extname(item.image);
  const basename = cleanFileStem(path.parse(item.image).name);
  const thumbImage = `${thumbPrefix}/${basename}-thumb${ext}`;

  if (item.thumbImage !== thumbImage) {
    item.thumbImage = thumbImage;
    return true;
  }
  return false;
}

function syncGeckowoThumbs(parsed, recordsKey, mode, prefix, thumbPrefix) {
  let changed = false;
  for (const item of parsed[recordsKey]) {
    changed = deriveGeckowoThumb(item, mode, prefix, thumbPrefix) || changed;
  }
  return changed;
}

function syncComicsFromDirectory() {
  if (!fs.existsSync(comicsDir)) {
    fail(`Missing ${comicsDir}`);
  }

  const files = fs.readdirSync(comicsDir)
    .filter((file) => file.toLowerCase().endsWith(".json"))
    .sort((a, b) => a.localeCompare(b));

  const comics = [];
  let updatedCount = 0;

  for (const file of files) {
    const filePath = path.join(comicsDir, file);
    const comic = readJson(filePath);

    const updated = deriveComicImagePaths(comic) || deriveBaldImagePaths(comic);
    if (updated) {
      writeJson(filePath, comic);
      updatedCount += 1;
    }

    comics.push(comic);
  }

  const sorted = comics
    .slice()
    .sort((a, b) => Number(a.number) - Number(b.number));

  writeJson(path.join(dataDir, "comics.json"), sorted);
  if (updatedCount > 0) {
    console.log(`[sync-cms-data] Updated comic derivative fields in ${updatedCount} comics-data files`);
  }
  console.log(`[sync-cms-data] Synced ${sorted.length} items to src/_data/comics.json`);
}

syncComicsFromDirectory();

for (const task of tasks) {
  const cmsPath = path.join(dataDir, task.cmsFile);
  const outPath = path.join(dataDir, task.outputFile);

  if (!fs.existsSync(cmsPath)) {
    fail(`Missing ${cmsPath}`);
  }

  const parsed = readJson(cmsPath);
  if (!parsed || !Array.isArray(parsed[task.cmsKey])) {
    fail(`Expected ${task.cmsFile} to have an array at key '${task.cmsKey}'.`);
  }

  if (task.cmsFile === "geckowo_comics.cms.json") {
    const updated = syncGeckowoThumbs(
      parsed,
      task.cmsKey,
      "geckowo_comics",
      "/images/geckowo/comics/",
      "/images/geckowo/comics/thumb",
    );
    if (updated) {
      writeJson(cmsPath, parsed);
      console.log("[sync-cms-data] Updated geckowo comic thumbnail fields in geckowo_comics.cms.json");
    }
  }
  if (task.cmsFile === "geckowo_doodles.cms.json") {
    const updated = syncGeckowoThumbs(
      parsed,
      task.cmsKey,
      "geckowo_doodles",
      "/images/geckowo/doodles/",
      "/images/geckowo/doodles/thumb",
    );
    if (updated) {
      writeJson(cmsPath, parsed);
      console.log("[sync-cms-data] Updated geckowo doodle thumbnail fields in geckowo_doodles.cms.json");
    }
  }

  const records = parsed[task.cmsKey]
    .slice()
    .sort((a, b) => Number(a.number) - Number(b.number));

  writeJson(outPath, records);
  console.log(`[sync-cms-data] Synced ${records.length} items to src/_data/${task.outputFile}`);
}
