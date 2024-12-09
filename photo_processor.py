from PIL import Image
import os
from werkzeug.utils import secure_filename

def process_and_save_image(photo, upload_folder, target_size=(800, 600), quality=85):
    """
    Process and save an uploaded image with consistent sizing
    
    Args:
    - photo: FileStorage object from Flask
    - upload_folder: Directory to save processed images
    - target_size: Tuple of (width, height) to resize images
    - quality: JPEG compression quality (1-95)
    
    Returns:
    - filename of processed image
    """
    # Open the image
    img = Image.open(photo)
    
    # Convert to RGB mode to handle various image formats
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize image while maintaining aspect ratio
    img.thumbnail(target_size, Image.LANCZOS)
    
    # Create a new image with solid background if needed
    if img.size != target_size:
        background = Image.new('RGB', target_size, (255, 255, 255))  # White background
        offset = ((target_size[0] - img.size[0]) // 2, 
                  (target_size[1] - img.size[1]) // 2)
        background.paste(img, offset)
        img = background
    
    # Generate a unique filename
    filename = secure_filename(f"{uuid.uuid4()}_{photo.filename}")
    filepath = os.path.join(upload_folder, filename)
    
    # Save the processed image
    img.save(filepath, 'JPEG', quality=quality, optimize=True)
    
    return filename