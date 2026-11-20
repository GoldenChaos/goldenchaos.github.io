import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const recordsDir = path.join(root, "src", "comics-data");
const outputFile = path.join(root, "src", "_data", "comics.json");
const imageScript = path.join(root, "scripts", "generate-images.py");

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function publicPathToFile(publicPath) {
  return path.join(root, String(publicPath).replace(/^\//, ""));
}

function pythonCommand() {
  const candidates = [
    process.env.SHELLEY_PYTHON,
    path.join(root, ".venv", "bin", "python"),
    "python3",
    "python"
  ].filter(Boolean);

  for (const command of candidates) {
    const check = spawnSync(command, ["-c", "from PIL import Image"], { stdio: "ignore" });
    if (check.status === 0) return command;
  }

  throw new Error("Pillow is required to generate comic images. Run: npm run setup:images");
}

function syncImages(comic) {
  if (!comic.image) return comic;
  const source = publicPathToFile(comic.image);
  if (!fs.existsSync(source)) {
    throw new Error(`Missing main image for comic ${comic.number}: ${comic.image}`);
  }

  const stem = path.parse(source).name;
  const thumbPublic = `/images/comics/thumb/${stem}-thumb.png`;
  const ogPublic = `/images/comics/og/${stem}-og.png`;
  const thumb = publicPathToFile(thumbPublic);
  const og = publicPathToFile(ogPublic);
  const position = comic.layout === "vertical-two-panel" ? "top" : "center";
  const sourceMtime = fs.statSync(source).mtimeMs;
  const needsBuild = [thumb, og].some((file) => !fs.existsSync(file) || fs.statSync(file).mtimeMs < sourceMtime);

  if (needsBuild) {
    const result = spawnSync(pythonCommand(), [
      imageScript,
      "--source", source,
      "--thumb", thumb,
      "--og", og,
      "--position", position
    ], { stdio: "inherit" });
    if (result.status !== 0) throw new Error(`Image generation failed for comic ${comic.number}`);
  }

  return {
    ...comic,
    thumbPosition: position,
    thumbImage: thumbPublic,
    ogImage: ogPublic,
    twitterImage: ogPublic
  };
}

fs.mkdirSync(recordsDir, { recursive: true });
const files = fs.readdirSync(recordsDir).filter((file) => file.endsWith(".json"));
const comics = files.map((file) => {
  const recordPath = path.join(recordsDir, file);
  const comic = syncImages(readJson(recordPath));
  writeJson(recordPath, comic);
  return comic;
}).sort((a, b) => Number(a.number) - Number(b.number));

const ids = new Set();
for (const comic of comics) {
  if (ids.has(String(comic.comicId))) throw new Error(`Duplicate comic ID: ${comic.comicId}`);
  ids.add(String(comic.comicId));
}

writeJson(outputFile, {
  all: comics,
  latest: comics.at(-1) ?? null
});

console.log(`[shelley-comics] Synced ${comics.length} comic${comics.length === 1 ? "" : "s"}.`);

