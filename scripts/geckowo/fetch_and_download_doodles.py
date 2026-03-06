#!/usr/bin/env python3
"""
Fetch image URLs from tweets and download missing doodles.
Uses web scraping to extract image URLs from tweet pages.
"""

import json
import os
import re
import time
from pathlib import Path

import requests
from PIL import Image

# All tracked doodle IDs
DOODLE_IDS = [
    "1945726526621679961", "1945726519847915927", "1973545988309786897",
    "1973357225826468232", "1934320424961073523", "1964314103863705905",
    "1909075939134185849", "1932060194756055376", "1929225464897327236",
    "1920938098956870081", "1906885517863461162", "1906461229985538398",
    "1906457320898326660", "1905430005103948109", "1904931179666567262",
    "1904682651404947719", "1904325170447393018", "1903939797917266021",
    "1902573765239669222", "1902469409009992048", "1899340715127194094",
    "1986888060072575412", "1989437638470967786", "1991617767242625433",
    "1994040903162581287", "1994938173575635124",
    "1898610649556492853", "1898604513449197853", "1889859988644036730",
    "1889708973697237476", "1894266609742590249", "1889149385885233377",
    "1884775370655736032", "1884781660379521495", "1859671154677702680",
    "1859033478358302873", "1859113446287003915", "1848416343588020679",
    "1846737870272303134", "1843741258113749412", "1843685106550223306",
    "1843635401082262010", "1842663848446493167", "1842234285836599687",
    "1842028984776769971", "1841987072099549609", "1841948247012868581",
    "1841867700156469497", "1841592538240553109", "1841586191524561108",
    "1841343308930707604", "1841275257820242373", "1840962769052479650",
    "1840120083487830348", "1840107774522601498", "1839886011519627449",
    "1838424904825217472", "1836975477115822149", "1836927607943680213",
    "1835830663708049851", "1835828891593605530", "1835727275880300968",
    "1835148653536657472", "1835103106591514778", "1835073115506069504",
    "1835019485176050163", "1833722928313077851", "1831530070927646909",
    "1829607289722192035", "1828187791693349050", "1828118161969033379"
]

OUT_DIR = Path("geckowo_archive/doodles")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_image_url(status_id: str, timeout: int = 10) -> str | None:
    """
    Scrape image URL from a tweet page.
    """
    tweet_url = f"https://x.com/geckowo/status/{status_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(tweet_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Look for pbs.twimg.com URLs in the HTML
        # These are the image URLs Twitter/X uses
        matches = re.findall(r'https://pbs\.twimg\.com/media/[^"<>\s]+', response.text)
        
        if matches:
            # Return the first image URL found
            # Strip off any parameters and ensure it's a valid format
            img_url = matches[0]
            # Add format parameters for high quality
            if '?' not in img_url:
                return img_url + '?format=jpg&name=orig'
            return img_url
                
    except Exception as e:
        pass
    
    return None

def download_image(url: str, status_id: str) -> bool:
    """Download an image from URL and save with status_id as filename."""
    out_file = OUT_DIR / f"{status_id}.jpg"
    
    if out_file.exists():
        print(f"  Skipping {status_id} (already present)")
        return True
    
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
        
        img.save(out_file, 'JPEG', quality=95)
        print(f"  ✓ Downloaded {status_id}")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to download {status_id}: {e}")
        return False

def main():
    print(f"Attempting to fetch and download {len(DOODLE_IDS)} doodles...\n")
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for i, status_id in enumerate(DOODLE_IDS, 1):
        print(f"[{i}/{len(DOODLE_IDS)}] Processing {status_id}...")
        
        out_file = OUT_DIR / f"{status_id}.jpg"
        if out_file.exists():
            print(f"  Skipping (already present)")
            skip_count += 1
            continue
        
        # Fetch the image URL
        image_url = fetch_image_url(status_id)
        
        if not image_url:
            print(f"  ✗ Could not find image URL")
            fail_count += 1
            time.sleep(1)  # Rate limiting
            continue
        
        print(f"  Found image URL: {image_url}")
        
        # Download the image
        if download_image(image_url, status_id):
            success_count += 1
        else:
            fail_count += 1
        
        # Rate limiting
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"Downloaded: {success_count}")
    print(f"Skipped (already present): {skip_count}")
    print(f"Failed: {fail_count}")
    print(f"Total: {len(DOODLE_IDS)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
