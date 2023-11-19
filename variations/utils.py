import os
import warnings
from pathlib import Path
from typing import Optional

from pilkit.exceptions import UnknownExtension
from pilkit.lib import Image
from pilkit.utils import extension_to_format, format_to_extension

from . import conf
from .processors import MakeOpaque, Transpose
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
        pass


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
    suggested_extension = format_to_extension(
        format
        or guess_format(path)
    )

    if suggested_extension:
        if isinstance(path, Path):
            return path.with_suffix(suggested_extension)
        else:
            root, ext = os.path.splitext(path)
            return root + suggested_extension
    else:
        return path


def apply_exif_orientation(img: Image) -> Image:
    """
    Applies the Exif orientation to the given image.
    """
    exif = img.getexif()
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
    warnings.warn(
        "The 'make_opaque' function is deprecated.",
        DeprecationWarning
    )

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
    warnings.warn(
        "The 'prepare_image' function is deprecated.",
        DeprecationWarning
    )

    format = img.format
    if draft_size is not None and format == "JPEG":
        img.draft(img.mode, draft_size)
    if format in {"JPEG", "TIFF"}:
        img = apply_exif_orientation(img)
    if background_color is not None:
        img = make_opaque(img, background_color)
    return img


def save_image(img: Image, fp: FilePointer, format: str, **options):
    """
    Wraps PIL's ``Image.save()`` method.
    """
    format = format.upper()

    if img.mode == "LA":
        if format in conf.RGBA_TRANSPARENCY_FORMATS:
            pass
        elif format in conf.PALETTE_TRANSPARENCY_FORMATS:
            # При сохранении LA в GIF теряются все цвета.
            # При конвертации в PA - тоже.
            img = img.convert("RGBA")
        else:
            # LA нельзя сохранить в формат, не поддерживающий прозрачность.
            img = MakeOpaque().process(img)
    elif img.mode in {"P", "PA"}:
        transparency = img.info.get("transparency")
        if format == "GIF" and isinstance(transparency, bytes):
            img = img.convert("RGBA")
        elif format not in conf.TRANSPARENCY_FORMATS:
            if transparency is None:
                img = img.convert("RGB")
            else:
                img = MakeOpaque().process(img)
    elif img.mode == "RGBA":
        if format not in conf.TRANSPARENCY_FORMATS:
            img = MakeOpaque().process(img)

    # Enable optimization by default
    if format in {"JPEG", "PNG"}:
        options.setdefault("optimize", True)

    img.save(fp, format=format, **options)
