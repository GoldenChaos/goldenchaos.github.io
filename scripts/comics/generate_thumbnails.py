from PIL import Image
import os

# Directory paths
comics_dir = "images/comics"
output_dir = "images/comics/thumb"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Thumbnail height (maintain aspect ratio, allow wide comics to exceed 500px wide)
thumb_height_target = 500

# Comic images to process
comics = [
    "1_alopecia.png",
    "2_latte_art.png",
    "3_yuri_mustache.png",
    "3.1_important_psa.png",
    "4_dont_tell_me_my_age.png",
    "5_freckles.png",
    "6_gay.png",
    "7_ally.png",
    "8_robot.png",
    "9_from_scratch.png",
    "10_dissociation.png",
    "11_warhammer_number.png",
    "12_comic_rooms.png",
    "13_new_outfit.png"
]

for comic in comics:
    input_path = os.path.join(comics_dir, comic)
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        continue
    
    # Open the original image
    img = Image.open(input_path)
    
    # Scale every thumbnail to a 500px height while maintaining aspect ratio.
    img_width, img_height = img.size
    aspect_ratio = img_width / img_height
    thumb_height = thumb_height_target
    thumb_width = int(thumb_height_target * aspect_ratio)
    
    # Resize the image
    thumb_img = img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
    
    # Generate output filename
    base_name = os.path.splitext(comic)[0]
    output_filename = f"{base_name}-thumb.png"
    output_path = os.path.join(output_dir, output_filename)
    
    # Save the thumbnail
    thumb_img.save(output_path, "PNG", optimize=True)
    print(f"Created: {output_path} ({thumb_width}x{thumb_height}px, height 500)")

print("Done! All thumbnails have been generated.")
