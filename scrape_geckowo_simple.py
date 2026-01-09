import requests
import json
import re
from pathlib import Path

def scrape_geckowo_twitter_html():
    """
    Scrape @geckowo's Twitter profile by extracting initial state data from HTML.
    Twitter embeds a lot of tweet data in the initial page load.
    """
    
    print("Scraping @geckowo profile from x.com...")
    print("=" * 60)
    
    url = "https://x.com/geckowo"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        print(f"\n[1] Fetching profile page...")
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        html = response.text
        print(f"✓ Retrieved {len(html)} bytes of HTML")
        
        # Extract all tweet IDs from the HTML
        # Twitter URLs are in format: /geckowo/status/1234567890
        print(f"\n[2] Extracting tweet IDs from HTML...")
        
        all_tweet_ids = set()
        
        # Method 1: Look for status URLs in links
        pattern1 = r'/geckowo/status/(\d+)'
        matches1 = re.findall(pattern1, html)
        all_tweet_ids.update(matches1)
        print(f"✓ Found {len(matches1)} IDs via URL pattern")
        
        # Method 2: Look for tweet IDs in data attributes
        pattern2 = r'data-tweet-id="(\d+)"'
        matches2 = re.findall(pattern2, html)
        all_tweet_ids.update(matches2)
        print(f"✓ Found {len(matches2)} IDs via data attributes")
        
        # Method 3: Look for IDs in embedded JSON (Twitter often embeds state)
        pattern3 = r'"rest_id":"(\d{15,})"'
        matches3 = re.findall(pattern3, html)
        all_tweet_ids.update(matches3)
        print(f"✓ Found {len(matches3)} IDs via JSON rest_id")
        
        # Method 4: Look for tweet IDs in JavaScript variables
        pattern4 = r'"id_str":"(\d+)"'
        matches4 = re.findall(pattern4, html)
        all_tweet_ids.update(matches4)
        print(f"✓ Found {len(matches4)} IDs via id_str")
        
        # Method 5: Direct numeric IDs that look like Twitter snowflake IDs
        # Twitter IDs are 15-19 digits, starting around 2006
        pattern5 = r'\b(1[89]\d{17})\b'  # IDs starting with 18 or 19 (2020s)
        matches5 = re.findall(pattern5, html)
        all_tweet_ids.update(matches5)
        print(f"✓ Found {len(matches5)} IDs via snowflake pattern")
        
        print(f"\n✓ Total unique tweet IDs found: {len(all_tweet_ids)}")
        
        # Load existing collection
        print(f"\n[3] Loading existing collection...")
        
        existing_ids = set()
        
        if Path('geckowo_additional_posts.json').exists():
            with open('geckowo_additional_posts.json', 'r') as f:
                for post in json.load(f):
                    existing_ids.add(str(post.get('id', '')))
        
        batch_files = list(Path('geckowo_batches').glob('*.json'))
        for batch_file in sorted(batch_files):
            try:
                with open(batch_file, 'r') as f:
                    for post in json.load(f):
                        existing_ids.add(str(post.get('id', '')))
            except:
                pass
        
        print(f"✓ Existing collection: {len(existing_ids)} tweets")
        print(f"✓ Loaded from {len(batch_files)} batch files")
        
        # Check what's on disk
        comic_files = list(Path('geckowo_comics').glob('*.jpg'))
        print(f"✓ Comics on disk: {len(comic_files)}")
        
        # Find new IDs
        new_ids = all_tweet_ids - existing_ids
        
        print("\n" + "=" * 60)
        print(f"SCRAPE RESULTS:")
        print(f"  IDs extracted from page: {len(all_tweet_ids)}")
        print(f"  Already in collection: {len(existing_ids & all_tweet_ids)}")
        print(f"  NEW to add: {len(new_ids)}")
        print("=" * 60)
        
        if new_ids:
            # Create new batch file
            new_posts = []
            for tweet_id in sorted(new_ids):
                new_posts.append({
                    'id': tweet_id,
                    'text': '',
                    'created_at': 'unknown',
                    'author_id': '0',
                    'public_metrics': {},
                    'entities': {}
                })
            
            batch_num = 9
            batch_file = f"geckowo_batches/batch_2026-01-08-{batch_num}.json"
            while Path(batch_file).exists():
                batch_num += 1
                batch_file = f"geckowo_batches/batch_2026-01-08-{batch_num}.json"
            
            with open(batch_file, 'w') as f:
                json.dump(new_posts, f, indent=2)
            
            print(f"\n✓ Saved {len(new_ids)} new tweet IDs to {batch_file}")
            print(f"\nNext step: Run pipeline to download comics")
            print(f"  cmd /c geckowo_pipeline.cmd")
            
            return len(new_ids)
        else:
            print(f"\n✓ No new tweets found on initial page load")
            print(f"\nNote: Twitter only loads ~20 tweets initially.")
            print(f"For complete scraping, you'd need:")
            print(f"  - Selenium to scroll and load more tweets")
            print(f"  - Or continue manual batch collection (which is working great!)")
            return 0
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    scrape_geckowo_twitter_html()
