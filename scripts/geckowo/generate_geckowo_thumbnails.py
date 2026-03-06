from PIL import Image
import os

MAX_DIM = 500


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def fit_within_max(width: int, height: int, max_dim: int = MAX_DIM) -> tuple[int, int]:
    if width <= max_dim and height <= max_dim:
        return width, height
    aspect = width / height
    if aspect >= 1:
        new_width = max_dim
        new_height = int(round(max_dim / aspect))
    else:
        new_height = max_dim
        new_width = int(round(max_dim * aspect))
    return new_width, new_height


def process_directory(input_dir: str, output_dir: str) -> None:
    ensure_dir(output_dir)
    for filename in sorted(os.listdir(input_dir)):
        lower = filename.lower()
        if not lower.endswith(".jpg") or lower.endswith("-thumb.jpg"):
            continue
        input_path = os.path.join(input_dir, filename)
        if not os.path.isfile(input_path):
            continue

        with Image.open(input_path) as img:
            img = img.convert("RGB")
            new_width, new_height = fit_within_max(img.width, img.height)
            thumb = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            base_name, _ = os.path.splitext(filename)
            output_path = os.path.join(output_dir, f"{base_name}-thumb.jpg")
            thumb.save(
                output_path,
                "JPEG",
                quality=85,
                optimize=True,
                progressive=True,
                subsampling=2,
            )
            print(f"Created: {output_path} ({new_width}x{new_height}px, fits within {MAX_DIM}x{MAX_DIM})")


def main() -> None:
    targets = [
        ("images/geckowo/comics", "images/geckowo/comics/thumb"),
        ("images/geckowo/doodles", "images/geckowo/doodles/thumb"),
    ]
    for input_dir, output_dir in targets:
        if not os.path.exists(input_dir):
            print(f"Skip: {input_dir} does not exist")
            continue
        process_directory(input_dir, output_dir)


if __name__ == "__main__":
    main()
