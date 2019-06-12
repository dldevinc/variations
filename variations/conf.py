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
