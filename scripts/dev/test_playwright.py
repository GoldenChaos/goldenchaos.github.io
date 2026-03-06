"""Test Playwright on the spooky post"""
import asyncio
from playwright.async_api import async_playwright

async def test():
    post_id = "1973545988309786897"
    url = f"https://x.com/geckowo/status/{post_id}"
    
    print(f"Fetching: {url}\n")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Wait for page to load with shorter timeout
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(3000)
            
            # Get article text
            article = await page.query_selector('article')
            if article:
                tweet_text = await article.inner_text()
                
                print("Full article text:")
                print(tweet_text)
                print("\n" + "="*60 + "\n")
                
                # Split into lines
                lines = tweet_text.split('\n')
                print(f"Total lines: {len(lines)}\n")
                for i, line in enumerate(lines[:25]):
                    print(f"{i:2d}: {line}")
            else:
                print("Could not find article element")
            
            await browser.close()
    
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
