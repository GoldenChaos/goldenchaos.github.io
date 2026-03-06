"""Attempt to extract captions for skipped doodles with enhanced error handling"""
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

async def get_post_caption_enhanced(post_id: str) -> str | None:
    """Fetch caption with multiple fallback strategies"""
    url = f"https://x.com/geckowo/status/{post_id}"
    
    try:
        browser = await get_browser()
        page = None
        
        try:
            page = await browser.new_page()
            
            try:
                # Try with longer timeout and network idle wait
                await page.goto(url, wait_until="networkidle", timeout=15000)
                await page.wait_for_timeout(2000)
                
                # Strategy 1: Try article selector (standard approach)
                article = await page.query_selector('article')
                if article:
                    tweet_text = await article.inner_text()
                    lines = tweet_text.split('\n')
                    
                    if len(lines) > 2:
                        caption = lines[2].strip()
                        if caption and len(caption) > 3:
                            if not any(skip in caption for skip in ['AM', 'PM', 'Views', 'Read', 'replies']):
                                return caption
                
                # Strategy 2: Try div with data-testid="tweet" (alternative selector)
                tweet_div = await page.query_selector('div[data-testid="tweet"]')
                if tweet_div:
                    tweet_text = await tweet_div.inner_text()
                    lines = tweet_text.split('\n')
                    
                    if len(lines) > 2:
                        caption = lines[2].strip()
                        if caption and len(caption) > 3:
                            if not any(skip in caption for skip in ['AM', 'PM', 'Views', 'Read', 'replies']):
                                return caption
                
                # Strategy 3: Try p tags (text container approach)
                p_tags = await page.query_selector_all('article p')
                if p_tags and len(p_tags) > 0:
                    # First p tag after metadata is usually caption
                    text = await p_tags[0].inner_text()
                    if text and len(text) > 3:
                        if not any(skip in text for skip in ['AM', 'PM', 'Views', 'Read', 'replies']):
                            return text.strip()
                
                return None
            
            except asyncio.TimeoutError:
                print(f"    ⏱️ Timeout after 15s")
                return None
            except Exception as e:
                print(f"    ℹ️ Strategy failed: {str(e)[:40]}")
                return None
        
        finally:
            if page:
                try:
                    await page.close()
                except:
                    pass
        
    except Exception as e:
        print(f"    ✗ Browser error: {str(e)[:40]}")
        return None

async def main():
    # Load existing captions
    captions_file = Path("data/geckowo/geckowo_doodle_captions.json")
    
    if not captions_file.exists():
        print("Captions file not found!")
        return
    
    with open(captions_file, 'r', encoding='utf-8') as f:
        captions = json.load(f)
    
    # Identify skipped posts
    skip_posts = {'1904325170447393018', '1859113446287003915', '1909972205053542681', '1934320424961073523'}
    skipped_entries = {post_id: captions.get(post_id) for post_id in skip_posts if post_id in captions}
    
    print(f"Attempting to extract captions for {len(skipped_entries)} skipped posts\n")
    
    success_count = 0
    
    for i, post_id in enumerate(skip_posts, 1):
        if post_id not in captions:
            print(f"[{i}/4] Post {post_id} not in file, skipping")
            continue
        
        print(f"[{i}/4] Attempting {post_id}...")
        
        try:
            caption = await get_post_caption_enhanced(post_id)
            
            if caption:
                captions[post_id] = caption
                success_count += 1
                print(f"  ✓ '{caption[:60]}{'...' if len(caption) > 60 else ''}'")
            else:
                print(f"  ∅ No caption found")
        
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:50]}")
        
        # Pause between requests to avoid overload
        await asyncio.sleep(1)
    
    # Close browser
    await close_browser()
    
    # Save updated captions
    with open(captions_file, 'w', encoding='utf-8') as f:
        json.dump(captions, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Attempt complete!")
    print(f"  ✓ New captions found: {success_count}")
    
    # Final stats
    total = len(captions)
    with_captions = sum(1 for v in captions.values() if v is not None)
    print(f"\nFinal stats: {with_captions}/{total} captions ({with_captions/total*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main())

