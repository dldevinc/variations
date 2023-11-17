import os
from collections import namedtuple
from pathlib import Path
from typing import Any, Dict, Optional

from pilkit.exceptions import UnknownExtension
from pilkit.lib import Image
from pilkit.utils import extension_to_format, format_to_extension

from . import conf
from .processors import Transpose
from .typing import Color, FilePath, FilePointer, Size


def guess_format(fp: FilePointer) -> Optional[str]:
    """
    Determine the image format based on the file extension.
    """
    if isinstance(fp, Path):
        extension = fp.suffix
    elif isinstance(fp, str):
        extension = os.path.splitext(fp)[1]
    elif hasattr(fp, "name"):
        extension = os.path.splitext(fp.name)[1]
    else:
        raise ValueError(
            "Invalid file pointer. It must be a string, Path, or have a 'name' attribute."
        )

    try:
        return extension_to_format(extension)
    except UnknownExtension:
        return conf.FALLBACK_FORMAT


def replace_extension(path: FilePath, format: str = None) -> FilePath:
    """
    Replace the file extension in the path with the most suitable one
    for the specified format. If no format is specified, the format
    to use is determined from the filename extension, if possible.

    Example:
        from variations.utils import replace_extension

        variation = Variation(...)
        destination_path = replace_extension("result.jpg", variation.format)
        variation.save(img, destination_path)
    """
    suggested_extension = format_to_extension(format or guess_format(path))

    if isinstance(path, Path):
        return path.with_suffix(suggested_extension)
    else:
        root, ext = os.path.splitext(path)
        return root + suggested_extension


def apply_exif_orientation(img: Image, info: Dict[str, Any] = None) -> Image:
    """
    Применение ориентации, указанной в EXIF-данных.
    """
    from PIL.JpegImagePlugin import _getexif

    if info:
        obj = namedtuple("FakeImage", ["info"])(info)
    else:
        obj = img

    exif = _getexif(obj)
    if not exif:
        return img

    orientation = exif.get(0x0112)
    if orientation is None:
        return img

    ops = Transpose._EXIF_ORIENTATION_STEPS[orientation]
    for method in ops:
        img = Transpose(method).process(img)
    return img


def make_opaque(img: Image, color: Color = "#FFFFFF") -> Image:
    """
    Замена RGB-составляющей полностью прозрачных пикселей на указанный цвет.
    """
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", img.size, color)
    return Image.alpha_composite(overlay, img)


def prepare_image(
    img: Image, draft_size: Size = None, background_color: Color = None,
) -> Image:
    """
    1) Эффективно уменьшает изображение методом Image.draft() для экономии памяти
       при обработке больших картинок.
    2) Примененяет ориентацию картинки, указанную в EXIF-данных
    3) Заливка RGB-данных в прозрачных пикселях указанным цветом во избежание
       артефактов при ресайзе

    Пример:
        from variations.utils import prepare_image

        variation = Variation(...)
        img = Image.open('source.jpg')
        img = prepare_image(img, draft_size=variation.get_output_size(img.size))
        new_img = variation.process(img)
    """
    format = img.format
    if draft_size is not None and format == "JPEG":
        img.draft(img.mode, draft_size)
    if format in {"JPEG", "TIFF"}:
        img = apply_exif_orientation(img)
    if background_color is not None:
        img = make_opaque(img, background_color)
    return img
