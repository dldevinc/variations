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
