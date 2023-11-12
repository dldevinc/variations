from fractions import Fraction
from typing import Union


class Scaler:
    """
    Вычисление новых размеров прямоугольника с сохранением пропорций.
    """

    __slots__ = (
        "_width",
        "_height",
        "_original_width",
        "_original_height",
        "_upscale",
        "_ratio",
    )

    def __init__(self, width: Union[int, float], height: Union[int, float], upscale: bool = False):
        self._width = self._original_width = width
        self._height = self._original_height = height
        self._upscale = bool(upscale)

        if isinstance(width, int) and isinstance(height, int):
            self._ratio = Fraction(width, height)
        else:
            self._ratio = Fraction(Fraction.from_float(width), Fraction.from_float(height))

    def __str__(self):
        return "{}x{}".format(self.width, self.height)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.width, self.height)

    @property
    def width(self) -> int:
        return round(self._width)

    @property
    def height(self) -> int:
        return round(self._height)

    @property
    def ratio(self) -> Fraction:
        return self._ratio

    def set_width(self, value):
        """
        Пропорциональное изменение ширины.
        """
        new_width = value
        if new_width <= self._original_width or not self._upscale:
            new_width = min(new_width, self._original_width)

        self._width = new_width
        self._height = self._width / self._ratio

    def set_height(self, value):
        """
        Пропорциональное изменение высоты.
        """
        new_height = value
        if new_height <= self._original_height or not self._upscale:
            new_height = min(new_height, self._original_height)

        self._height = new_height
        self._width = self._height * self._ratio
