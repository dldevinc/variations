import os
from collections.abc import Sequence
from typing import IO, Union

FilePath = Union[str, os.PathLike[str]]
FilePointer = Union[FilePath, IO]
Size = Sequence[Union[int, float]]
Color = Union[str, tuple[int, int, int], tuple[int, int, int, int]]
Rectangle = tuple[int, int, int, int]
