from pathlib import Path
import argparse

from PIL import Image, ImageOps


THUMB_SIZE = (720, 720)
OG_SIZE = (1200, 630)
BACKGROUND = (255, 252, 248)


def output_options(source: Image.Image) -> dict:
    options = {"optimize": True}
    if "icc_profile" in source.info:
        options["icc_profile"] = source.info["icc_profile"]
    return options


def normalized(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image)
    return image.convert("RGBA") if image.mode in ("RGBA", "LA", "P") else image.convert("RGB")


def make_thumbnail(image: Image.Image, position: str) -> Image.Image:
    centering = (0.5, 0.0) if position == "top" else (0.5, 0.5)
    return ImageOps.fit(image, THUMB_SIZE, Image.Resampling.LANCZOS, centering=centering)


def make_social_image(image: Image.Image) -> Image.Image:
    canvas = Image.new("RGB", OG_SIZE, BACKGROUND)
    contained = ImageOps.contain(image.convert("RGB"), OG_SIZE, Image.Resampling.LANCZOS)
    x = (OG_SIZE[0] - contained.width) // 2
    y = (OG_SIZE[1] - contained.height) // 2
    canvas.paste(contained, (x, y))
    return canvas


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--thumb", required=True)
    parser.add_argument("--og", required=True)
    parser.add_argument("--position", choices=("center", "top"), default="center")
    args = parser.parse_args()

    source_path = Path(args.source)
    thumb_path = Path(args.thumb)
    og_path = Path(args.og)
    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    og_path.parent.mkdir(parents=True, exist_ok=True)

    source = Image.open(source_path)
    image = normalized(source)
    make_thumbnail(image, args.position).save(thumb_path, "PNG", **output_options(source))
    make_social_image(image).save(og_path, "PNG", **output_options(source))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

