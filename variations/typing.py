from typing import IO, Sequence, Tuple, Union

FilePtr = Union[str, IO]
Size = Tuple[int, int]
Color = Union[str, Sequence[Tuple[int, int, int]], Sequence[Tuple[int, int, int, int]]]
