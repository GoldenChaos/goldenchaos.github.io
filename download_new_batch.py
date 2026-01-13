#!/usr/bin/env python3
"""Download images from batch files with full URLs."""

import json
from pathlib import Path
import requests
from PIL import Image
import re

def download_from_batch(batch_file: Path, out_dir: Path):
    """Download all images from a batch file."""
    with open(batch_file) as f:
        data = json.load(f)
    
    out_dir.mkdir(parents=True, exist_ok=True)
    
    success = 0
    skip = 0
    fail = 0
    
    for item in data:
        link = item.get("link", "")
        imgs = item.get("imgs", [])
        
        # Extract status ID from link
        match = re.search(r'/status/(\d+)', link)
        if not match or not imgs:
            continue
        
        status_id = match.group(1)
        
        for img_url in imgs:
            out_file = out_dir / f"{status_id}.jpg"
            
            if out_file.exists():
                print(f"  Skipping {status_id} (already present)")
                skip += 1
                continue
            
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(img_url, headers=headers, timeout=15)
                response.raise_for_status()
                
                # Open with PIL
                img = Image.open(requests.get(img_url, headers=headers, stream=True, timeout=15).raw)
                
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                img.save(out_file, 'JPEG', quality=95)
                print(f"  ✓ Downloaded {status_id}")
                success += 1
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"  ✗ Failed {status_id}: {e}")
                fail += 1
                break
    
    return success, skip, fail

# Download comics
print("Downloading comics...")
comics_success, comics_skip, comics_fail = download_from_batch(
    Path("geckowo_batches/batch_2026-01-11-14.json"),
    Path("geckowo_archive/comics")
)

# Download doodles  
print("\nDownloading doodles...")
doodles_success, doodles_skip, doodles_fail = download_from_batch(
    Path("geckowo_batches/batch_doodles_2026-01-11-new.json"),
    Path("geckowo_archive/doodles")
)

print(f"\n{'='*60}")
print(f"Comics: ✓{comics_success} Skipped:{comics_skip} ✗{comics_fail}")
print(f"Doodles: ✓{doodles_success} Skipped:{doodles_skip} ✗{doodles_fail}")
print(f"{'='*60}")
