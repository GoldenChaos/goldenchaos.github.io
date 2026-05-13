from PIL import Image
import os

# Directory paths
comics_dir = "images/comics"
output_dir = "images/comics/thumb"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Thumbnail max dimensions (fit within 500x500, maintain aspect ratio)
thumb_max = 500

# Comic images to process
comics = [
    "1_alopecia.png",
    "2_latte_art.png",
    "3_yuri_mustache.png",
    "4_dont_tell_me_my_age.png",
    "5_freckles.png",
    "6_gay.png",
    "7_ally.png",
    "8_robot.png"
]

for comic in comics:
    input_path = os.path.join(comics_dir, comic)
    
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

print("Done! All thumbnails have been generated.")
