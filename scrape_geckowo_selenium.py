import json
import time
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def scrape_geckowo_selenium():
    """
    Scrape @geckowo's entire profile using Selenium to handle JavaScript loading.
    Scrolls through the entire timeline to collect all tweet IDs.
    """
    
    print("Starting Selenium-based full profile scrape of @geckowo...")
    print("=" * 60)
    
    driver = None
    all_tweet_ids = set()
    
    try:
        # Initialize Chrome driver
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        print("[1] Starting Chrome browser...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Navigate to profile
        print("[2] Loading @geckowo profile...")
        driver.get("https://x.com/geckowo")
        
        # Wait for tweets to load
        wait = WebDriverWait(driver, 10)
        
        print("[3] Scrolling through entire timeline...")
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        no_new_tweets_count = 0
        max_no_change_scrolls = 3
        
        while True:
            scroll_count += 1
            
            # Extract tweet IDs from current view
            # Twitter stores tweet links in href attributes
            tweets_before = len(all_tweet_ids)
            
            # Look for tweet links in the DOM
            tweet_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/status/']")
            
            for link in tweet_links:
                href = link.get_attribute('href')
                if href and '/status/' in href:
                    match = re.search(r'/status/(\d+)', href)
                    if match:
                        all_tweet_ids.add(match.group(1))
            
            tweets_after = len(all_tweet_ids)
            new_tweets = tweets_after - tweets_before
            
            print(f"  Scroll {scroll_count}: {all_tweet_ids.__len__()} total tweets found (+{new_tweets} new)")
            
            # Scroll down
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(2)  # Wait for new content to load
            
            # Check if we've reached the bottom
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                # Page height didn't change
                if new_tweets == 0:
                    no_new_tweets_count += 1
                    if no_new_tweets_count >= max_no_change_scrolls:
                        print("\n✓ Reached end of profile (no new tweets in last scrolls)")
                        break
                else:
                    no_new_tweets_count = 0
            else:
                no_new_tweets_count = 0
            
            last_height = new_height
            
            # Safety limit: stop after reasonable number of scrolls
            if scroll_count > 100:
                print("\n⚠ Reached scroll limit (100 scrolls), stopping")
                break
        
        print("\n" + "=" * 60)
        print(f"SCRAPE RESULTS:")
        print(f"  Total unique tweets found: {len(all_tweet_ids)}")
        
    except Exception as e:
        print(f"\n✗ Error during scraping: {e}")
    
    finally:
        if driver:
            driver.quit()
            print("\n[4] Browser closed")
    
    # Now compare with existing collection
    print("\n[5] Comparing with existing collection...")
    
    existing_ids = set()
    
    # Load from all existing sources
    if Path('geckowo_additional_posts.json').exists():
        try:
            with open('geckowo_additional_posts.json', 'r') as f:
                for post in json.load(f):
                    existing_ids.add(post.get('id', ''))
        except:
            pass
    
    for batch_file in sorted(Path('geckowo_batches').glob('*.json')):
        try:
            with open(batch_file, 'r') as f:
                for post in json.load(f):
                    existing_ids.add(post.get('id', ''))
        except:
            pass
    
    print(f"✓ Existing collection has {len(existing_ids)} unique tweets")
    
    new_ids = all_tweet_ids - existing_ids
    
    print("\n" + "=" * 60)
    print(f"COLLECTION STATUS:")
    print(f"  Existing tweets: {len(existing_ids)}")
    print(f"  Newly discovered: {len(new_ids)}")
    print(f"  Total profile tweets: {len(all_tweet_ids)}")
    print("=" * 60)
    
    if new_ids:
        # Create batch file with new tweets
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
        print(f"\nNext step: Run pipeline to download these comics")
        print(f"  cmd /c geckowo_pipeline.cmd")
        
        return len(new_ids)
    else:
        print("\n✓ Collection is complete!")
        return 0

if __name__ == "__main__":
    try:
        new_count = scrape_geckowo_selenium()
    except ImportError:
        print("ERROR: Selenium not installed")
        print("\nInstall with: pip install selenium")
        print("Also need ChromeDriver: https://chromedriver.chromium.org/")
