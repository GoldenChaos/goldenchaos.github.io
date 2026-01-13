import os
import json
from io import BytesIO
from PIL import Image
import requests
import sys

# Force UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Base doodle posts
BASE_POSTS = []

# Load additional posts from batch files
def load_json(path):
    """Load JSON file safely"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return []

# Load batch files
doodle_batches = []
batch_dir = 'geckowo_batches'
for fname in sorted(os.listdir(batch_dir)):
    if fname.startswith('batch_doodles_') and fname.endswith('.json'):
        posts = load_json(os.path.join(batch_dir, fname))
        doodle_batches.extend(posts)
        print(f"Loaded {len(posts)} doodles from {fname}")

all_posts = BASE_POSTS + doodle_batches

# Deduplicate and extract image URLs
unique = {}
for post in all_posts:
    link = post.get('link', '')
    if not link:
        continue
    sid = link.split('/')[-1]
    
    try:
        imgs = post.get('imgs', [])
        if isinstance(imgs, str):
            imgs = [imgs]
        # For doodles, links without imgs are still valid (we'll fetch from API)
        if sid not in unique:
            unique[sid] = {'status_id': sid, 'link': link, 'imgs': imgs}
        else:
            for u in imgs:
                if u not in unique[sid]['imgs']:
                    unique[sid]['imgs'].append(u)
    except Exception:
        continue

final_posts = list(unique.values())
# Sort newest first by status_id
final_posts.sort(key=lambda x: int(x['status_id']), reverse=True)

out_dir = 'geckowo_archive/doodles'
os.makedirs(out_dir, exist_ok=True)

# Build a set of status_ids that already exist
existing_ids = set()
for name in os.listdir(out_dir):
    if not name.lower().endswith('.jpg'):
        continue
    base = name[:-4]
    if base.isdigit():
        existing_ids.add(base)
        continue
    if len(base) > 1 and base[:-1].isdigit() and base[-1].isalpha():
        existing_ids.add(base[:-1])
        continue
    if ' - ' in base:
        parts = base.split(' - ')
        if len(parts) == 2 and parts[1].isdigit():
            existing_ids.add(parts[1])

print(f"Starting download of {len(final_posts)} doodles...")

for i, post in enumerate(final_posts, 1):
    sid = post['status_id']
    if sid in existing_ids:
        print(f"[{i}/{len(final_posts)}] Skipping {sid} (already present)")
        continue
    for j, url in enumerate(post['imgs']):
        # Attempt multiple URL formats
        attempts = [
            f"{url}?format=jpg&name=orig",
            f"{url}:orig",
            f"{url}:large",
            url
        ]
        
        success = False
        for attempt_url in attempts:
            try:
                r = requests.get(attempt_url, timeout=10)
                if r.status_code != 200:
                    continue
                    
                img = Image.open(BytesIO(r.content))
                # Save with suffix if multiple images
                suffix = '' if j == 0 else chr(97 + j - 1)  # a, b, c...
                fname = f"{sid}{suffix}.jpg"
                fpath = os.path.join(out_dir, fname)
                img.save(fpath, 'JPEG', quality=95)
                print(f"[{i}/{len(final_posts)}] Downloaded {sid} → {fname}")
                success = True
                break
            except Exception as e:
                continue
        
        if not success:
            print(f"[{i}/{len(final_posts)}] Failed to download {sid}")

print(f"Total unique posts processed: {len(final_posts)}")
