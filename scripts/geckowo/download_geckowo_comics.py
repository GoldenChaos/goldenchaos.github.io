import os
import json
from io import BytesIO
from PIL import Image
import requests
import sys

# Force UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load excluded posts (non-comics that should be skipped)
EXCLUDED_POSTS = set()
excluded_file = 'data/geckowo/geckowo_excluded_posts.json'
if os.path.exists(excluded_file):
    with open(excluded_file, 'r', encoding='utf-8') as f:
        EXCLUDED_POSTS = set(json.load(f))
    print(f"Loaded {len(EXCLUDED_POSTS)} excluded post IDs")

# Base posts embedded (existing set)
BASE_POSTS = [
  {"time": "unknown", "link": "https://x.com/geckowo/status/2007627462503694821", "imgs": ["https://pbs.twimg.com/media/G9yGf2mXMAAPdNc"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/2006942118607221121", "imgs": ["https://pbs.twimg.com/media/G9oXG8wW4AACpit"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/2006512742098940073", "imgs": ["https://pbs.twimg.com/media/G9iQtNYWQAAv-Ek"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/2004104557735903739", "imgs": ["https://pbs.twimg.com/media/G9ACZMoXgAABRCx"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/2003348435332923592", "imgs": ["https://pbs.twimg.com/media/G81SyRAXMAEHC3u"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/2001009071022014485", "imgs": ["https://pbs.twimg.com/media/G8UDJSdXQAI5zuH"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/2000031769073197547", "imgs": ["https://pbs.twimg.com/media/G8GKSx0W4AULLII"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1998193217003737463", "imgs": ["https://pbs.twimg.com/media/G7sCG4vWcAA-bUz"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1995170443209461907", "imgs": ["https://pbs.twimg.com/media/G7BE8cxXEAAmYYB"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1994938173575635124", "imgs": ["https://pbs.twimg.com/media/G69xnHDXMAAojm9"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1994764481201934616", "imgs": ["https://pbs.twimg.com/media/G67TuW-XYAE7gQn"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1994040903162581287", "imgs": ["https://pbs.twimg.com/media/G6xBolfXMAAzaWy"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1994038594013454591", "imgs": ["https://pbs.twimg.com/media/G6w_iL-WMAA0jfE"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1993317557206761930", "imgs": ["https://pbs.twimg.com/media/G6mvv9hWUAAthA9"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1992951646620651938", "imgs": ["https://pbs.twimg.com/media/G6hi9hAWcAAymjq"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1992705242094526606", "imgs": ["https://pbs.twimg.com/media/G6eC2LQXAAAPhXX"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1992290183270593009", "imgs": ["https://pbs.twimg.com/media/G6YJVFkX0AAZ9Cu"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1991995739740991926", "imgs": ["https://pbs.twimg.com/media/G6T9kaJXkAARnau"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1991617767242625433", "imgs": ["https://pbs.twimg.com/media/G6OlzlGXAAECGOe"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1991170107482238983", "imgs": ["https://pbs.twimg.com/media/G6IOpv4XYAAgYdy"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1989437638470967786", "imgs": ["https://pbs.twimg.com/media/G5vm782WMAAQN8T"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1989342790778765448", "imgs": ["https://pbs.twimg.com/media/G5uQufkXYAAmMJs"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1986888060072575412", "imgs": ["https://pbs.twimg.com/media/G5LYC5qXsAANOXz"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1986142667248701949", "imgs": ["https://pbs.twimg.com/media/G5AyOvobIAEsKXI"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1986055753481032070", "imgs": ["https://pbs.twimg.com/media/G4_jKwqaoAAFiGF"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1983649436090998818", "imgs": ["https://pbs.twimg.com/media/G4dWplFXEAA16gJ"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1982075078293483613", "imgs": ["https://pbs.twimg.com/media/G4G-x5cXkAAFnsB"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1981316646946898378", "imgs": ["https://pbs.twimg.com/media/G38M_WwWkAAI7yC"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1979880208225239518", "imgs": ["https://pbs.twimg.com/media/G3mSVO9XkAAEmMi"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1978089944779202991", "imgs": ["https://pbs.twimg.com/media/G3OWUpIWAAAO_Ve"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1975545937402704151", "imgs": ["https://pbs.twimg.com/media/G2qMj43XAAAoLYW"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1975166690984915230", "imgs": ["https://pbs.twimg.com/media/G2kzo4jWoAAWA-V"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1974811148026339513", "imgs": ["https://pbs.twimg.com/media/G2fwRgxWQAAF5bF"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1974570348868763846", "imgs": ["https://pbs.twimg.com/media/G2cVLPvW0AA16OM"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1974457416545955937", "imgs": ["https://pbs.twimg.com/media/G2aujppWUAAk6wV"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1973545988309786897", "imgs": ["https://pbs.twimg.com/media/G2NxbILWkAAsbuk"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1973357225826468232", "imgs": ["https://pbs.twimg.com/media/G2JuPNuX0AAdi4J"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1972994836681932971", "imgs": ["https://pbs.twimg.com/media/G2CrW1OXIAAQ8Xh"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1972655936838766978", "imgs": ["https://pbs.twimg.com/media/G2BIHp8W0AAzYw3"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1972417152188829877", "imgs": ["https://pbs.twimg.com/media/G19u72pXoAAHm9Z"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1970820522762993773", "imgs": ["https://pbs.twimg.com/media/G1llFEtXIAAHgtg"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1970253718282264891", "imgs": ["https://pbs.twimg.com/media/G1e_SOGWcAAkXLi"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1969913743850279300", "imgs": ["https://pbs.twimg.com/media/G1aKGjmWkAAMDCR"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1968646191417008319", "imgs": ["https://pbs.twimg.com/media/G1GftKwWEAEM5Qn"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1967908198339555468", "imgs": ["https://pbs.twimg.com/media/G09qE1YWEAEzNsW"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1967715400403304558", "imgs": ["https://pbs.twimg.com/media/G066sipXQAA1SvM"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1966480036422131732", "imgs": ["https://pbs.twimg.com/media/G0pXK9eX0AALahH"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1966471865213600145", "imgs": ["https://pbs.twimg.com/media/G0n2qTtW8AAFUt9"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1966121044403712204", "imgs": ["https://pbs.twimg.com/media/G0hfz9rXEAAh8Uk"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1965742004316647768", "imgs": ["https://pbs.twimg.com/media/G0e37qBX0AAumQI"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1965033378266394862", "imgs": ["https://pbs.twimg.com/media/G0UzcRsWQAAySyv"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1964677260566544579", "imgs": ["https://pbs.twimg.com/media/G0Pvjb4W4AAET5E"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1964314103863705905", "imgs": ["https://pbs.twimg.com/media/G0KlRCmXcAA5zR5"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1964303964356198700", "imgs": ["https://pbs.twimg.com/media/G0KcCsGW4AEdwdB"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1963954550383026218", "imgs": ["https://pbs.twimg.com/media/G0FeQQRXMAAMvw8"]},
  {"time": "unknown", "link": "https://x.com/geckowo/status/1963935349077422174", "imgs": ["https://pbs.twimg.com/media/G0FMygwXgAAM5Ik"]}
]

def extend_from_json(path, posts):
    try:
        with open(path, 'r') as f:
            extra = json.load(f)
            if isinstance(extra, list):
                posts.extend(extra)
                print(f"Loaded {len(extra)} additional posts from {path}")
    except Exception as e:
        print(f"Warning: failed to read {path}: {e}")

# Merge in additional posts if present
posts = list(BASE_POSTS)

# Back-compat single-file path
ADD_PATH = 'data/geckowo/geckowo_additional_posts.json'
if os.path.exists(ADD_PATH):
    extend_from_json(ADD_PATH, posts)

# New multi-batch ingestion from folder
BATCH_DIR = 'geckowo_batches'
if os.path.isdir(BATCH_DIR):
    for name in sorted(os.listdir(BATCH_DIR)):
        # Skip doodle batches; those are handled by the doodles downloader
        if name.lower().startswith('batch_doodles_'):
            continue
        if name.lower().endswith('.json'):
            extend_from_json(os.path.join(BATCH_DIR, name), posts)

# Build unique map by status_id and merge image URLs
unique = {}
for p in posts:
    try:
        sid = p['link'].split('/')[-1]
        
        # Skip excluded posts (non-comics)
        if sid in EXCLUDED_POSTS:
            continue
            
        imgs = p.get('imgs', [])
        if sid not in unique:
            unique[sid] = { 'status_id': sid, 'link': p['link'], 'imgs': [] }
        for u in imgs:
            if u not in unique[sid]['imgs']:
                unique[sid]['imgs'].append(u)
    except Exception:
        continue

final_posts = list(unique.values())
# Sort newest first by status_id
final_posts.sort(key=lambda x: int(x['status_id']), reverse=True)

out_dir = 'geckowo_archive/comics'
os.makedirs(out_dir, exist_ok=True)

# Build a set of status_ids that already exist (raw or numbered) to avoid re-downloading
existing_ids = set()
for name in os.listdir(out_dir):
    if not name.lower().endswith('.jpg'):
        continue
    base = name[:-4]
    # Raw variants: <sid>.jpg or <sid><suffix>.jpg
    if base.isdigit():
        existing_ids.add(base)
        continue
    # Suffixed raw: digits + single letter
    if len(base) > 1 and base[:-1].isdigit() and base[-1].isalpha():
        existing_ids.add(base[:-1])
        continue
    # Numbered: 0001 - <sid>.jpg
    if ' - ' in base:
        parts = base.split(' - ')
        if len(parts) == 2 and parts[1].isdigit():
            existing_ids.add(parts[1])

print(f"Starting download of {len(final_posts)} comics...")

for i, post in enumerate(final_posts, 1):
    sid = post['status_id']
    if sid in existing_ids:
        print(f"[{i}/{len(final_posts)}] Skipping {sid} (already present)")
        continue
    for j, url in enumerate(post['imgs']):
        # Attempt multiple URL formats
        attempts = [
            f"{url}?format=jpg&name=orig",
            f"{url}?format=png&name=orig",
            f"{url}.jpg:orig",
            f"{url}.png:orig",
        ]
        resp = None
        for a in attempts:
            print(f"[{i}/{len(final_posts)}] Downloading {a}...")
            try:
                r = requests.get(a, timeout=20)
                if r.status_code == 200:
                    resp = r
                    print("  ✓ Success with this URL format!")
                    break
            except Exception:
                pass
        if not resp:
            print("  ❌ Failed all URL formats - skipping")
            continue
        try:
            img = Image.open(BytesIO(resp.content))
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            suffix = '' if len(post['imgs']) == 1 else chr(97 + j)
            filename = f"{sid}{suffix}.jpg"
            path = os.path.join(out_dir, filename)
            img.save(path, format='JPEG', quality=95)
            print(f"  ✓ Saved: {filename}")
        except Exception as e:
            print(f"  ❌ Error processing image: {e}")

print(f"\n✓ All done! Comics saved to: {os.path.abspath(out_dir)}")
print(f"Total unique posts processed: {len(final_posts)}")

