from PIL import Image
import os

# Directory paths
bald_dir = "images/comics/bald"
output_dir = "images/comics/bald/thumb"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Thumbnail width
thumb_width = 500

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
    
    # Calculate new height to maintain aspect ratio
    aspect_ratio = img.height / img.width
    thumb_height = int(thumb_width * aspect_ratio)
    
    # Resize the image
    thumb_img = img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
    
    # Generate output filename
    base_name = os.path.splitext(comic)[0]
    output_filename = f"{base_name}-thumb.png"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save the thumbnail
    thumb_img.save(output_path, "PNG", optimize=True)
    print(f"Created: {output_path} ({thumb_width}x{thumb_height}px)")

print("Done! All bald thumbnails have been generated.")
