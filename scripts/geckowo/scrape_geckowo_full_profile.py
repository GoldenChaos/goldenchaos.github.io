import requests
import json
import time
import re
from pathlib import Path
from datetime import datetime

def scrape_geckowo_full_profile():
    """
    Scrape the entire @geckowo Twitter profile to get all comic posts.
    Uses Twitter's public API endpoints and web scraping as fallback.
    """
    
    print("Starting full profile scrape of @geckowo...")
    print("=" * 60)
    
    base_url = "https://x.com/geckowo"
    all_posts = {}  # Use dict to track by status_id
    
    # Try using Twitter's public API endpoints
    print("\n[Phase 1] Attempting to fetch via nitter.net mirror...")
    nitter_url = "https://nitter.net/geckowo"
    
    try:
        response = requests.get(nitter_url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            # Extract status IDs from nitter HTML
            # Nitter URLs look like: /geckowo/status/1234567890
            pattern = r'/geckowo/status/(\d+)'
            matches = re.findall(pattern, response.text)
            
            if matches:
                print(f"✓ Found {len(set(matches))} tweets via nitter")
                for status_id in set(matches):
                    if status_id not in all_posts:
                        all_posts[status_id] = {
                            'id': status_id,
                            'text': '',
                            'created_at': 'unknown',
                            'author_id': '0',
                            'public_metrics': {},
                            'entities': {}
                        }
    except Exception as e:
        print(f"✗ Nitter approach failed: {e}")
    
    # Try searching for all tweets from geckowo
    print("\n[Phase 2] Attempting search-based discovery...")
    
    # Build a search that gets all tweets from the user
    search_queries = [
        "from:geckowo",  # All tweets from geckowo
    ]
    
    for query in search_queries:
        try:
            search_url = f"https://x.com/search?q={query}&f=live"
            response = requests.get(search_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Look for status IDs in the response
            # Twitter embeds tweet data in data attributes
            pattern = r'/geckowo/status/(\d+)'
            matches = re.findall(pattern, response.text)
            
            found = len([s for s in matches if s not in all_posts])
            if found > 0:
                print(f"✓ Found {found} new tweets via search")
                for status_id in set(matches):
                    if status_id not in all_posts:
                        all_posts[status_id] = {
                            'id': status_id,
                            'text': '',
                            'created_at': 'unknown',
                            'author_id': '0',
                            'public_metrics': {},
                            'entities': {}
                        }
            time.sleep(1)
        except Exception as e:
            print(f"✗ Search query '{query}' failed: {e}")
    
    # Try direct profile scrape with pagination simulation
    print("\n[Phase 3] Attempting direct profile scrape...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch profile page
        response = requests.get("https://x.com/geckowo", headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Extract all status IDs from the page
            pattern = r'/geckowo/status/(\d+)'
            matches = re.findall(pattern, response.text)
            
            found = len([s for s in matches if s not in all_posts])
            if found > 0:
                print(f"✓ Found {found} new tweets on profile page")
                for status_id in set(matches):
                    if status_id not in all_posts:
                        all_posts[status_id] = {
                            'id': status_id,
                            'text': '',
                            'created_at': 'unknown',
                            'author_id': '0',
                            'public_metrics': {},
                            'entities': {}
                        }
    except Exception as e:
        print(f"✗ Direct profile scrape failed: {e}")
    
    # Load existing posts
    print("\n[Phase 4] Loading existing collection...")
    
    existing_ids = set()
    
    # Load from additional_posts.json
    try:
        if Path('data/geckowo/geckowo_additional_posts.json').exists():
            with open('data/geckowo/geckowo_additional_posts.json', 'r') as f:
                data = json.load(f)
                for post in data:
                    existing_ids.add(post.get('id', ''))
            print(f"✓ Loaded {len(existing_ids)} existing posts")
    except Exception as e:
        print(f"✗ Failed to load additional_posts.json: {e}")
    
    # Load from batch files
    batch_count = 0
    for batch_file in sorted(Path('geckowo_batches').glob('*.json')):
        try:
            with open(batch_file, 'r') as f:
                data = json.load(f)
                for post in data:
                    existing_ids.add(post.get('id', ''))
            batch_count += 1
        except:
            pass
    
    if batch_count > 0:
        print(f"✓ Loaded {batch_count} batch files ({len(existing_ids)} total unique)")
    
    # Filter out existing posts
    new_posts = {k: v for k, v in all_posts.items() if k not in existing_ids}
    
    print("\n" + "=" * 60)
    print(f"SCRAPE RESULTS:")
    print(f"  Total posts found: {len(all_posts)}")
    print(f"  Existing in collection: {len(existing_ids & set(all_posts.keys()))}")
    print(f"  NEW posts to add: {len(new_posts)}")
    print("=" * 60)
    
    if new_posts:
        # Save new posts to a batch file
        batch_num = 9
        batch_file = f"geckowo_batches/batch_2026-01-08-{batch_num}.json"
        
        # Check if file already exists and increment if needed
        while Path(batch_file).exists():
            batch_num += 1
            batch_file = f"geckowo_batches/batch_2026-01-08-{batch_num}.json"
        
        with open(batch_file, 'w') as f:
            json.dump(list(new_posts.values()), f, indent=2)
        
        print(f"\n✓ Saved {len(new_posts)} new posts to {batch_file}")
        print(f"\nNext step: Run the pipeline to download and number these comics")
        print(f"  cmd /c geckowo_pipeline.cmd")
        
        return len(new_posts)
    else:
        print("\n✓ No new posts found. Your collection is up to date!")
        print(f"Current collection size: {len(existing_ids)} comics")
        return 0

if __name__ == "__main__":
    scrape_geckowo_full_profile()

