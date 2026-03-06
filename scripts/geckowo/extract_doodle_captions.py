"""Extract captions from Twitter posts using Playwright for JavaScript rendering"""
from pathlib import Path
import asyncio
import json
from playwright.async_api import async_playwright

# Global browser instance
_browser = None

async def get_browser():
    """Get or create a browser instance"""
    global _browser
    if _browser is None:
        p = await async_playwright().__aenter__()
        _browser = await p.chromium.launch(headless=True)
    return _browser

async def close_browser():
    """Close browser instance"""
    global _browser
    if _browser:
        await _browser.close()
        _browser = None

async def get_post_caption(post_id: str) -> str | None:
    """Fetch the caption text from a Twitter/X post using browser rendering"""
    url = f"https://x.com/geckowo/status/{post_id}"
    
    try:
        browser = await get_browser()
        page = None
        
        try:
            # Create page with error handling
            page = await browser.new_page()
            
            try:
                # Navigate to post with timeout handling
                await page.goto(url, wait_until="domcontentloaded", timeout=10000)
                await page.wait_for_timeout(1000)
                
                # Find the article element with tweet content
                article = await page.query_selector('article')
                if not article:
                    return None
                
                tweet_text = await article.inner_text()
                lines = tweet_text.split('\n')
                
                # The caption is typically at line 2 (after username lines)
                if len(lines) > 2:
                    caption = lines[2].strip()
                    
                    # Ignore very short strings
                    if caption and len(caption) > 3:
                        # Make sure it's not a timestamp or metric
                        if not any(skip in caption for skip in ['AM', 'PM', 'Views', 'Read', 'replies']):
                            return caption
                
                return None
            
            except asyncio.TimeoutError:
                return None
            except Exception as e:
                return None
        
        finally:
            if page:
                try:
                    await page.close()
                except:
                    pass
        
    except Exception:
        return None

async def main():
    # Get all doodle files
    doodles_dir = Path("geckowo_archive/doodles")
    doodle_files = sorted(doodles_dir.glob("*.jpg"))
    
    print(f"Found {len(doodle_files)} doodles")
    print("Extracting captions with browser rendering...\n")
    
    # Load existing captions if any
    captions_file = Path("data/geckowo/geckowo_doodle_captions.json")
    if captions_file.exists():
        with open(captions_file, 'r', encoding='utf-8') as f:
            captions = json.load(f)
        print(f"Loaded {len(captions)} existing captions\n")
    else:
        captions = {}
    
    # Extract post IDs from filenames
    post_ids = [f.stem for f in doodle_files]
    
    # Posts known to be problematic (skip them)
    skip_posts = {'1904325170447393018', '1859113446287003915', '1909972205053542681', '1934320424961073523'}  # Posts that cause crash
    
    # Process each post
    success_count = 0
    skip_count = 0
    empty_count = 0
    error_count = 0
    
    for i, post_id in enumerate(post_ids, 1):
        # Skip if already have caption
        if post_id in captions:
            skip_count += 1
            continue
        
        # Skip known problematic posts
        if post_id in skip_posts:
            captions[post_id] = None
            skip_count += 1
            print(f"[{i}/{len(post_ids)}] Skipping {post_id} (known issue)")
            continue
        
        print(f"[{i}/{len(post_ids)}] Fetching {post_id}...")
        
        try:
            caption = await get_post_caption(post_id)
            
            if caption:
                captions[post_id] = caption
                success_count += 1
                print(f"  ✓ '{caption[:60]}{'...' if len(caption) > 60 else ''}'")
            else:
                captions[post_id] = None
                empty_count += 1
                print(f"  ∅ No caption")
        except Exception as e:
            captions[post_id] = None
            error_count += 1
            print(f"  ✗ Error: {str(e)[:50]}")
        
        # Save every post to ensure no data loss
        if i % 5 == 0:
            with open(captions_file, 'w', encoding='utf-8') as f:
                json.dump(captions, f, indent=2, ensure_ascii=False)
            found = sum(1 for v in captions.values() if v is not None)
            print(f"  Progress saved ({i}/{len(post_ids)}) - Found: {found}\n")
        
        # Restart browser every 10 posts to prevent resource issues
        if i % 10 == 0:
            await close_browser()
            await asyncio.sleep(2)  # Brief pause
    
    # Final save
    with open(captions_file, 'w', encoding='utf-8') as f:
        json.dump(captions, f, indent=2, ensure_ascii=False)
    
    # Close browser
    await close_browser()
    
    print(f"\n{'='*60}")
    print(f"Complete!")
    print(f"  ✓ Found captions: {success_count}")
    print(f"  ○ Already had: {skip_count}")
    print(f"  ∅ No caption: {empty_count}")
    print(f"  ✗ Errors: {error_count}")
    print(f"\nTotal captions found: {sum(1 for v in captions.values() if v is not None)}")

if __name__ == "__main__":
    asyncio.run(main())

