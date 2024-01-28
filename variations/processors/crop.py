from pilkit.processors.crop import SmartCrop, TrimBorderColor

__all__ = ["Crop", "TrimBorderColor", "SmartCrop"]


class Crop:
    """
    Crops an image, cropping it to the specified width and height. You may
    optionally provide either an anchor or x and y coordinates. This processor
    functions exactly the same as ``ResizeCanvas`` except that it will never
    enlarge the image.

    """

    def __init__(self, width=None, height=None, anchor=None, x=None, y=None):
        self.width = width
        self.height = height
        self.anchor = anchor
        self.x = x
        self.y = y

    def process(self, img):
        original_width, original_height = img.size
        new_width = int(
            min(original_width, self.width)
            if self.width
            else original_width
        )
        new_height = int(
            min(original_height, self.height)
            if self.height
            else original_height
        )

        if (
            self.x is None
            and self.y is None
            and new_width == original_width
            and new_height == original_height
        ):
            return img

        from .resize import ResizeCanvas
        return ResizeCanvas(
            new_width,
            new_height,
            anchor=self.anchor,
            x=self.x,
            y=self.y
        ).process(img)
