import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
import os
import platform


def generate_avatar(initials, size=200):
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    color = random.choice(colors)
    
    image = Image.new('RGB', (size, size), color)
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 120)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), initials, font=font)
    x = (size - (bbox[2] - bbox[0])) // 2
    y = (size - (bbox[3] - bbox[1])) // 2
    draw.text((x, y), initials, fill='#FFFFFF', font=font)
    
    image_io = BytesIO()
    image.save(image_io, format='PNG')
    return ContentFile(image_io.getvalue(), f'avatar_{initials}.png')
