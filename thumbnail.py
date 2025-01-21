"""
Create Thumbnail using title
"""

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
import textwrap
import re
import os
from pathlib import Path


def name_normalize(name: str) -> str:
    name = re.sub(r'[?\\"%*,:|<>]', "", name)
    name = re.sub(r"( [w,W]\s?\/\s?[o,O,0])", r" without", name)
    name = re.sub(r"( [w,W]\s?\/)", r" with", name)
    name = re.sub(r"(\d+)\s?\/\s?(\d+)", r"\1 of \2", name)
    name = re.sub(r"(\w+)\s?\/\s?(\w+)", r"\1 or \2", name)
    name = re.sub(r"\/", r"", name)
    return name


def getsize(font: ImageFont.ImageFont | FreeTypeFont, text: str):
    left, top, right, bottom = font.getbbox(text)
    width = right - left
    height = bottom - top
    return width, height


def getheight(font: ImageFont.ImageFont | FreeTypeFont, text: str):
    _, height = getsize(font, text)
    return height


def create_fancy_thumbnail(image, text, text_color, padding, wrap=35):
    print(f"Creating fancy thumbnail for: {text}")
    font_title_size = 47
    font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_title_size)
    image_width, image_height = image.size
    lines = textwrap.wrap(text, width=wrap)
    y = (
        (image_height / 2)
        - (((getheight(font, text) + (len(lines) * padding) / len(lines)) * len(lines)) / 2)
        + 30
    )
    draw = ImageDraw.Draw(image)

    username_font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 30)
    draw.text(
        (205, 825),
        "Reddit Stories",
        font=username_font,
        fill=text_color,
        align="left",
    )

    if len(lines) == 3:
        lines = textwrap.wrap(text, width=wrap + 10)
        font_title_size = 40
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_title_size)
        y = (
            (image_height / 2)
            - (((getheight(font, text) + (len(lines) * padding) / len(lines)) * len(lines)) / 2)
            + 35
        )
    elif len(lines) == 4:
        lines = textwrap.wrap(text, width=wrap + 10)
        font_title_size = 35
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_title_size)
        y = (
            (image_height / 2)
            - (((getheight(font, text) + (len(lines) * padding) / len(lines)) * len(lines)) / 2)
            + 40
        )
    elif len(lines) > 4:
        lines = textwrap.wrap(text, width=wrap + 10)
        font_title_size = 30
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_title_size)
        y = (
            (image_height / 2)
            - (((getheight(font, text) + (len(lines) * padding) / len(lines)) * len(lines)) / 2)
            + 30
        )

    for line in lines:
        draw.text((120, y), line, font=font, fill=text_color, align="left")
        y += getheight(font, line) + padding

    return image



# reddit_id= "qwerty"
# title_template = Image.open("assets/title_template.png")

# title = "Mysteries of the Forest: Encounters as a Search and Rescue Officer"

# title = name_normalize(title)

# font_color = "#000000"
# padding = 5
# Path(f"assets/temp/{reddit_id}/png").mkdir(parents=True, exist_ok=True)
# # create_fancy_thumbnail(image, text, text_color, padding
# title_img = create_fancy_thumbnail(title_template, title, font_color, padding)
# title_img.save(f"assets/temp/{reddit_id}/png/title.png")