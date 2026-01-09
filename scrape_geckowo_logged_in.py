import json
import time
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def scrape_geckowo_media_logged_in(username, password):
    """
    Scrape @geckowo's media tab while logged in.
    This allows access to the full timeline including all historical posts.
    """
    
    print("Starting logged-in media scrape of @geckowo...")
    print("=" * 60)
    
    driver = None
    all_tweet_ids = set()
    
    try:
        # Initialize Chrome driver
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        print("[1] Starting Chrome browser...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Login to Twitter
        print("\n[2] Logging in to Twitter/X...")
        driver.get("https://x.com/i/flow/login")
        
        wait = WebDriverWait(driver, 20)
        
        # Enter username
        print("  Entering username...")
        username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='username']")))
        username_input.send_keys(username)
        username_input.send_keys(Keys.RETURN)
        
        time.sleep(2)
        
        # Enter password
        print("  Entering password...")
        password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']")))
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        
        # Wait for login to complete
        time.sleep(5)
        
        # Check if login was successful by looking for home timeline
        if "home" in driver.current_url.lower() or "x.com" in driver.current_url:
            print("  ✓ Login successful!")
        else:
            print("  ⚠ Login may have failed or requires additional verification")
            print(f"  Current URL: {driver.current_url}")
            print("\n  Waiting 30 seconds for you to complete any verification...")
            time.sleep(30)
        
        # Navigate to media tab
        print("\n[3] Navigating to @geckowo/media...")
        driver.get("https://x.com/geckowo/media")
        time.sleep(3)
        
        # Scroll and collect tweet IDs
        print("\n[4] Scrolling through media timeline...")
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        no_new_tweets_count = 0
        max_no_change_scrolls = 5
        
        while True:
            scroll_count += 1
            
            # Extract tweet IDs from current view
            tweets_before = len(all_tweet_ids)
            
            # Look for tweet links in the DOM
            tweet_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/status/']")
            
            for link in tweet_links:
                href = link.get_attribute('href')
                if href and '/status/' in href and '/geckowo/' in href:
                    match = re.search(r'/status/(\d+)', href)
                    if match:
                        all_tweet_ids.add(match.group(1))
            
            tweets_after = len(all_tweet_ids)
            new_tweets = tweets_after - tweets_before
            
            print(f"  Scroll {scroll_count}: {len(all_tweet_ids)} total tweets (+{new_tweets} new)")
            
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2.5)  # Wait for content to load
            
            # Check if we've reached the bottom
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                if new_tweets == 0:
                    no_new_tweets_count += 1
                    if no_new_tweets_count >= max_no_change_scrolls:
                        print("\n✓ Reached end of media timeline!")
                        break
                else:
                    no_new_tweets_count = 0
            else:
                no_new_tweets_count = 0
            
            last_height = new_height
            
            # Safety limit
            if scroll_count > 200:
                print("\n⚠ Reached scroll limit (200 scrolls)")
                break
        
        print("\n" + "=" * 60)
        print(f"SCRAPE RESULTS:")
        print(f"  Total unique media tweets found: {len(all_tweet_ids)}")
        
    except Exception as e:
        print(f"\n✗ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            print("\n[5] Closing browser...")
            driver.quit()
    
    # Compare with existing collection
    print("\n[6] Comparing with existing collection...")
    
    existing_ids = set()
    
    if Path('geckowo_additional_posts.json').exists():
        try:
            with open('geckowo_additional_posts.json', 'r') as f:
                for post in json.load(f):
                    existing_ids.add(str(post.get('id', '')))
        except:
            pass
    
    for batch_file in sorted(Path('geckowo_batches').glob('*.json')):
        try:
            with open(batch_file, 'r') as f:
                for post in json.load(f):
                    existing_ids.add(str(post.get('id', '')))
        except:
            pass
    
    print(f"✓ Existing collection: {len(existing_ids)} tweets")
    
    new_ids = all_tweet_ids - existing_ids
    
    print("\n" + "=" * 60)
    print(f"COLLECTION STATUS:")
    print(f"  Existing in collection: {len(existing_ids)}")
    print(f"  Newly discovered: {len(new_ids)}")
    print(f"  Total media tweets: {len(all_tweet_ids)}")
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
        
        batch_num = 10
        batch_file = f"geckowo_batches/batch_2026-01-08-{batch_num}.json"
        while Path(batch_file).exists():
            batch_num += 1
            batch_file = f"geckowo_batches/batch_2026-01-08-{batch_num}.json"
        
        with open(batch_file, 'w') as f:
            json.dump(new_posts, f, indent=2)
        
        print(f"\n✓ Saved {len(new_ids)} new tweets to {batch_file}")
        print(f"\nNext: Run pipeline to download")
        print(f"  cmd /c geckowo_pipeline.cmd")
        
        return len(new_ids)
    else:
        print("\n✓ Collection is complete!")
        return 0

if __name__ == "__main__":
    print("Twitter/X Login Scraper for @geckowo/media")
    print("=" * 60)
    print("\nPlease provide your Twitter/X credentials:")
    print("(These are only used locally and not stored)")
    print()
    
    username = input("Username (or email or phone): ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("\n✗ Username and password are required!")
    else:
        print()
        scrape_geckowo_media_logged_in(username, password)
