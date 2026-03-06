#!/usr/bin/env python3
"""
Download doodles with provided image URLs.
Handles single and multiple images per post.
"""

import os
from pathlib import Path
import requests
from PIL import Image

OUT_DIR = Path("geckowo_archive/doodles")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Image URLs by status ID (from user)
DOODLE_URLS = {
    "1964314103863705905": ["https://pbs.twimg.com/media/G0KlRCmXcAA5zR5?format=jpg&name=large"],
    "1909075939134185849": ["https://pbs.twimg.com/media/Gn5mcuZXMAA0I7Y?format=jpg&name=large"],
    "1986888060072575412": ["https://pbs.twimg.com/media/G5LYC5qXsAANOXz?format=jpg&name=large"],
    "1989437638470967786": ["https://pbs.twimg.com/media/G5vm782WMAAQN8T?format=jpg&name=4096x4096"],
    "1991617767242625433": ["https://pbs.twimg.com/media/G6OlzlGXAAECGOe?format=jpg&name=small"],
    "1994040903162581287": ["https://pbs.twimg.com/media/G6xBolfXMAAzaWy?format=jpg&name=large"],
    "1994938173575635124": ["https://pbs.twimg.com/media/G69xnHDXMAAojm9?format=jpg&name=large"],
    "1898604513449197853": ["https://pbs.twimg.com/media/Glkyt46WIAAdolu?format=png&name=900x900"],
    "1889859988644036730": ["https://pbs.twimg.com/media/GjohpK-WsAAq8PQ?format=jpg&name=large"],
    "1889708973697237476": ["https://pbs.twimg.com/media/GjmYS7oWoAE6IIz?format=jpg&name=large"],
    "1894266609742590249": ["https://pbs.twimg.com/media/GknJcTXXwAA-UFX?format=jpg&name=large"],
    "1889149385885233377": ["https://pbs.twimg.com/media/GjebWr2WgAAz67H?format=jpg&name=large"],
    "1884775370655736032": ["https://pbs.twimg.com/media/GigRNbSWQAAmUPW?format=jpg&name=large"],
    "1884781660379521495": ["https://pbs.twimg.com/media/GigW7iiWMAAvd37?format=jpg&name=large"],
    "1859671154677702680": ["https://pbs.twimg.com/media/Gc7hDzDWUAAk6Aq?format=jpg&name=large", "https://pbs.twimg.com/media/Gc7hDzEXIAEpwLX?format=jpg&name=large"],
    "1859033478358302873": ["https://pbs.twimg.com/media/GcydGK-XkAA8kpU?format=jpg&name=large", "https://pbs.twimg.com/media/GcydGK8XgAAcKi9?format=jpg&name=large"],
    "1859113446287003915": ["https://pbs.twimg.com/media/Gczl04vWkAEcnkR?format=jpg&name=large", "https://pbs.twimg.com/media/Gczl042WkAAs33_?format=jpg&name=large"],
    "1848416343588020679": ["https://pbs.twimg.com/media/Gabk3aZWYAAsqja?format=jpg&name=large"],
    "1846737870272303134": ["https://pbs.twimg.com/media/GaDuTe8WsAADAS4?format=jpg&name=large"],
    "1843741258113749412": ["https://pbs.twimg.com/media/GZZI5tlWMAAsBX8?format=jpg&name=large"],
    "1843685106550223306": ["https://pbs.twimg.com/media/GZYV1VPWwAAyOfn?format=jpg&name=medium"],
    "1843635401082262010": ["https://pbs.twimg.com/media/GZXooGDWgAA3ydE?format=jpg&name=small"],
    "1842663848446493167": ["https://pbs.twimg.com/media/GZJ1AGcXMAAIbFb?format=jpg&name=large"],
    "1842234285836599687": ["https://pbs.twimg.com/media/GZDuUYIWsAAOW5f?format=jpg&name=large"],
    "1842028984776769971": ["https://pbs.twimg.com/media/GZAzmUAXQAAB0fx?format=jpg&name=large"],
    "1841987072099549609": ["https://pbs.twimg.com/media/GZANeduXMAEPK-B?format=jpg&name=large"],
    "1841948247012868581": ["https://pbs.twimg.com/media/GY_qKUXXoAA-Wfl?format=jpg&name=large"],
    "1841867700156469497": ["https://pbs.twimg.com/media/GY-g6S9W0AEL75U?format=jpg&name=large"],
    "1841592538240553109": ["https://pbs.twimg.com/media/GY6mp0rXUAAhF_l?format=jpg&name=large"],
    "1841586191524561108": ["https://pbs.twimg.com/media/GY6g4YRWUAAiV7l?format=jpg&name=large"],
    "1841343308930707604": ["https://pbs.twimg.com/media/GY3D-q3WAAAzev0?format=jpg&name=small"],
    "1841275257820242373": ["https://pbs.twimg.com/media/GY2GFqDWMAILWih?format=jpg&name=large"],
    "1840962769052479650": ["https://pbs.twimg.com/media/GYxp4aqXYAQ40jw?format=jpg&name=large"],
    "1840120083487830348": ["https://pbs.twimg.com/media/GYlrdeOXgAIAx22?format=jpg&name=large"],
    "1840107774522601498": ["https://pbs.twimg.com/media/GYlgRBcXEAAuKnk?format=jpg&name=large"],
    "1839886011519627449": ["https://pbs.twimg.com/media/GYiWkxNXcAATeUk?format=jpg&name=large"],
    "1838424904825217472": ["https://pbs.twimg.com/media/GYNls5PW0AAwe8O?format=jpg&name=large"],
    "1836975477115822149": ["https://pbs.twimg.com/media/GX4_df7WoAA9Zfq?format=jpg&name=large"],
    "1836927607943680213": ["https://pbs.twimg.com/media/GX4T61GXUAASbnK?format=jpg&name=medium"],
    "1835830663708049851": ["https://pbs.twimg.com/media/GXouQguW4AAEllR?format=jpg&name=large"],
    "1835828891593605530": ["https://pbs.twimg.com/media/GXospZNXUAA6iWs?format=jpg&name=large", "https://pbs.twimg.com/media/GXospZCXAAAn7ho?format=jpg&name=large"],
    "1835727275880300968": ["https://pbs.twimg.com/media/GXnQOghXgAAPzgF?format=jpg&name=900x900"],
    "1835148653536657472": ["https://pbs.twimg.com/media/GXfB-WhWwAAg4kX?format=jpg&name=medium"],
    "1835103106591514778": ["https://pbs.twimg.com/media/GXeYjACXwAAXoZb?format=jpg&name=large"],
    "1835073115506069504": ["https://pbs.twimg.com/media/GXd9RbqWYAAL9z0?format=jpg&name=large"],
    "1835019485176050163": ["https://pbs.twimg.com/media/GXdMfuHWwAAVT9Z?format=jpg&name=large"],
    "1833722928313077851": ["https://pbs.twimg.com/media/GXKxSGgXIAAU85q?format=jpg&name=large"],
    "1831530070927646909": ["https://pbs.twimg.com/media/GWrm5DrWgAAa0bE?format=jpg&name=large", "https://pbs.twimg.com/media/GWrm5DpXMAEoyCD?format=jpg&name=large", "https://pbs.twimg.com/media/GWrm5DsXkAE7bA8?format=jpg&name=large"],
    "1829607289722192035": ["https://pbs.twimg.com/media/GWQSIarW4AI-5jE?format=jpg&name=large"],
    "1828187791693349050": ["https://pbs.twimg.com/media/GV8HF6XWAAALVD1?format=jpg&name=large"],
    "1828118161969033379": ["https://pbs.twimg.com/media/GV7HxwLXUAAg8Yr?format=jpg&name=large"],
}

