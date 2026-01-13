"""Generate Geckowo all comics and doodles pages"""
import json
from pathlib import Path

# Load captions
comic_captions = json.load(open('geckowo_comic_captions.json', encoding='utf-8'))
doodle_captions = json.load(open('geckowo_doodle_captions.json', encoding='utf-8'))

# Sort by ID (chronological)
comics_list = sorted(comic_captions.keys())
doodles_list = sorted(doodle_captions.keys())

def create_all_page(post_type, post_ids, captions_dict):
    """Create an 'all' page showing grid of all comics/doodles"""
    
    title_prefix = "Geckowo Comics" if post_type == 'comic' else "Geckowo Doodles"
    url_prefix = "comics" if post_type == 'comic' else "doodles"
    
    # Build grid items
    grid_items = ""
    for i, post_id in enumerate(post_ids):
        caption = captions_dict[post_id]
        if caption:
            display_title = f"#{i + 1} - {caption}"
        else:
            display_title = f"#{i + 1}"
        
        grid_items += f"""            <div class="comic-item">
                <a href="../{i + 1}/">
                    <img src="../../images/geckowo_archive/{url_prefix}s/{post_id}.jpg" alt="{display_title}">
                    <h3>{display_title}</h3>
                </a>
            </div>
"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-317947-1"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag() {{ dataLayer.push(arguments); }}
        gtag('js', new Date());
        gtag('config', 'UA-317947-1');
    </script>
    <meta charset="utf-8">
    
    <!-- HTML Meta Tags -->
    <title>{title_prefix} - All</title>
    <meta name="description" content="{title_prefix} - All">
    
    <!-- Facebook Meta Tags -->
    <meta property="og:url" content="https://goldenchaos.net/geckowo/{url_prefix}s/all/">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{title_prefix}">
    <meta property="og:description" content="Comics and doodles by Claire (Geckowo)!">
    
    <!-- Twitter Meta Tags -->
    <meta name="twitter:card" content="summary">
    <meta property="twitter:domain" content="goldenchaos.net">
    <meta property="twitter:url" content="https://goldenchaos.net/geckowo/{url_prefix}s/all/">
    <meta name="twitter:title" content="{title_prefix}">
    <meta name="twitter:description" content="Comics and doodles by Claire (Geckowo)!">
    
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="author" content="Claire (Geckowo)">
    <link rel="stylesheet" type="text/css" href="../../../style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
    <script src="https://kit.fontawesome.com/ede7ed9b9e.js" crossorigin="anonymous"></script>
    <meta name='viewport' content='initial-scale=1, viewport-fit=cover'>
    
    <script>
        document.addEventListener('DOMContentLoaded', function () {{
            if (window.sessionStorage.getItem('animated') === null) {{
                ['about', 'segmented-control', 'chevron'].forEach(function(id) {{
                    var el = document.getElementById(id);
                    if (el && el.classList) el.classList.add('animate');
                }});
                window.sessionStorage.setItem('animated', 1);
            }}
        }});
    </script>
    <style>
        .comics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 16px;
        }}
        @media (max-width: 720px) {{
            .comics-grid {{
                grid-template-columns: repeat(3, 1fr);
                gap: 4px;
                padding: 0;
            }}
            .comic-item h3 {{
                display: none;
                margin: 0;
            }}
        }}
        .comic-item {{
            text-align: center;
            margin: 0;
        }}
        .comic-item a {{
            display: block;
            text-decoration: none;
            color: inherit;
            margin: 0;
            padding: 0;
        }}
        .comic-item img {{
            width: 100%;
            height: auto;
            display: block;
            margin: 0;
            padding: 0;
        }}
        .comic-item h3 {{
            margin: 8px 0 0 0;
            font-size: 18px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="page-top white goldenchaos-btt">
        <nav>
            <a id="logo" class="back-logo" href="../../../">
                <i class="fas fa-chevron-left mobile"></i>
            </a>
            <div class="menu">
                <div>
                    <a class="social" href="https://twitch.tv/jessrappaport" target="_blank"><i class="fab fa-twitch"></i></a>
                    <a class="social" href="https://discord.gg/kp3s6ysCtn" target="_blank" style="display:none;"><i class="fab fa-discord"></i></a>
                    <a class="social" href="https://twitter.com/goldenchaos" target="_blank"><i class="fa-brands fa-x-twitter"></i></a>
                    <a class="social" href="https://instagram.com/goldenchaos" target="_blank"><i class="fab fa-instagram"></i></a>
                    <a class="social" href="https://threads.net/@goldenchaos" target="_blank"><i class="fa-brands fa-threads"></i></a>
                    <a class="social" href="https://bsky.app/profile/goldenchaos.bsky.social" target="_blank"><i class="fa-brands fa-bluesky"></i></a>
                    <a class="social" href="https://www.linkedin.com/in/goldenchaos" target="_blank"><i class="fab fa-linkedin"></i></a>
                    <a class="social" href="mailto:jess@goldenchaos.net" style="display:none;"><i class="fa fa-envelope-square"></i></a>
                </div>
                <div class="desktop">
                    <a href="../../../">
                        <i class="fas fa-chevron-left" style="font-size:14px;margin-right:3px;"></i> Back to Home
                    </a>
                </div>
            </div>
        </nav>
    </div>
    <div class="content index page" id="comic-title">
        <h1 id="comics" class="title" style="text-align:center;margin:0;text-transform:none;">All {title_prefix}</h1>
    </div>
    <div class="content page">
        <div class="comics-grid" style="margin-top: 32px;">
{grid_items}        </div>
    </div>
    <footer>
        <span>&copy; 2004-<script>document.write(new Date().getFullYear())</script> Jess Rappaport</span>
    </footer>
</body>
</html>
"""
    
    # Create folder and write file
    folder = Path(f'geckowo/{url_prefix}s/all')
    folder.mkdir(parents=True, exist_ok=True)
    
    index_file = folder / 'index.html'
    index_file.write_text(html, encoding='utf-8')
    
    print(f"✓ Created {title_prefix} all page")

# Generate all pages
create_all_page('comic', comics_list, comic_captions)
create_all_page('doodle', doodles_list, doodle_captions)

print("\n✓ All pages created successfully!")
