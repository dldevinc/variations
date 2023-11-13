import logging
from fractions import Fraction
from typing import Optional

from pilkit.processors.resize import (
    AddBorder,
    Resize,
    ResizeCanvas,
    ResizeToCover,
    ResizeToFill,
    ResizeToFit,
    SmartResize,
    Thumbnail,
)

from ..typing import Rectangle

try:
    import face_recognition
    import numpy
    FACE_DETECTION_SUPPORT = True
except ImportError:
    FACE_DETECTION_SUPPORT = False

__all__ = [
    "Resize",
    "ResizeToCover",
    "ResizeToFill",
    "SmartResize",
    "ResizeCanvas",
    "AddBorder",
    "ResizeToFit",
    "Thumbnail",
    "ResizeToFillFace",
]


class ResizeToFillFace:
    expand_face_top_factor = 0.7
    expand_face_x_factor = 0.5
    expand_face_bottom_factor = 0.5

    def __init__(self, width=None, height=None, upscale=True):
        """
        :param width: The target width, in pixels.
        :param height: The target height, in pixels.
        :param upscale: Should the image be enlarged if smaller than the dimensions?

        """
        self.width = width
        self.height = height
        self.upscale = upscale

    def _expand_face_rect(self, rect: Rectangle) -> Rectangle:
        """
        FaceDetection находит прямоугольник именно лица (глаза, нос, рот).
        Но, в большинстве случаев, пользователя интересует голова целиком.
        Этот метод раширяет прямоугольник лица на заданный процент по всем
        направлениям.
        """
        rect = list(rect)
        widht, height = (rect[1] - rect[3]), (rect[2] - rect[0])
        rect[0] -= round(self.expand_face_top_factor * height)
        rect[1] += round(self.expand_face_x_factor * widht)
        rect[2] += round(self.expand_face_bottom_factor * height)
        rect[3] -= round(self.expand_face_x_factor * widht)
        return rect[0], rect[1], rect[2], rect[3]

    def _detect_faces(self, img) -> Optional[Rectangle]:
        # Image must be 8bit gray or RGB image.
        if img.mode in ("CMYK", "LA"):
            image_data = numpy.array(img.convert("RGB"))
        else:
            image_data = numpy.array(img)

        faces = face_recognition.face_locations(
            image_data,
            number_of_times_to_upsample=0,
        )
        if not faces:
            return

        rect = list(self._expand_face_rect(faces[0]))
        for face in faces[1:]:
            top, right, bottom, left = self._expand_face_rect(face)
            rect[0] = min(rect[0], top)
            rect[1] = max(rect[1], right)
            rect[2] = max(rect[2], bottom)
            rect[3] = min(rect[3], left)

        # left, top, width, height
        return rect[3], rect[0], (rect[1] - rect[3]), (rect[2] - rect[0])

    def process(self, img):
        if not FACE_DETECTION_SUPPORT:
            logging.warning(
                "Cannot use face detection because 'face_recognition' is not installed."
            )
            return

        rect = self._detect_faces(img)
        if not rect:
            return SmartResize(self.width, self.height, upscale=self.upscale).process(img)

        # Рассчет размеров изображения для покрытия (из класса ResizeToCover)
        original_width, original_height = img.size
        ratio = max(
            Fraction(self.width, original_width),
            Fraction(self.height, original_height)
        )
        new_width, new_height = (
            round(original_width * ratio),
            round(original_height * ratio)
        )

        #                 X           Y
        #   |-------------┴-----○-----┴---|
        #   A                   C         B
        #
        #   Anchor = AX / (AX + YB) = ?
        #   AX + YB = AB - XY
        #   Ratio = AC / AB
        #   AX = AC - XC = (AB * Ratio) - XY / 2
        #   Anchor = ( (AB * Ratio) - XY / 2 ) / (AB - XY)
        #
        rect_center_coords = (
            rect[0] + Fraction(rect[2], 2),
            rect[1] + Fraction(rect[3], 2),
        )
        rect_center_ratio = (
            Fraction(rect_center_coords[0], original_width),
            Fraction(rect_center_coords[1], original_height),
        )

        anchor_left_numerator = rect_center_ratio[0] * new_width - self.width / 2
        anchor_left_denominator = new_width - self.width
        anchor_top_numerator = rect_center_ratio[1] * new_height - self.height / 2
        anchor_top_denominator = new_height - self.height
        anchor = (
            min(max(0, anchor_left_numerator) / anchor_left_denominator, 1)
            if anchor_left_denominator else 0,
            min(max(0, anchor_top_numerator) / anchor_top_denominator, 1)
            if anchor_top_denominator else 0
        )

        return ResizeToFill(self.width, self.height, anchor=anchor, upscale=self.upscale).process(img)
