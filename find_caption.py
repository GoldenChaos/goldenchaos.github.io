"""Debug script to find specific caption in post"""
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

post_id = "1973545988309786897"
caption = "It's spooky month!"
url = f"https://x.com/geckowo/status/{post_id}"

print(f"Fetching: {url}")
print(f"Looking for: '{caption}'\n")

try:
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    html = resp.text
    
    # Check if caption exists in HTML
    if caption in html:
        print(f"✓ Found caption in HTML!")
        
        # Find context around it
        idx = html.find(caption)
        context_start = max(0, idx - 200)
        context_end = min(len(html), idx + len(caption) + 200)
        context = html[context_start:context_end]
        
        print(f"\nContext (400 chars around caption):")
        print("..." + context + "...")
        
    else:
        print(f"✗ Caption NOT found in static HTML")
        
        # Save HTML for inspection
        with open('spooky_post.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✓ Saved full HTML to spooky_post.html for inspection")
        
        # Try to find similar text
        if "spooky" in html.lower():
            print("⚠ Found 'spooky' somewhere in page")
        if "month" in html.lower():
            print("⚠ Found 'month' somewhere in page")
    
    print(f"\nHTML size: {len(html)} bytes")
    
except Exception as e:
    print(f"Error: {e}")
