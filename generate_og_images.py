from PIL import Image
import os

# Directory paths
comics_dir = "images/comics"
output_dir = "images/comics/og"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Social media standard sizes (width x height)
sizes = {
    "og": (1200, 630),  # Open Graph standard (Twitter, Facebook, LinkedIn, etc.)
}

# Comic images to process
comics = [
    "1_alopecia.png",
    "2_latte_art.png",
    "3_yuri_mustache.png",
    "4_dont_tell_me_my_age.png"
]

# Background color (white)
background_color = (255, 255, 255)

for comic in comics:
    input_path = os.path.join(comics_dir, comic)
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        continue
    
    # Open the original image
    img = Image.open(input_path)
    
    for size_name, (width, height) in sizes.items():
        # Create a new image with the target size and white background
        new_img = Image.new("RGB", (width, height), background_color)
        
        # Calculate aspect ratios
        original_ratio = img.width / img.height
        target_ratio = width / height
        
        # Calculate dimensions to fit the image into the new size while maintaining aspect ratio
        if original_ratio > target_ratio:
            # Image is wider, fit by width
            new_width = width
            new_height = int(width / original_ratio)
        else:
            # Image is taller, fit by height
            new_height = height
            new_width = int(height * original_ratio)
        
        # Resize the image
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Calculate position to center the image
        x_offset = (width - new_width) // 2
        y_offset = (height - new_height) // 2
        
        # Paste the resized image onto the new image
        new_img.paste(resized_img, (x_offset, y_offset))
        
        # Generate output filename
        base_name = os.path.splitext(comic)[0]
        output_filename = f"{base_name}-og.png"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save the new image
        new_img.save(output_path, "PNG")
        print(f"Created: {output_path}")

print("Done! All og:images have been generated.")
