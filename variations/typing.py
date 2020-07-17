from pathlib import Path
from typing import IO, List, Tuple, Union

PathLike = Union[str, Path]
FilePtr = Union[str, Path, IO]
Size = Union[Tuple[int, int], List[int]]
Color = Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]
