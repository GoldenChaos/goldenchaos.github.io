"""Copy geckowo images to the images directory for the site"""
import shutil
from pathlib import Path

def copy_images():
    # Ensure destination directories exist
    comics_dest = Path("images/geckowo/comics")
    doodles_dest = Path("images/geckowo/doodles")
    
    comics_dest.mkdir(parents=True, exist_ok=True)
    doodles_dest.mkdir(parents=True, exist_ok=True)
    
    # Copy comics
    comics_src = Path("geckowo_archive/comics")
    comic_count = 0
    for img in comics_src.glob("*.jpg"):
        dest_file = comics_dest / img.name
        shutil.copy2(img, dest_file)
        comic_count += 1
    
    print(f"✓ Copied {comic_count} comic images to {comics_dest}")
    
    # Copy doodles
    doodles_src = Path("geckowo_archive/doodles")
    doodle_count = 0
    for img in doodles_src.glob("*.jpg"):
        dest_file = doodles_dest / img.name
        shutil.copy2(img, dest_file)
        doodle_count += 1
    
    print(f"✓ Copied {doodle_count} doodle images to {doodles_dest}")
    print(f"\nTotal: {comic_count + doodle_count} images copied")

if __name__ == "__main__":
    copy_images()
