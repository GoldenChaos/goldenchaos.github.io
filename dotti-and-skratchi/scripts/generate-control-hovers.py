from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "src" / "assets" / "images"

COLORS = {
    "dotti": (255, 174, 201),   # #ffaec9, sampled from dotti.png
    "skratchi": (139, 216, 183),  # #8bd8b7, sampled from skratchi.png
}


def create_filled_variant(source_name: str, output_name: str, fill: tuple[int, int, int]) -> None:
    image = Image.open(ASSETS / source_name).convert("RGB")
    pixels = image.load()
    width, height = image.size
    outline = Image.new("L", image.size)
    outline_pixels = outline.load()
    for y in range(height):
        for x in range(width):
            red, green, blue = pixels[x, y]
            outline_pixels[x, y] = 255 if max(red, green, blue) < 190 else 0
    # Close tiny hand-drawn gaps before identifying the enclosed fill area.
    outline = outline.filter(ImageFilter.MaxFilter(5))
    outline_pixels = outline.load()

    def is_open(x: int, y: int) -> bool:
        red, green, blue = pixels[x, y]
        return red >= 235 and green >= 235 and blue >= 235

    outside = set()
    queue = deque()
    for x in range(width):
        queue.extend(((x, 0), (x, height - 1)))
    for y in range(height):
        queue.extend(((0, y), (width - 1, y)))

    while queue:
        x, y = queue.popleft()
        if (x, y) in outside or outline_pixels[x, y] != 0:
            continue
        outside.add((x, y))
        if x > 0:
            queue.append((x - 1, y))
        if x + 1 < width:
            queue.append((x + 1, y))
        if y > 0:
            queue.append((x, y - 1))
        if y + 1 < height:
            queue.append((x, y + 1))

    # Include every enclosed pocket so the small hand-drawn corner notches fill too.
    inside = {
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in outside and outline_pixels[x, y] == 0
    }

    fill_mask = Image.new("L", image.size)
    fill_mask_pixels = fill_mask.load()
    for x, y in inside:
        fill_mask_pixels[x, y] = 255
    # Grow back beneath the original black edge after sealing the tiny gaps.
    fill_mask = fill_mask.filter(ImageFilter.MaxFilter(5))
    fill_mask_pixels = fill_mask.load()
    for y in range(height):
        for x in range(width):
            if is_open(x, y) and fill_mask_pixels[x, y]:
                pixels[x, y] = fill

    image.save(ASSETS / output_name, optimize=True)


create_filled_variant("control-oldest.png", "control-oldest-dotti.png", COLORS["dotti"])
create_filled_variant("control-previous.png", "control-previous-dotti.png", COLORS["dotti"])
create_filled_variant("control-oldest.png", "control-oldest-skratchi.png", COLORS["skratchi"])
create_filled_variant("control-previous.png", "control-previous-skratchi.png", COLORS["skratchi"])
