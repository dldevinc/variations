from pilkit.lib import Image, ImageColor

try:
    # pilkit >= 2.0 compat
    from pilkit.processors.overlay import *
except ImportError:
    pass

__all__ = ['ColorOverlay']


class ColorOverlay(object):
    """
    Аналогичен pilkit-процессору ColorOverlay, но корректно работает с RGBA.
    """
    def __init__(self, color, overlay_opacity=0.5):
        self.color = color
        self.overlay_opacity = overlay_opacity

    def process(self, img):
        if isinstance(self.color, str):
            color = ImageColor.getrgb(self.color)
        else:
            color = self.color
        if len(color) == 3:
            color += (int(self.overlay_opacity * 255),)

        original = img
        overlay = Image.new('RGBA', original.size, color)
        img = Image.alpha_composite(original, overlay)
        return img
