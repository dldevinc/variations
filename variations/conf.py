RGBA_TRANSPARENCY_FORMATS = {"PNG", "WEBP"}
PALETTE_TRANSPARENCY_FORMATS = {"PNG", "GIF"}
TRANSPARENCY_FORMATS = RGBA_TRANSPARENCY_FORMATS | PALETTE_TRANSPARENCY_FORMATS

# Определение подходящего формата по режиму изображения
MODE_TO_FORMAT = {
    "1": "PNG",
    "L": "WEBP",
    "LA": "WEBP",
    "P": "PNG",
    "PA": "PNG",
    "RGB": "WEBP",
    "RGBA": "WEBP",
}
