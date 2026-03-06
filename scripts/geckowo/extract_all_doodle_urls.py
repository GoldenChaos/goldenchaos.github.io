#!/usr/bin/env python3
"""
Extract all doodle image URLs from batch files.
Search all batch formats and collect URLs for missing doodles.
"""

import json
import re
from pathlib import Path

# All tracked doodle IDs
DOODLE_IDS = {
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
}

BATCH_DIR = Path("geckowo_batches")
found_urls = {}

# Format 1: {"link": "...", "imgs": [...]} format
for batch_file in sorted(BATCH_DIR.glob("batch_*.json")):
    if "doodles" in batch_file.name:
        continue
    
    try:
        with open(batch_file) as f:
            data = json.load(f)
        
        if isinstance(data, list):
            for item in data:
                # Check format 1
                if "link" in item and "imgs" in item:
                    # Extract status ID from link
                    match = re.search(r'/status/(\d+)', item.get("link", ""))
                    if match:
                        status_id = match.group(1)
                        if status_id in DOODLE_IDS and status_id not in found_urls:
                            imgs = item.get("imgs", [])
                            if imgs:
                                found_urls[status_id] = imgs[0]
                                print(f"Found {status_id} in {batch_file.name}: {imgs[0]}")
                
                # Check format 2 (id field)
                elif "id" in item:
                    status_id = str(item.get("id"))
                    if status_id in DOODLE_IDS and status_id not in found_urls:
                        # Some have image data in different formats
                        if "image" in item:
                            found_urls[status_id] = item.get("image")
                            print(f"Found {status_id} in {batch_file.name}: {item.get('image')}")
    
    except (json.JSONDecodeError, KeyError):
        pass

print(f"\n{'='*60}")
print(f"Total doodles with image URLs: {len(found_urls)}")
print(f"{'='*60}\n")

# Write to new batch file
output_batch = {
    "doodles": []
}

for status_id, img_url in sorted(found_urls.items()):
    output_batch["doodles"].append({
        "link": f"https://x.com/geckowo/status/{status_id}",
        "imgs": [img_url]
    })

# Load existing batch to preserve what we have
existing_batch = []
batch_doodles_file = BATCH_DIR / "batch_doodles_2026-01-11.json"
if batch_doodles_file.exists():
    with open(batch_doodles_file) as f:
        existing_batch = json.load(f)

# Merge: existing entries first, then add new ones that aren't already there
existing_ids = {re.search(r'/status/(\d+)', item.get("link", "")).group(1) 
                for item in existing_batch if "link" in item}

merged = list(existing_batch)
for item in output_batch["doodles"]:
    status_id = re.search(r'/status/(\d+)', item.get("link", "")).group(1)
    if status_id not in existing_ids:
        merged.append(item)
        print(f"Adding {status_id} to batch file")

with open(batch_doodles_file, 'w') as f:
    json.dump(merged, f, indent=2)

print(f"\nUpdated {batch_doodles_file}")
print(f"Total entries in batch file: {len(merged)}")
