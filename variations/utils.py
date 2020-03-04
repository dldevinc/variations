import posixpath
from collections import namedtuple
from typing import IO, Any, Dict, Optional, Sequence, Union

from pilkit.lib import Image

from . import conf, processors


def guess_format(fp: Union[str, IO]) -> Optional[str]:
    """
    Определение формата изображение по расширению файла.
    """
    if isinstance(fp, (bytes, str)):
        filename = fp
    elif hasattr(fp, 'name'):
        filename = fp.name
    else:
        return

    ext = posixpath.splitext(filename)[1].lower()
    try:
        return Image.EXTENSION[ext]
    except KeyError:
        pass


def get_preferred_extension(format: str) -> str:
    """
    Возвращает наиболее подходящее расширение для формата format.
    """
    return conf.PREFERRED_EXTENSIONS[format.upper()]


def replace_extension(path: str, format: str) -> str:
    """
    Замена расширения файла в пути path на наиболее подходящее для формата format.
    """
    try:
        preferred_extension = get_preferred_extension(format)
    except KeyError:
        return path

    root, original_ext = posixpath.splitext(path)
    return ''.join((root, preferred_extension))


def apply_exif_orientation(img: Image, info: Dict[str, Any] = None) -> Image:
    """
    Применение ориентации, указанной в EXIF-данных.
    """
    from PIL.JpegImagePlugin import _getexif

    if info:
        obj = namedtuple('FakeImage', 'info')(info=info)
    else:
        obj = img

    exif = _getexif(obj)
    if not exif:
        return img

    orientation = exif.get(0x0112)
    if orientation is None:
        return img

    ops = processors.Transpose._EXIF_ORIENTATION_STEPS[orientation]
    for method in ops:
        img = processors.Transpose(method).process(img)
    return img


def make_opaque(img: Image, color: Union[str, Sequence] = '#FFFFFF') -> Image:
    """
    Замена RGB-составляющей полностью прозрачных пикселей на указанный цвет.
    """
    img = img.convert('RGBA')
    overlay = Image.new('RGBA', img.size, color)
    return Image.alpha_composite(overlay, img)


def prepare_image(
    img: Image,
    draft_size: Sequence[int] = None,
    background_color: Union[str, Sequence] = None,
) -> Image:
    """
    1) Эффективно уменьшает изображение методом Image.draft() для экономии памяти
       при обработке больших картинок.
    2) Примененяет ориентацию картинки, указанную в EXIF-данных
    3) Заливка RGB-данных в прозрачных пикселях указанным цветом во избежание
       артефактов при ресайзе
    """
    format = img.format
    if draft_size is not None and format == 'JPEG':
        img.draft(img.mode, draft_size)
    if format in {'JPEG', 'TIFF'}:
        img = apply_exif_orientation(img)

    if background_color is not None:
        img = make_opaque(img, background_color)
    return img
