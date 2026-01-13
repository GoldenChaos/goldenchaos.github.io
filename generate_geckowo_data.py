"""Generate geckowo comics and doodles data files for Eleventy"""
import json
from pathlib import Path

def load_captions(filename):
    """Load caption data"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_comics_data():
    """Generate geckowo comics data"""
    comics_dir = Path("geckowo_archive/comics")
    comics_files = sorted(comics_dir.glob("*.jpg"))
    captions = load_captions("geckowo_comic_captions.json")
    
    comics_data = []
    for i, comic_file in enumerate(comics_files, 1):
        post_id = comic_file.stem
        caption = captions.get(post_id)
        
        # Create comic entry
        comic = {
            "number": i,
            "slug": str(i),
            "title": caption if caption else "",
            "alt": f"Geckowo comic #{i}" + (f" - {caption}" if caption else ""),
            "image": f"/images/geckowo/comics/{comic_file.name}",
            "ogImage": f"/images/geckowo/comics/{comic_file.name}",
            "twitterImage": f"/images/geckowo/comics/{comic_file.name}",
            "postId": post_id
        }
        comics_data.append(comic)
    
    return comics_data

def generate_doodles_data():
    """Generate geckowo doodles data"""
    doodles_dir = Path("geckowo_archive/doodles")
    doodles_files = sorted(doodles_dir.glob("*.jpg"))
    captions = load_captions("geckowo_doodle_captions.json")
    
    doodles_data = []
    for i, doodle_file in enumerate(doodles_files, 1):
        post_id = doodle_file.stem
        caption = captions.get(post_id)
        
        # Create doodle entry
        doodle = {
            "number": i,
            "slug": str(i),
            "title": caption if caption else "",
            "alt": f"Geckowo doodle #{i}" + (f" - {caption}" if caption else ""),
            "image": f"/images/geckowo/doodles/{doodle_file.name}",
            "ogImage": f"/images/geckowo/doodles/{doodle_file.name}",
            "twitterImage": f"/images/geckowo/doodles/{doodle_file.name}",
            "postId": post_id
        }
        doodles_data.append(doodle)
    
    return doodles_data

if __name__ == "__main__":
    # Generate comics data
    comics_data = generate_comics_data()
    with open("src/_data/geckowo_comics.json", 'w', encoding='utf-8') as f:
        json.dump(comics_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Generated {len(comics_data)} geckowo comics entries")
    
    # Generate doodles data
    doodles_data = generate_doodles_data()
    with open("src/_data/geckowo_doodles.json", 'w', encoding='utf-8') as f:
        json.dump(doodles_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Generated {len(doodles_data)} geckowo doodles entries")
    
    print(f"\nTotal: {len(comics_data)} comics, {len(doodles_data)} doodles")
