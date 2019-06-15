import posixpath
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


def guess_format(fp):
    """
    Определение формата, в котором будет сохранено изображение.

    :type fp: str|typing.IO
    :rtype: str
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


def replace_extension(path, format):
    """
    Замена расширения файла в пути path на наиболее подходящее для формата format.

    :type path: str
    :type format: str
    :rtype: str
    """
    try:
        best_ext = EXTENSION_MAP[format.upper()]
    except KeyError:
        return path

    root, old_ext = posixpath.splitext(path)
    return ''.join((root, best_ext))


def apply_exif(img, info=None):
    """
    Применение ориентации, указанной в EXIF-данных.

    :type img: PIL.Image.Image
    :type info: dict
    :rtype: PIL.Image.Image
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


def reset_transparency(img, color='#FFFFFF', format=None):
    """
    Замена RGB-составляющей полностью прозрачных пикселей на указанный цвет.

    :type img: PIL.Image.Image
    :type format: str
    :type color: tuple | list | str
    :rtype: PIL.Image.Image
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


def prepare_image(img, draft_size=None, background_color=None):
    """
    1) Эффекивно уменьшает изображение методом Image.draft() для экономии памяти
       при обработке больших картинок.
    2) Примененяет ориентацию картинки, указанную в EXIF-данных
    3) Заливка RGB-данных в прозрачных пикселях указанным цветом во избежание
       артефактов при ресайзе

    :type img: PIL.Image.Image
    :type draft_size: list | tuple
    :type background_color: list | tuple | str
    :rtype: PIL.Image.Image
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
