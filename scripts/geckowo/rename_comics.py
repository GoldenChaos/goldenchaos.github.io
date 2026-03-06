import os
import json

# Load metadata
with open('data/geckowo/geckowo_comics_metadata.json', 'r') as f:
    comics = json.load(f)

comics_folder = 'geckowo_comics'

print(f"Renaming {len(comics)} comics...")

for comic in comics:
    old_filename = comic['filename']
    old_path = os.path.join(comics_folder, old_filename)
    
    # Extract status_id from filename
    status_id = comic['status_id']
    
    # Create new filename with reverse-chronological number
    new_filename = f"{comic['number']:04d} - {status_id}.jpg"
    new_path = os.path.join(comics_folder, new_filename)
    
    if os.path.exists(old_path) and old_filename != new_filename:
        # Use replace to overwrite if the destination already exists (handles prior numbered duplicates)
        os.replace(old_path, new_path)
        print(f"#{comic['number']:04d}: {old_filename} -> {new_filename}")
        
        # Update metadata
        comic['filename'] = new_filename

# Save updated metadata
with open('data/geckowo/geckowo_comics_metadata.json', 'w') as f:
    json.dump(comics, f, indent=2)

print(f"\n✓ All comics renamed!")
print(f"✓ Metadata updated in data/geckowo/geckowo_comics_metadata.json")

