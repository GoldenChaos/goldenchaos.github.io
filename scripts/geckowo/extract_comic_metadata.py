import os
import json
import re
from datetime import datetime

# Twitter's snowflake epoch (Nov 04, 2010 01:42:54 UTC)
TWITTER_EPOCH = 1288834974657

def decode_twitter_id(status_id):
    """Extract timestamp from Twitter snowflake ID"""
    timestamp_ms = (int(status_id) >> 22) + TWITTER_EPOCH
    return datetime.fromtimestamp(timestamp_ms / 1000.0)

# Read all files from geckowo_comics folder
comics_folder = 'geckowo_comics'

# Group candidates by status_id, preferring raw files over previously numbered ones
groups = {}

for filename in sorted(os.listdir(comics_folder)):
    if not filename.lower().endswith('.jpg'):
        continue

    base = filename[:-4]  # strip .jpg

    # Parse numbered files: "0001 - 1963935349077422174.jpg" and extract status_id
    if ' - ' in base:
        parts = base.split(' - ')
        if len(parts) == 2 and parts[1].isdigit():
            status_id = parts[1]
            if status_id not in groups:
                groups[status_id] = set()
            groups[status_id].add('')  # canonical is already applied; just track it
            continue

    # Match raw filenames: "<status_id>.jpg" or "<status_id><suffix>.jpg" where suffix is a single letter (a/b/...)
    m = re.match(r'^(\d+)([a-z])?$', base)
    if not m:
        continue

    status_id, suffix = m.group(1), m.group(2) or ''

    if status_id not in groups:
        groups[status_id] = set()
    groups[status_id].add(suffix)

# Build comic entries, choosing a canonical filename per status_id
def choose_filename(status_id, suffixes):
    # Prefer no-suffix file ("<id>.jpg") if present; otherwise prefer 'b', then highest suffix alphabetically
    if '' in suffixes:
        return f"{status_id}.jpg"
    if 'b' in suffixes:
        return f"{status_id}b.jpg"
    chosen = sorted(suffixes)[-1]
    return f"{status_id}{chosen}.jpg"

comics = []
for status_id, suffixes in groups.items():
    timestamp = decode_twitter_id(status_id)
    filename = choose_filename(status_id, suffixes)
    comics.append({
        'status_id': status_id,
        'filename': filename,
        'timestamp': timestamp.isoformat(),
        'date': timestamp.strftime('%Y-%m-%d'),
        'time': timestamp.strftime('%H:%M:%S'),
        'link': f'https://x.com/geckowo/status/{status_id}'
    })

# Sort by timestamp descending (newest first) and assign numbers
comics.sort(key=lambda x: x['timestamp'], reverse=True)
for idx, comic in enumerate(comics, 1):
    comic['number'] = idx
    print(f"#{idx:04d} - {comic['date']} {comic['time']} - {comic['filename']}")

# Save to JSON
with open('data/geckowo/geckowo_comics_metadata.json', 'w') as f:
    json.dump(comics, f, indent=2)

print(f"\n✓ Metadata saved to: {os.path.abspath('data/geckowo/geckowo_comics_metadata.json')}")
print(f"Total comics processed: {len(comics)}")
print(f"Date range: {comics[0]['date']} to {comics[-1]['date']}")

