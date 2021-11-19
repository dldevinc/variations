from fractions import Fraction


class Scaler:
    """
    Вычисляет размеры прямоугольника, сохраняя пропорции
    """

    __slots__ = (
        "_width",
        "_height",
        "_width_orig",
        "_height_orig",
        "_upscale",
        "_ratio",
    )

    def __init__(self, width: int, height: int, upscale: bool = False):
        self._width = self._width_orig = int(width)
        self._height = self._height_orig = int(height)
        self._ratio = Fraction(width, height)
        self._upscale = bool(upscale)

    def __str__(self):
        return "{}x{}".format(self.width, self.height)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.width, self.height)

    @property
    def width(self):
        return round(self._width)

    @property
    def height(self):
        return round(self._height)

    @property
    def ratio(self):
        return self._ratio

    def set_width(self, value):
        new_width = value
        if new_width <= self._width_orig or not self._upscale:
            new_width = min(new_width, self._width_orig)

        self._width = new_width
        self._height = self._width / self._ratio
        return self

    def set_height(self, value):
        new_height = value
        if new_height <= self._height_orig or not self._upscale:
            new_height = min(new_height, self._height_orig)

        self._height = new_height
        self._width = self._height * self._ratio
        return self
