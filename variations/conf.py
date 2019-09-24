from pilkit.lib import Image

# Значение параметра format для автоматического определения итогового формата
AUTO_FORMAT = 'AUTO'

# Выходной формат изображения, если удалось установить автоматически
DEFAULT_FORMAT = 'JPEG'

DEFAULT_EXTRA = dict(
    jpeg=dict(
        quality=85,
        progressive=True,
    ),
    png=dict(

    ),
    webp=dict(
        autoconvert=False,
        quality=85,
    ),
    tiff=dict(
        compression='jpeg',
    )
)

# Предпочитаемые расширения
PREFERRED_EXTENSIONS = {
    value: key
    for key, value in Image.EXTENSION.items()
}
PREFERRED_EXTENSIONS['PNG'] = '.png'
PREFERRED_EXTENSIONS['JPEG'] = '.jpg'
PREFERRED_EXTENSIONS['JPEG2000'] = '.j2k'
PREFERRED_EXTENSIONS['TIFF'] = '.tiff'
