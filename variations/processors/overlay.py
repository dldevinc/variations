from pilkit.lib import Image, ImageColor

from ..typing import Color

__all__ = ["ColorOverlay"]


class ColorOverlay:
    """
    Аналогичен pilkit-процессору ColorOverlay, но корректно работает с RGBA.

    :param color: `ImageColor` instance to overlay on the original image
    :param overlay_opacity: Define the fusion factor for the overlay mask
    """
    def __init__(self, color: Color, overlay_opacity=0.5):
        if isinstance(color, str):
            color = ImageColor.getrgb(color)

        if len(color) == 3:
            color += (int(overlay_opacity * 255 + 0.5),)

        self.color = color

    def process(self, img):
        overlay = Image.new("RGBA", img.size, self.color)
        return Image.alpha_composite(img.convert("RGBA"), overlay)
