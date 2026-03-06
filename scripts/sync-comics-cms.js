const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const repoDir = path.join(__dirname, "..");
const comicsDir = path.join(repoDir, "src", "comics-data");
const dataDir = path.join(__dirname, "..", "src", "_data");
const imageScript = path.join(__dirname, "sync_comic_images.py");

const geckowoTasks = [
  {
    name: "geckowo_comics",
    sourceDir: path.join(repoDir, "src", "geckowo-comics-data"),
    legacyCmsFile: "geckowo_comics.cms.json",
    outputFile: "geckowo_comics.json",
    mode: "geckowo_comics",
    prefix: "/images/geckowo/comics/",
    thumbPrefix: "/images/geckowo/comics/thumb",
  },
  {
    name: "geckowo_doodles",
    sourceDir: path.join(repoDir, "src", "geckowo-doodles-data"),
    legacyCmsFile: "geckowo_doodles.cms.json",
    outputFile: "geckowo_doodles.json",
    mode: "geckowo_doodles",
    prefix: "/images/geckowo/doodles/",
    thumbPrefix: "/images/geckowo/doodles/thumb",
  },
];
const twitterEpochMs = 1288834974657n;

const pythonCommand = process.platform === "win32" ? "py" : "python3";
const skipImageDerivatives = process.env.SYNC_SKIP_IMAGE_DERIVATIVES === "true";
let skipNoticePrinted = false;

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
  const next = `${JSON.stringify(data, null, 2)}\n`;
  if (fs.existsSync(filePath)) {
    const prev = fs.readFileSync(filePath, "utf8");
    if (prev === next) {
      return false;
    }
  }
  fs.writeFileSync(filePath, next, "utf8");
  return true;
}

