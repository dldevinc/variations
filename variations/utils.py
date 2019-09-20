import posixpath
from typing import IO, Union, Optional, Dict, Any, Sequence
from collections import namedtuple
from pilkit import utils
from pilkit.lib import Image
from . import processors

EXTENSION_MAP = {
    value: key
    for key, value in Image.EXTENSION.items()
}
EXTENSION_MAP['PNG'] = '.png'
EXTENSION_MAP['JPEG'] = '.jpg'
EXTENSION_MAP['JPEG2000'] = '.j2k'
EXTENSION_MAP['TIFF'] = '.tiff'


def guess_format(fp: Union[str, IO]) -> Optional[str]:
    """
    Определение формата, в котором будет сохранено изображение.
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


def replace_extension(path: str, format: str) -> str:
    """
    Замена расширения файла в пути path на наиболее подходящее для формата format.
    """
    try:
        best_ext = EXTENSION_MAP[format.upper()]
    except KeyError:
        return path

    root, old_ext = posixpath.splitext(path)
    return ''.join((root, best_ext))


def apply_exif(img: Image, info: Dict[str, Any] = None) -> Image:
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


def reset_transparency(img: Image, color: Union[str, Sequence] = '#FFFFFF', format: str = None) -> Image:
    """
    Замена RGB-составляющей полностью прозрачных пикселей на указанный цвет.
    """
    format = format or img.format
    if format is None:
        return img
    else:
        format = format.upper()

    if img.mode == 'RGBA':
        if format not in utils.RGBA_TRANSPARENCY_FORMATS:
            return img
    elif img.mode == 'P':
        if format not in utils.PALETTE_TRANSPARENCY_FORMATS:
            return img
    else:
        return img

    img = img.convert('RGBA')
    overlay = Image.new('RGB', img.size, color)
    mask = img.getchannel('A')
    return Image.composite(img, overlay, mask)


def prepare_image(img: Image, draft_size: Sequence = None, background_color: Union[str, Sequence] = None) -> Image:
    """
    1) Эффекивно уменьшает изображение методом Image.draft() для экономии памяти
       при обработке больших картинок.
    2) Примененяет ориентацию картинки, указанную в EXIF-данных
    3) Заливка RGB-данных в прозрачных пикселях указанным цветом во избежание
       артефактов при ресайзе
    """
    format = img.format
    if draft_size is not None and format == 'JPEG':
        img.draft(img.mode, draft_size)
    if format in {'JPEG', 'TIFF'}:
        img = apply_exif(img)

    # TODO: перепроверить необходимость
    if background_color is not None and img.mode in ('RGBA', 'P'):
        img = reset_transparency(img, background_color, format=format)
    return img
