"""Re-attempt caption extraction for doodles that still have no captions"""
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
            except Exception:
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
    # Load existing captions
    captions_file = Path("geckowo_doodle_captions.json")
    
    if not captions_file.exists():
        print("Captions file not found!")
        return
    
    with open(captions_file, 'r', encoding='utf-8') as f:
        captions = json.load(f)
    
    # Find doodles with no captions
    no_caption_posts = [post_id for post_id, caption in captions.items() if caption is None]
    
    print(f"Double-checking {len(no_caption_posts)} doodles without captions\n")
    
    success_count = 0
    
    for i, post_id in enumerate(no_caption_posts, 1):
        print(f"[{i}/{len(no_caption_posts)}] Fetching {post_id}...")
        
        try:
            caption = await get_post_caption(post_id)
            
            if caption:
                captions[post_id] = caption
                success_count += 1
                print(f"  ✓ '{caption[:60]}{'...' if len(caption) > 60 else ''}'")
            else:
                print(f"  ∅ No caption")
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:50]}")
        
        # Save every 5 posts to ensure no data loss
        if i % 5 == 0:
            with open(captions_file, 'w', encoding='utf-8') as f:
                json.dump(captions, f, indent=2, ensure_ascii=False)
            found = sum(1 for v in captions.values() if v is not None)
            print(f"  Progress saved ({i}/{len(no_caption_posts)}) - Total found: {found}\n")
        
        # Restart browser every 20 posts to prevent resource issues
        if i % 20 == 0:
            await close_browser()
            await asyncio.sleep(2)
    
    # Final save
    with open(captions_file, 'w', encoding='utf-8') as f:
        json.dump(captions, f, indent=2, ensure_ascii=False)
    
    # Close browser
    await close_browser()
    
    print(f"\n{'='*60}")
    print(f"Complete!")
    print(f"  ✓ New captions found: {success_count}")
    
    # Final stats
    total = len(captions)
    with_captions = sum(1 for v in captions.values() if v is not None)
    print(f"\nFinal stats: {with_captions}/{total} captions ({with_captions/total*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main())
