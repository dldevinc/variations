from pilkit.lib import Image

# Значение параметра format для автоматического определения итогового формата
AUTO_FORMAT = "AUTO"

# Выходной формат изображения, если не удалось установить автоматически
FALLBACK_FORMAT = "JPEG"

# Предпочитаемые расширения
PREFERRED_EXTENSIONS = {value: key for key, value in Image.EXTENSION.items()}
PREFERRED_EXTENSIONS["PNG"] = ".png"
PREFERRED_EXTENSIONS["JPEG"] = ".jpg"
PREFERRED_EXTENSIONS["JPEG2000"] = ".j2k"
PREFERRED_EXTENSIONS["TIFF"] = ".tiff"
