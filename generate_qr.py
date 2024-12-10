import qrcode
from PIL import Image

def generate_qr(base_url, scale_factor=4):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  # This controls the size of each box in the QR code
        border=4,
    )
    qr.add_data(base_url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Calculate the new size based on the scale factor
    new_size = (img.size[0] * scale_factor, img.size[1] * scale_factor)
    
    # Resize the image to a higher resolution
    img = img.resize(new_size, Image.LANCZOS)
    
    img.save(f"static/website_high_res.png")

if __name__ == "__main__":
    base_url = "https://jemslocale.onrender.com/"  # Replace with your actual base URL
    generate_qr(base_url)
