from pathlib import Path
import argparse

from PIL import Image


THUMB_MAX = 500
OG_SIZE = (1200, 630)
OG_BG = (255, 255, 255)


def ensure_parent_dir(file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)


def resize_for_thumb(img: Image.Image) -> Image.Image:
    width, height = img.size
    aspect_ratio = width / height

    if aspect_ratio > 1:
        thumb_width = THUMB_MAX
        thumb_height = int(THUMB_MAX / aspect_ratio)
    else:
        thumb_height = THUMB_MAX
        thumb_width = int(THUMB_MAX * aspect_ratio)

    return img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)


def render_og(img: Image.Image) -> Image.Image:
    width, height = OG_SIZE
    if img.mode == "RGBA":
        canvas = Image.new("RGBA", OG_SIZE, OG_BG + (255,))
    else:
        canvas = Image.new(img.mode, OG_SIZE, OG_BG)

    original_ratio = img.width / img.height
    target_ratio = width / height

    if original_ratio > target_ratio:
        new_width = width
        new_height = int(width / original_ratio)
    else:
        new_height = height
        new_width = int(height * original_ratio)

    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    x_offset = (width - new_width) // 2
    y_offset = (height - new_height) // 2
    canvas.paste(resized, (x_offset, y_offset))
    return canvas


def derive_output_paths(source: Path, mode: str) -> tuple[Path, Path | None]:
    base_name = source.stem
    source_posix = source.as_posix()

    if mode == "normal":
        marker = "/images/comics/"
        if marker not in source_posix:
            raise ValueError("Normal comic image must be inside images/comics/")
        repo_root = source_posix.split(marker)[0]
        thumb = Path(f"{repo_root}/images/comics/thumb/{base_name}-thumb.png")
        og = Path(f"{repo_root}/images/comics/og/{base_name}-og.png")
        return thumb, og

    if mode == "geckowo_comics":
        marker = "/images/geckowo/comics/"
        if marker not in source_posix:
            raise ValueError("Geckowo comic image must be inside images/geckowo/comics/")
        repo_root = source_posix.split(marker)[0]
        thumb = Path(f"{repo_root}/images/geckowo/comics/thumb/{base_name}-thumb{source.suffix}")
        return thumb, None

    if mode == "geckowo_doodles":
        marker = "/images/geckowo/doodles/"
        if marker not in source_posix:
            raise ValueError("Geckowo doodle image must be inside images/geckowo/doodles/")
        repo_root = source_posix.split(marker)[0]
        thumb = Path(f"{repo_root}/images/geckowo/doodles/thumb/{base_name}-thumb{source.suffix}")
        return thumb, None

    marker = "/images/comics/bald/"
    if marker not in source_posix:
        raise ValueError("Bald comic image must be inside images/comics/bald/")
    repo_root = source_posix.split(marker)[0]
    thumb = Path(f"{repo_root}/images/comics/bald/thumb/{base_name}-thumb.png")
    return thumb, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["normal", "bald", "geckowo_comics", "geckowo_doodles"], required=True)
    parser.add_argument("--source", required=True)
    args = parser.parse_args()

    source = Path(args.source).resolve()
    if not source.exists():
        raise FileNotFoundError(f"Source image not found: {source}")

    thumb_path, og_path = derive_output_paths(source, args.mode)

    img = Image.open(source)
    thumb = resize_for_thumb(img)
    ensure_parent_dir(thumb_path)
    thumb_format = "PNG"
    thumb_kwargs = {"optimize": True}
    if source.suffix.lower() in [".jpg", ".jpeg"]:
        thumb_format = "JPEG"
        thumb_kwargs = {"quality": 90, "optimize": True}
        if thumb.mode in ("RGBA", "LA", "P"):
            thumb = thumb.convert("RGB")

    thumb.save(thumb_path, thumb_format, **thumb_kwargs)

    if args.mode == "normal" and og_path is not None:
        og = render_og(img)
        ensure_parent_dir(og_path)
        og_kwargs = {}
        if "icc_profile" in img.info:
            og_kwargs["icc_profile"] = img.info["icc_profile"]
        og.save(og_path, "PNG", **og_kwargs)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
