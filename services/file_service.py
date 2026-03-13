import os
import shutil
from PIL import Image

MAX_DIM = 1920

class FileService:
    @staticmethod
    def optimize_image(input_path: str) -> str:
        try:
            # Check basic extensions before opening to save processing
            name_lower = input_path.lower()
            if not (name_lower.endswith(".jpg") or name_lower.endswith(".jpeg") or name_lower.endswith(".png")):
                return input_path

            with Image.open(input_path) as img:
                width, height = img.size
                max_side = max(width, height)
                
                if max_side <= MAX_DIM:
                    return input_path
                    
                scale = MAX_DIM / max_side
                new_width = int(round(width * scale))
                new_height = int(round(height * scale))
                
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                directory = os.path.dirname(input_path)
                filename = os.path.basename(input_path)
                out_path = os.path.join(directory, f"opt_{filename}")
                
                if name_lower.endswith(".jpg") or name_lower.endswith(".jpeg"):
                    if img_resized.mode in ("RGBA", "P"):
                        img_resized = img_resized.convert("RGB")
                    img_resized.save(out_path, format="JPEG", quality=60, optimize=True)
                elif name_lower.endswith(".png"):
                    img_resized.save(out_path, format="PNG", optimize=True)
                else:
                    return input_path
                    
                return out_path
        except Exception as e:
            print(f"Error optimizing image: {e}")
            return input_path

    @staticmethod
    def cleanup_empty_directories(base_cleanup_path: str):
        """Recursively cleans up empty directories up the tree."""
        try:
            if os.path.exists(base_cleanup_path) and not os.listdir(base_cleanup_path):
                shutil.rmtree(base_cleanup_path)
        except Exception as e:
            print(f"Error cleaning empty directory {base_cleanup_path}: {e}")
