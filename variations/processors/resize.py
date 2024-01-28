from fractions import Fraction

from pilkit.processors.resize import (
    AddBorder,
    Resize,
    ResizeCanvas,
    ResizeToCover,
    ResizeToFill,
    SmartResize,
    Thumbnail,
)

from .base import Anchor

__all__ = [
    "Resize",
    "ResizeToCover",
    "ResizeToFill",
    "SmartResize",
    "ResizeCanvas",
    "AddBorder",
    "ResizeToFit",
    "Thumbnail",
]


class ResizeToFit:
    """
    Resizes an image to fit within the specified dimensions.

    Исправлен баг в библиотеке pilkit, когда указано лишь одно значение
    width или height, совсемтно с указание фонового цвета.
    """

    def __init__(
        self,
        width=None,
        height=None,
        upscale=True,
        mat_color=None,
        anchor=Anchor.CENTER
    ):
        """
        :param width: The maximum width of the desired image.
        :param height: The maximum height of the desired image.
        :param upscale: A boolean value specifying whether the image should
            be enlarged if its dimensions are smaller than the target
            dimensions.
        :param mat_color: If set, the target image size will be enforced and the
            specified color will be used as a background color to pad the image.

        """
        self.width = width
        self.height = height
        self.upscale = upscale
        self.mat_color = mat_color
        self.anchor = anchor

    def process(self, img):
        original_width, original_height = img.size
        if self.width is not None and self.height is not None:
            ratio = min(
                Fraction(self.width, original_width),
                Fraction(self.height, original_height)
            )
        else:
            if self.width is None and self.height is not None:
                ratio = Fraction(self.height, original_height)
            elif self.width is not None and self.height is None:
                ratio = Fraction(self.width, original_width)
            else:
                return img

        new_dimensions = (
            round(original_width * ratio),
            round(original_height * ratio)
        )

        img = Resize(*new_dimensions, upscale=self.upscale).process(img)
        if self.mat_color is not None:
            new_width = (
                self.width
                or (
                    new_dimensions[0]
                    if self.upscale
                    else min(original_width, new_dimensions[0])
                )
            )
            new_height = (
                self.height
                or (
                    new_dimensions[1]
                    if self.upscale
                    else min(original_height, new_dimensions[1])
                )
            )

            img = ResizeCanvas(
                new_width,
                new_height,
                self.mat_color,
                anchor=self.anchor
            ).process(img)

        return img
