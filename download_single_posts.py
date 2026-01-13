"""Quick script to download single posts with provided URLs"""
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO

def download_image(url: str, output_path: Path) -> bool:
    """Download image from URL"""
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        
        img = Image.open(BytesIO(resp.content))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.save(output_path, 'JPEG', quality=95)
        print(f"✓ Downloaded: {output_path.name}")
        return True
    except Exception as e:
        print(f"✗ Failed {output_path.name}: {e}")
        return False

# Download new comic
comics_dir = Path("geckowo_archive/comics")
comics_dir.mkdir(parents=True, exist_ok=True)

comic_url = "https://pbs.twimg.com/media/GvzQBPrXEAAVpRy?format=jpg&name=900x900"
comic_path = comics_dir / "1944657861360939304.jpg"

if not comic_path.exists():
    download_image(comic_url, comic_path)
else:
    print(f"Skipped: {comic_path.name} (already exists)")

# Download new doodle
doodles_dir = Path("geckowo_archive/doodles")
doodles_dir.mkdir(parents=True, exist_ok=True)

doodle_url = "https://pbs.twimg.com/media/Gob1zsFXkAAmKmt?format=jpg&name=large"
doodle_path = doodles_dir / "1911485363702419697.jpg"

if not doodle_path.exists():
    download_image(doodle_url, doodle_path)
else:
    print(f"Skipped: {doodle_path.name} (already exists)")

# Download repost with corrected name
repost_url = "https://pbs.twimg.com/media/G6IOpv4XYAAgYdy?format=jpg&name=large"
repost_path = comics_dir / "1975166690984915229.jpg"

if not repost_path.exists():
    download_image(repost_url, repost_path)
else:
    print(f"Skipped: {repost_path.name} (already exists)")

print("\nDone!")
