from pilkit.lib import ImageFilter

try:
    from PIL import ImageOps
except ImportError:
    import ImageOps

try:
    from stackblur import StackBlur as StackBlurFilter

    STACK_BLUR_SUPPORT = True
except ImportError:
    STACK_BLUR_SUPPORT = False
    StackBlurFilter = None
    StackBlur = None

__all__ = [
    "Grayscale",
    "GaussianBlur",
    "BoxBlur",
    "STACK_BLUR_SUPPORT",
    "StackBlur",
]


class Grayscale:
    def process(self, img):
        return img.convert("LA")


class GaussianBlur:
    """
    Can't be applied to 1-bit images.
    """
    def __init__(self, radius=2):
        self.radius = radius

    def process(self, img):
        if img.mode == "P":
            img = img.convert()
        return img.filter(ImageFilter.GaussianBlur(self.radius))


class BoxBlur:
    """
    Can't be applied to 1-bit images.
    """
    def __init__(self, radius):
        self.radius = radius

    def process(self, img):
        if img.mode == "P":
            img = img.convert()
        return img.filter(ImageFilter.BoxBlur(self.radius))


if STACK_BLUR_SUPPORT:

    class StackBlur:
        def __init__(self, radius):
            self.radius = radius

        def process(self, img):
            if img.mode == "1":
                img = img.convert("L")
            elif img.mode == "P":
                img = img.convert()
            return img.filter(StackBlurFilter(self.radius))
