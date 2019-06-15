try:
    from PIL import ImageOps
except ImportError:
    import ImageOps

from pilkit.lib import ImageFilter

__all__ = ['Grayscale', 'Posterize', 'Solarize', 'Blur', 'Sharpen', 'Smooth',
           'EdgeEnhance', 'UnsharpMask', 'BoxBlur', 'GaussianBlur']


class Grayscale:
    def process(self, img):
        return img.convert('LA').convert('RGBA')


class Posterize:
    """
    Can only be applied to "L" and "RGB" images.
    """
    def __init__(self, bits):
        self.bits = bits

    def process(self, img):
        return ImageOps.posterize(img, self.bits)


class Solarize:
    """
    Can only be applied to "L" and "RGB" images.
    """
    def __init__(self, threshold=128):
        self.threshold = threshold

    def process(self, img):
        return ImageOps.solarize(img, self.threshold)


class Blur:
    def process(self, img):
        return img.filter(ImageFilter.BLUR)


class Sharpen:
    def process(self, img):
        return img.filter(ImageFilter.SHARPEN)


class Smooth:
    def process(self, img):
        return img.filter(ImageFilter.SMOOTH)


class EdgeEnhance:
    def process(self, img):
        return img.filter(ImageFilter.EDGE_ENHANCE)


class UnsharpMask:
    def __init__(self, radius=2, percent=150, threshold=3):
        self.radius = radius
        self.percent = percent
        self.threshold = threshold

    def process(self, img):
        radius = self.radius(*img.size) if callable(self.radius) else self.radius
        return img.filter(ImageFilter.UnsharpMask(radius, self.percent, self.threshold))


class BoxBlur:
    def __init__(self, radius=2):
        self.radius = radius

    def process(self, img):
        radius = self.radius(*img.size) if callable(self.radius) else self.radius
        return img.filter(ImageFilter.BoxBlur(radius))


class GaussianBlur:
    def __init__(self, radius=2):
        self.radius = radius

    def process(self, img):
        radius = self.radius(*img.size) if callable(self.radius) else self.radius
        return img.filter(ImageFilter.GaussianBlur(radius))
