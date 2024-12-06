import qrcode

def generate_qr(location_id, base_url):
    qr_url = f"{base_url}/location/{location_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img.save(f"static/location_{location_id}.png")

if __name__ == "__main__":
    base_url = "http://192.168.86.21:5000" # Replace with your actual base URL
    location_id = 1
    generate_qr(location_id, base_url)