function runPy(args) {
  if (skipImageDerivatives) {
    if (!skipNoticePrinted) {
      console.log("[sync-cms-data] Skipping image derivative generation (SYNC_SKIP_IMAGE_DERIVATIVES=true)");
      skipNoticePrinted = true;
    }
    return;
  }

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

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function listJsonFiles(dirPath) {
  if (!fs.existsSync(dirPath)) {
    return [];
  }
  return fs.readdirSync(dirPath)
    .filter((file) => file.toLowerCase().endsWith(".json"))
    .sort((a, b) => a.localeCompare(b));
}

function cleanFilename(value) {
  const cleaned = String(value || "")
    .trim()
    .replace(/[<>:"/\\|?*\u0000-\u001F]/g, "");
  return cleaned || "item";
}

function toRecordFilename(item) {
  const base = item.slug || numberToSlug(item.number) || "item";
  return `${cleanFilename(base)}.json`;
}

function numberToSlug(value) {
  if (value === undefined || value === null) {
    return "";
  }

  const raw = String(value).trim();
  if (!raw) {
    return "";
  }

  return raw.replace(/\./g, "-");
}

function isSameValue(a, b) {
  return String(a || "").trim() === String(b || "").trim();
}

function slugifyText(value) {
  if (typeof value !== "string") {
    return "";
  }

  return value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/['"]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function ensureComicSlugs(comic) {
  let changed = false;

  const fallbackComicId = numberToSlug(comic.number);
  const comicId = typeof comic.comicId === "string" && comic.comicId.trim()
    ? comic.comicId.trim()
    : (typeof comic.slugNumeric === "string" && comic.slugNumeric.trim()
      ? comic.slugNumeric.trim()
      : (typeof comic.slug === "string" && comic.slug.trim() && !comic.slug.includes("-")
        ? comic.slug.trim()
        : fallbackComicId));

  if (comicId && comic.comicId !== comicId) {
    comic.comicId = comicId;
    changed = true;
  }

  let semanticPart = "";
  if (typeof comic.slug === "string" && comic.slug.trim() && !isSameValue(comic.slug, comicId)) {
    semanticPart = comic.slug.trim();
  } else if (typeof comic.slugSemantic === "string" && comic.slugSemantic.trim()) {
    const full = comic.slugSemantic.trim();
    if (full.startsWith(`${comicId}-`)) {
      semanticPart = full.slice(comicId.length + 1);
    }
  }
  if (!semanticPart) {
    semanticPart = slugifyText(comic.title) || "comic";
  }
  semanticPart = slugifyText(semanticPart) || "comic";

  if (comic.slug !== semanticPart) {
    comic.slug = semanticPart;
    changed = true;
  }

  if (comic.slugNumeric !== undefined) {
    delete comic.slugNumeric;
    changed = true;
  }
  if (comic.slugSemantic !== undefined) {
    delete comic.slugSemantic;
    changed = true;
  }
  if (comic.slugLegacy !== undefined) {
    delete comic.slugLegacy;
    changed = true;
  }

  return changed;
}

function ensureTooltipText(comic) {
  if (comic.titleText === undefined && typeof comic.alt === "string" && comic.alt.trim().length > 0) {
    comic.titleText = comic.alt;
    return true;
  }
  return false;
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

  const basename = cleanFileStem(path.parse(comic.image).name);
  const thumbImage = `/images/comics/thumb/${basename}-thumb.png`;
  const ogImage = `/images/comics/og/${basename}-og.png`;
  const thumbPath = toFsPath(thumbImage);
  const ogPath = toFsPath(ogImage);

  if (!fs.existsSync(thumbPath) || !fs.existsSync(ogPath)) {
    runPy([imageScript, "--mode", "normal", "--source", sourcePath]);
  }

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

  const basename = cleanFileStem(path.parse(comic.baldImage).name);
  const baldThumbImage = `/images/comics/bald/thumb/${basename}-thumb.png`;
  const baldThumbPath = toFsPath(baldThumbImage);

  if (!fs.existsSync(baldThumbPath)) {
    runPy([imageScript, "--mode", "bald", "--source", sourcePath]);
  }

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

  const ext = path.extname(item.image);
  const basename = cleanFileStem(path.parse(item.image).name);
  const thumbImage = `${thumbPrefix}/${basename}-thumb${ext}`;
  const thumbPath = toFsPath(thumbImage);

  if (!fs.existsSync(thumbPath)) {
    runPy([imageScript, "--mode", mode, "--source", sourcePath]);
  }

  if (item.thumbImage !== thumbImage) {
    item.thumbImage = thumbImage;
    return true;
  }
  return false;
}

function ensureGeckowoSummaryTitle(item) {
  const title = typeof item.title === "string" ? item.title.trim() : "";
  const summaryTitle = title ? ` - ${title}` : "";
  if (item.summaryTitle !== summaryTitle) {
    item.summaryTitle = summaryTitle;
    return true;
  }
  return false;
}

function dateOnlyToIso(dateOnly) {
  if (typeof dateOnly !== "string") {
    return "";
  }
  const trimmed = dateOnly.trim();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
    return "";
  }
  return `${trimmed}T00:00:00.000Z`;
}

function deriveIsoFromTwitterPostId(postId) {
  const value = String(postId || "").trim();
  if (!/^\d+$/.test(value)) {
    return "";
  }
  try {
    const tweetId = BigInt(value);
    const timestampMs = Number((tweetId >> 22n) + twitterEpochMs);
    if (!Number.isFinite(timestampMs) || timestampMs <= 0) {
      return "";
    }
    return new Date(timestampMs).toISOString();
  } catch {
    return "";
  }
}

function loadGeckowoComicPublishDates() {
  const map = new Map();
  const metadataPath = path.join(repoDir, "data", "geckowo", "geckowo_comics_metadata.json");
  if (!fs.existsSync(metadataPath)) {
    return map;
  }

  const metadata = readJson(metadataPath);
  if (!Array.isArray(metadata)) {
    return map;
  }

  for (const item of metadata) {
    const id = String(item.status_id || "").trim();
    if (!id) {
      continue;
    }
    let isoFromTimestamp = "";
    if (typeof item.timestamp === "string" && item.timestamp.trim()) {
      const ts = item.timestamp.trim();
      const parsed = new Date(ts.endsWith("Z") ? ts : `${ts}Z`);
      if (!Number.isNaN(parsed.getTime())) {
        isoFromTimestamp = parsed.toISOString();
      }
    }
    const isoFromDate = dateOnlyToIso(item.date);
    map.set(id, isoFromTimestamp || isoFromDate || "");
  }

  return map;
}

function ensureGeckowoPublishDate(item, taskName, comicsDateMap) {
  const current = typeof item.date === "string" ? item.date.trim() : "";
  const postId = String(item.postId || "").trim();

  let next = "";
  if (taskName === "geckowo_comics" && postId && comicsDateMap.has(postId)) {
    next = comicsDateMap.get(postId) || "";
  }
  if (!next && current) {
    // Keep existing curated/manual date values when no authoritative comics metadata exists.
    return false;
  }
  if (!next && postId) {
    next = deriveIsoFromTwitterPostId(postId);
  }
  if (!next && current) {
    next = dateOnlyToIso(current) || current;
  }

  if (!next) {
    return false;
  }
  if (current !== next) {
    item.date = next;
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

function migrateLegacyGeckowoCms(task) {
  const legacyPath = path.join(dataDir, task.legacyCmsFile);
  if (!fs.existsSync(legacyPath)) {
    return 0;
  }

  const parsed = readJson(legacyPath);
  if (!parsed || !Array.isArray(parsed.items)) {
    fail(`Expected ${task.legacyCmsFile} to have an array at key 'items'.`);
  }

  ensureDir(task.sourceDir);

  let created = 0;
  for (const item of parsed.items) {
    const filePath = path.join(task.sourceDir, toRecordFilename(item));
    if (!fs.existsSync(filePath)) {
      writeJson(filePath, item);
      created += 1;
    }
  }

  return created;
}

function syncGeckowoCollection(task) {
  ensureDir(task.sourceDir);
  let files = listJsonFiles(task.sourceDir);

  if (files.length === 0) {
    const created = migrateLegacyGeckowoCms(task);
    if (created > 0) {
      console.log(`[sync-cms-data] Migrated ${created} ${task.name} entries to ${path.relative(repoDir, task.sourceDir)}`);
    }
    files = listJsonFiles(task.sourceDir);
  }

  const records = [];
  let updatedCount = 0;
  const comicsDateMap = loadGeckowoComicPublishDates();

  for (const file of files) {
    const filePath = path.join(task.sourceDir, file);
    const item = readJson(filePath);
    let updated = false;
    updated = ensureGeckowoSummaryTitle(item) || updated;
    updated = ensureGeckowoPublishDate(item, task.name, comicsDateMap) || updated;
    updated = deriveGeckowoThumb(item, task.mode, task.prefix, task.thumbPrefix) || updated;
    if (updated) {
      if (writeJson(filePath, item)) {
        updatedCount += 1;
      }
    }
    records.push(item);
  }

  const sorted = records
    .slice()
    .sort((a, b) => Number(a.number) - Number(b.number));

  const outPath = path.join(dataDir, task.outputFile);
  if (writeJson(outPath, sorted)) {
    console.log(`[sync-cms-data] Synced ${sorted.length} items to src/_data/${task.outputFile}`);
  }

  const legacyPath = path.join(dataDir, task.legacyCmsFile);
  writeJson(legacyPath, { items: sorted });

  if (updatedCount > 0) {
    console.log(`[sync-cms-data] Updated thumbnail fields in ${updatedCount} ${task.name} files`);
  }
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

    let updated = false;
    updated = ensureComicSlugs(comic) || updated;
    updated = ensureTooltipText(comic) || updated;
    updated = deriveComicImagePaths(comic) || updated;
    updated = deriveBaldImagePaths(comic) || updated;
    if (updated) {
      if (writeJson(filePath, comic)) {
        updatedCount += 1;
      }
    }

    comics.push(comic);
  }

  const sorted = comics
    .slice()
    .sort((a, b) => Number(a.number) - Number(b.number));

  const comicsDataUpdated = writeJson(path.join(dataDir, "comics.json"), sorted);
  if (updatedCount > 0) {
    console.log(`[sync-cms-data] Updated comic derivative fields in ${updatedCount} comics-data files`);
  }
  if (comicsDataUpdated) {
    console.log(`[sync-cms-data] Synced ${sorted.length} items to src/_data/comics.json`);
  }
}

syncComicsFromDirectory();

for (const task of geckowoTasks) {
  syncGeckowoCollection(task);
}
