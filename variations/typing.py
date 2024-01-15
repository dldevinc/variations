import os
from abc import abstractmethod
from collections.abc import Collection, Sequence
from decimal import Decimal
from fractions import Fraction
from numbers import Real
from typing import IO, Protocol, Union, runtime_checkable

from PIL import Image


@runtime_checkable
class ProcessorProtocol(Protocol):
    @abstractmethod
    def process(self, img: Image) -> Image:
        pass


FilePath = Union[str, os.PathLike[str]]
FilePointer = Union[FilePath, IO]
Dimension = int
AspectRatio = Union[int, float, Fraction, Decimal]
Size = Sequence[Dimension]
Color = Union[str, Collection[int]]
Rectangle = tuple[int, int, int, int]
GravityTuple = Sequence[Real]
