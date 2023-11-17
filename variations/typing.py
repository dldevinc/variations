import os
from abc import abstractmethod
from collections.abc import Sequence, Iterable
from numbers import Integral, Real
from typing import IO, Protocol, Union, runtime_checkable

from PIL import Image


@runtime_checkable
class ProcessorProtocol(Protocol):
    @abstractmethod
    def process(self, img: Image) -> Image:
        pass


FilePath = Union[str, os.PathLike[str]]
FilePointer = Union[FilePath, IO]
Dimension = Integral
Size = Sequence[Dimension]
Color = Union[str, Iterable[int]]
Rectangle = tuple[int, int, int, int]
GravityTuple = Sequence[Real]
