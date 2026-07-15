import os
import shutil
from PIL import Image

MEDIA_SRC = 'media'
MEDIA_DIST = 'docs/media'

# Standard responsive width target (1200px is excellent for desktop/mobile crispness)
MAX_WIDTH = 1200 

if not os.path.exists(MEDIA_SRC):
    os.makedirs(MEDIA_SRC)

os.makedirs(MEDIA_DIST, exist_ok=True)

def compress_image(src_path, dest_path_base):
    try:
        # If the committed file is already a WebP, skip re-compression and copy directly
        if src_path.lower().endswith('.webp'):
            shutil.copy2(src_path, f"{dest_path_base}.webp")
            print(f"Copied pre-optimized WebP: {os.path.basename(src_path)}")
            return

        with Image.open(src_path) as img:
            # Handle EXIF rotation data automatically
            img = img.convert("RGB")
            
            # Downscale only if exceptionally large to preserve crisp resolution
            if img.width > MAX_WIDTH:
                ratio = MAX_WIDTH / float(img.width)
                new_height = int(float(img.height) * float(ratio))
                img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
            
            # Save compressed WebP
            webp_path = f"{dest_path_base}.webp"
            img.save(webp_path, "WEBP", quality=82, method=6)
            
            # Save optimized fallback JPG
            jpg_path = f"{dest_path_base}.jpg"
            img.save(jpg_path, "JPEG", quality=80, optimize=True)
            
            print(f"Compressed non-WebP: {os.path.basename(src_path)} -> WebP/JPG")
    except Exception as e:
        print(f"Failed to process {src_path}: {e}")

# Crawl RAW media directory
for root, dirs, files in os.walk(MEDIA_SRC):
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            src_file_path = os.path.join(root, file)
            
            rel_path = os.path.relpath(root, MEDIA_SRC)
            target_dir = MEDIA_DIST if rel_path == '.' else os.path.join(MEDIA_DIST, rel_path)
            os.makedirs(target_dir, exist_ok=True)
            
            file_no_ext = os.path.splitext(file)[0]
            dest_file_base = os.path.join(target_dir, file_no_ext)
            
            compress_image(src_file_path, dest_file_base)
