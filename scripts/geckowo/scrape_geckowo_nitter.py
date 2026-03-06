import requests
import json
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup

def scrape_geckowo_nitter():
    """
    Scrape @geckowo from nitter.net (open-source Twitter frontend).
    Nitter doesn't require authentication and loads all tweets server-side.
    """
    
    print("Scraping @geckowo from nitter.net...")
    print("=" * 60)
    
    all_tweet_ids = set()
    cursor = None
    page_count = 0
    max_pages = 100  # Safety limit
    
    base_url = "https://nitter.net/geckowo"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        while page_count < max_pages:
            page_count += 1
            
            # Build URL with pagination
            url = base_url
            params = {}
            if cursor:
                params['cursor'] = cursor
            
            print(f"\n[Page {page_count}] Fetching {url}...")
            
            try:
                response = requests.get(url, params=params, headers=headers, timeout=15)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all tweet links
                # Nitter tweet links are in format: /geckowo/status/1234567890
                tweet_links = soup.find_all('a', href=re.compile(r'/geckowo/status/\d+'))
                
                tweets_before = len(all_tweet_ids)
                
                for link in tweet_links:
                    href = link.get('href', '')
                    match = re.search(r'/status/(\d+)', href)
                    if match:
                        all_tweet_ids.add(match.group(1))
                
                tweets_after = len(all_tweet_ids)
                new_tweets = tweets_after - tweets_before
                
                print(f"  Found {new_tweets} new tweets (total: {tweets_after})")
                
                # Look for next page cursor/continuation
                # Nitter pagination uses cursor parameter
                continuation = soup.find('div', {'class': 'timeline-continuation'})
                if continuation:
                    cursor_match = re.search(r'cursor=([^"&]+)', str(continuation))
                    if cursor_match:
                        cursor = cursor_match.group(1)
                        print(f"  Next cursor found: {cursor[:20]}...")
                    else:
                        print("  No more pages found")
                        break
                else:
                    # Try alternative: look for infinite scroll marker
                    if '<div class="show-more">' not in response.text and new_tweets == 0:
                        print("  Reached end of timeline (no new tweets)")
                        break
                
                time.sleep(2)  # Be respectful to the server
                
            except requests.RequestException as e:
                print(f"  ✗ Request failed: {e}")
                if page_count > 3:  # Only stop after getting some data
                    print("  Continuing with collected data...")
                    break
                raise
        
        print("\n" + "=" * 60)
        print(f"SCRAPE RESULTS:")
        print(f"  Pages scraped: {page_count}")
        print(f"  Total unique tweets found: {len(all_tweet_ids)}")
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        if len(all_tweet_ids) == 0:
            print("  No tweets collected. Try: pip install beautifulsoup4")
            raise
    
    # Compare with existing collection
    print("\n[Comparing with existing collection...]")
    
    existing_ids = set()
    
    # Load existing posts
    if Path('data/geckowo/geckowo_additional_posts.json').exists():
        with open('data/geckowo/geckowo_additional_posts.json', 'r') as f:
            for post in json.load(f):
                existing_ids.add(str(post.get('id', '')))
    
    for batch_file in sorted(Path('geckowo_batches').glob('*.json')):
        try:
            with open(batch_file, 'r') as f:
                for post in json.load(f):
                    existing_ids.add(str(post.get('id', '')))
        except:
            pass
    
    print(f"✓ Existing collection: {len(existing_ids)} tweets")
    
    # Also check disk for files
    comic_files = list(Path('geckowo_comics').glob('*.jpg'))
    print(f"✓ Comics on disk: {len(comic_files)}")
    
    new_ids = all_tweet_ids - existing_ids
    
    print("\n" + "=" * 60)
    print(f"COLLECTION STATUS:")
    print(f"  Existing in metadata: {len(existing_ids)}")
    print(f"  Newly discovered: {len(new_ids)}")
    print(f"  Total on @geckowo: {len(all_tweet_ids)}")
    print(f"  Collection coverage: {len(existing_ids) / max(len(all_tweet_ids), 1) * 100:.1f}%")
    print("=" * 60)
    
    if new_ids:
        # Create batch file
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
        
        print(f"\n✓ Saved {len(new_ids)} new tweets to {batch_file}")
        print(f"\nNext: Run the pipeline to download these comics")
        print(f"  cd C:\\Users\\jess\\Sites\\goldenchaos.github.io\\goldenchaos.github.io")
        print(f"  cmd /c geckowo_pipeline.cmd")
        
        return len(new_ids)
    else:
        print("\n✓ Collection appears to be complete or up to date!")
        return 0

if __name__ == "__main__":
    try:
        scrape_geckowo_nitter()
    except ImportError as e:
        print(f"ERROR: Missing package: {e}")
        print("\nInstall with: pip install beautifulsoup4 requests")

