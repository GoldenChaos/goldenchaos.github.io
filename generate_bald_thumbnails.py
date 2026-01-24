from PIL import Image
import os

# Directory paths
bald_dir = "images/comics/bald"
output_dir = "images/comics/bald/thumb"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Thumbnail max dimensions (fit within 500x500, maintain aspect ratio)
thumb_max = 500

# Bald comic images to process
bald_comics = [
    "6_gay-bald.png"
]

for comic in bald_comics:
    input_path = os.path.join(bald_dir, comic)
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        continue
    
    # Open the original image
    img = Image.open(input_path)
    
    # Calculate dimensions to fit within 500x500 while maintaining aspect ratio
    img_width, img_height = img.size
    aspect_ratio = img_width / img_height
    
    if aspect_ratio > 1:  # Wider than tall
        thumb_width = thumb_max
        thumb_height = int(thumb_max / aspect_ratio)
    else:  # Taller than wide
        thumb_height = thumb_max
        thumb_width = int(thumb_max * aspect_ratio)
    
    # Resize the image
    thumb_img = img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
    
    # Generate output filename
    base_name = os.path.splitext(comic)[0]
    output_filename = f"{base_name}-thumb.png"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save the thumbnail
    thumb_img.save(output_path, "PNG", optimize=True)
    print(f"Created: {output_path} ({thumb_width}x{thumb_height}px, fits within 500x500)")

print("Done! All bald thumbnails have been generated.")
