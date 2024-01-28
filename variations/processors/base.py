from pilkit.lib import Image, ImageColor
from pilkit.processors.base import (
    Adjust,
    Anchor,
    ProcessorPipeline,
    Reflection,
    Transpose,
)

from ..typing import Color

__all__ = [
    "ProcessorPipeline",
    "Adjust",
    "Reflection",
    "Transpose",
    "Anchor",
    "MakeOpaque",
]


class MakeOpaque:
    """
    Подобен pilkit-процессору MakeOpaque, но работает с изображениями
    любого типа, включая RGB, LA и P.
    """

    def __init__(self, background_color: Color = "#FFFFFF"):
        if isinstance(background_color, str):
            background_color = ImageColor.getrgb(background_color)
        self.background_color = background_color[:3]

    def process(self, img):
        has_transparency = img.info.get("transparency") is not None
        if not has_transparency and (img.mode not in ("LA", "PA", "RGBA")):
            return img

        if img.mode == "P" and has_transparency:
            img = img.convert("RGBA")

        new_img = Image.new("RGB", img.size, self.background_color)
        new_img.paste(img, img)
        return new_img
