import base64
import io
import uuid as uuid_module
from enum import Enum

import qrcode
from PIL import ImageDraw
from qrcode.main import QRCode

from database import save_to_db


# Enum for domain status
class DomainStatus(Enum):
    VALID = "VALID"
    TRAILING_SLASH = "VALID_WITH_TRAILING_SLASH"
    NO_DOMAIN = "UNDEFINED"
    HTTP_NOT_SUPPORTED = "INVALID"
    DOMAIN_MALFORMED = "INVALID"


class QRGenerator:
    def __init__(self, domain: str, database_name: str):
        self.database_name = database_name

        domain_status = self.__validate_domain(domain)

        if domain_status != "VALID" and domain_status != "VALID_WITH_TRAILING_SLASH":
            self.__throw_domain_status_error(domain_status)

        if domain_status is DomainStatus.VALID:
            self.domain = domain + "/"
        else:
            self.domain = domain
            
        self.domain_status = domain_status

    def save_uuid_to_database(self, uuid, url_data):
        save_to_db(uuid, url_data, self.database_name)

    def generate_qr_code_data(self, url_data) -> str:
        uuid = str(uuid_module.uuid4())
        domain = self.domain + uuid

        self.save_uuid_to_database(uuid, url_data)
        
        return domain

    @staticmethod
    def __generate_uuid() -> str:
        return str(uuid_module.uuid4())

    @staticmethod
    def decode_base64(data):
        img_data = base64.b64decode(data)
        return img_data

    @staticmethod
    def encode_base64_in_memory(qr):
        img_data = io.BytesIO()
        qr.save(img_data, "PNG")
        encoded_img_data = base64.b64encode(img_data.getvalue())
        return encoded_img_data

    @staticmethod
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

    @staticmethod
    def __throw_domain_status_error(domain_status: DomainStatus):
        match domain_status:
            case DomainStatus.NO_DOMAIN:
                raise ValueError("No domain was provided")
            case DomainStatus.HTTP_NOT_SUPPORTED:
                raise ValueError("Only HTTPS is supported")
            case DomainStatus.DOMAIN_MALFORMED:
                raise ValueError("The domain is malformed")
            case DomainStatus.TRAILING_SLASH:
                raise ValueError("The domain should not end with a trailing slash")

    @staticmethod
    def __validate_domain(domain: str) -> DomainStatus:
        if domain is None:
            return DomainStatus.NO_DOMAIN

        if not domain.startswith("http"):
            return DomainStatus.DOMAIN_MALFORMED

        if not domain.startswith("https"):
            return DomainStatus.HTTP_NOT_SUPPORTED

        if not domain.startswith("https://"):
            return DomainStatus.DOMAIN_MALFORMED

        if domain.endswith("/"):
            return DomainStatus.TRAILING_SLASH

        return DomainStatus.VALID