def download_image(url: str, filepath: Path) -> bool:
    """Download an image from URL and save it."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Try to open with PIL to ensure it's a valid image
        img = Image.open(requests.get(url, headers=headers, stream=True, timeout=15).raw)
        
        # Convert to RGB if needed and save as JPEG
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        img.save(filepath, 'JPEG', quality=95)
        return True
        
    except Exception as e:
        print(f"    Error downloading: {e}")
        return False

def main():
    print(f"Downloading {len(DOODLE_URLS)} doodles with {sum(len(urls) for urls in DOODLE_URLS.values())} images...\n")
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for i, (status_id, urls) in enumerate(sorted(DOODLE_URLS.items()), 1):
        print(f"[{i}/{len(DOODLE_URLS)}] {status_id}...")
        
        # Check if already exists (for single images)
        if len(urls) == 1:
            out_file = OUT_DIR / f"{status_id}.jpg"
            if out_file.exists():
                print(f"  Skipping (already present)")
                skip_count += 1
                continue
        
        # Download all images for this post
        for img_idx, url in enumerate(urls, 1):
            if len(urls) == 1:
                # Single image: use status_id.jpg
                out_file = OUT_DIR / f"{status_id}.jpg"
            else:
                # Multiple images: use status_id-1.jpg, status_id-2.jpg, etc
                out_file = OUT_DIR / f"{status_id}-{img_idx}.jpg"
            
            if out_file.exists():
                print(f"  Image {img_idx}: already present")
                continue
            
            if download_image(url, out_file):
                print(f"  Image {img_idx}: ✓ Downloaded")
                success_count += 1
            else:
                print(f"  Image {img_idx}: ✗ Failed")
                fail_count += 1
    
    print(f"\n{'='*60}")
    print(f"Downloaded: {success_count}")
    print(f"Skipped: {skip_count}")
    print(f"Failed: {fail_count}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
