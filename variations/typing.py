from typing import IO, Tuple, Union

FilePtr = Union[str, IO]
Size = Tuple[int, int]
Color = Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]
