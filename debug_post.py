"""Debug script to check actual HTML structure of a Twitter post"""
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Fetch a sample post
post_id = "1920811774787346745"  # One that might have a caption
url = f"https://x.com/geckowo/status/{post_id}"

print(f"Fetching: {url}\n")

try:
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    html = resp.text
    
    # Save to file for inspection
    with open('sample_post.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Look for og:description tag
    import re
    og_pattern = r'<meta\s+property="og:description"\s+content="([^"]*)"'
    og_match = re.search(og_pattern, html)
    
    print(f"og:description found: {og_match is not None}")
    if og_match:
        print(f"Content: {og_match.group(1)[:200]}")
    
    # Look for any description
    desc_pattern = r'<meta\s+name="description"\s+content="([^"]*)"'
    desc_match = re.search(desc_pattern, html)
    
    print(f"description found: {desc_match is not None}")
    if desc_match:
        print(f"Content: {desc_match.group(1)[:200]}")
    
    # Look for any meta tags with content
    all_meta = re.findall(r'<meta[^>]+content="([^"]{30,})"', html)
    print(f"\nFound {len(all_meta)} meta tags with content longer than 30 chars:")
    for i, content in enumerate(all_meta[:5]):
        print(f"  {i+1}. {content[:100]}...")
    
    print("\n✓ Saved full HTML to sample_post.html for inspection")
    
except Exception as e:
    print(f"Error: {e}")
