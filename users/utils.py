import random
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from .constants import AVATAR_SIZE, AVATAR_TEXT_COLOR, COLORS


def generate_avatar(initials, size=AVATAR_SIZE):
    color = random.choice(COLORS)

    image = Image.new("RGB", (size, size), color)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", size // 2
        )
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), initials, font=font)
    x = (size - (bbox[2] - bbox[0])) // 2
    y = (size - (bbox[3] - bbox[1])) // 2
    draw.text((x, y), initials, fill=AVATAR_TEXT_COLOR, font=font)

    image_io = BytesIO()
    image.save(image_io, format="PNG")
    return ContentFile(image_io.getvalue(), f"avatar_{initials}.png")
