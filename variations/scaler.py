from fractions import Fraction
from numbers import Real


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

    def __init__(
        self,
        width: Real,
        height: Real,
        upscale: bool = False
    ):
        self._width = self._original_width = width
        self._height = self._original_height = height
        self._upscale = bool(upscale)
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

    def set_width(self, value: Real):
        """
        Пропорциональное изменение ширины.
        """
        new_width = value
        if new_width <= self._original_width or not self._upscale:
            new_width = min(new_width, self._original_width)

        self._width = new_width
        self._height = self._width / self._ratio

    def set_height(self, value: Real):
        """
        Пропорциональное изменение высоты.
        """
        new_height = value
        if new_height <= self._original_height or not self._upscale:
            new_height = min(new_height, self._original_height)

        self._height = new_height
        self._width = self._height * self._ratio
