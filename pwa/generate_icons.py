from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    img = Image.new('RGB', (size, size), color='#4f46e5')
    d = ImageDraw.Draw(img)
    
    # Add a simple "B" in the center
    try:
        font_size = size // 2
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "B"
    text_bbox = d.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position = ((size - text_width) // 2, (size - text_height) // 2)
    d.text(position, text, fill="white", font=font)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)

# Create different icon sizes
if __name__ == "__main__":
    sizes = [192, 512]
    for size in sizes:
        output_path = f"static/images/icon-{size}x{size}.png"
        create_icon(size, output_path)
        print(f"Created {output_path}")
