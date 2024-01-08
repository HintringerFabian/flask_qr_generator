import base64
import io

import qrcode
from PIL import ImageDraw
from qrcode.main import QRCode


def generate_qr_code(data, back_color: str = "white"):
    # Create a QR code object with a larger size and higher error correction
    qr = QRCode(version=3, box_size=10, border=2, error_correction=qrcode.constants.ERROR_CORRECT_H)

    # Add the data to the QR code object
    qr.add_data(data)

    # Make the QR code
    qr.make(fit=True)

    # Make the QR code using the PIL backend
    img = qr.make_image(fill_color="black", back_color=back_color, make_image=ImageDraw.Image)
    return img


def encode_base64_in_memory(qr):
    img_data = io.BytesIO()
    qr.save(img_data, "PNG")
    encoded_img_data = base64.b64encode(img_data.getvalue())
    return encoded_img_data


def decode_base64(data):
    img_data = base64.b64decode(data)
    return img_data
