from io import BytesIO
from PIL import Image

def to_png_bytes(pil_image: Image.Image) -> bytes:
    buf = BytesIO()
    pil_image.save(buf, format="PNG")
    return buf.getvalue()