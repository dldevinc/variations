import copy
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, cast

from pilkit.lib import Image
from pilkit.utils import save_image

from . import conf, processors, utils
from .scaler import Scaler
from .typing import FilePtr, PathLike, Size


class Variation:
    logger = logging.getLogger('variations')

    def __init__(
        self,
        size: Size = (0, 0),
        max_width: int = 0,
        max_height: int = 0,
        clip: bool = True,
        upscale: bool = False,
        anchor: str = processors.Anchor.CENTER,
        face_detection: bool = False,
        format: str = conf.AUTO_FORMAT,
        preprocessors: Iterable = None,
        postprocessors: Iterable = None,
        **kwargs
    ):
        self.size = size
        self.clip = clip
        self.upscale = upscale
        self.max_width = max_width
        self.max_height = max_height
        self.face_detection = face_detection
        self.anchor = anchor
        self.format = format
        self.preprocessors = preprocessors
        self.postprocessors = postprocessors
        self.extra_context = kwargs

        # check face_recognition installed
        if self.face_detection:
            try:
                import face_recognition  # noqa
            except ImportError:
                self.logger.warning(
                    "Cannot use face detection because 'face_recognition' is not installed."
                )

    @property
    def clip(self):
        return self._clip

    @clip.setter
    def clip(self, value):
        if not isinstance(value, bool):
            raise TypeError(value)
        self._clip = value

    @property
    def upscale(self):
        return self._upscale

    @upscale.setter
    def upscale(self, value):
        if not isinstance(value, bool):
            raise TypeError(value)
        self._upscale = value

    @property
    def size(self) -> Size:
        return cast(Size, self._size)

    @size.setter
    def size(self, value: Size):
        error_msg = '"size" argument must be a sequence of two non-negative integers'

        # filter out some wrong types
        if isinstance(value, (dict, set, str)):
            raise TypeError(error_msg)

        try:
            formatted_value = tuple(int(item) for item in value)
        except (TypeError, ValueError):
            raise TypeError(error_msg)

        if len(formatted_value) != 2:
            raise ValueError(error_msg)

        if not all(i >= 0 for i in formatted_value):
            raise ValueError(error_msg)

        self._size = formatted_value

    @property
    def width(self):
        return self._size[0]

    @property
    def height(self):
        return self._size[1]

    @property
    def max_width(self):
        return self._max_width

    @max_width.setter
    def max_width(self, value):
        error_msg = '"max_width" argument must be a non-negative integer'
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise TypeError(error_msg)

        if value < 0:
            raise ValueError(error_msg)

        if value and self.clip:
            self.logger.warning('"max_width" makes sense only when "clip" is False')

        if value and self.width:
            self.logger.warning('"max_width" makes sense only when "width" is 0')

        self._max_width = value

    @property
    def max_height(self):
        return self._max_height

    @max_height.setter
    def max_height(self, value):
        error_msg = '"max_height" argument must be a non-negative integer'
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise TypeError(error_msg)

        if value < 0:
            raise ValueError(error_msg)

        if value and self.clip:
            self.logger.warning('"max_height" makes sense only when "clip" is False')

        if value and self.height:
            self.logger.warning('`max_height` makes sense only when "height" is 0')

        self._max_height = value

    @property
    def face_detection(self):
        return self._face_detection

    @face_detection.setter
    def face_detection(self, value):
        if not isinstance(value, bool):
            raise TypeError(value)
        self._face_detection = value

    @property
    def anchor(self):
        return self._anchor

    @anchor.setter
    def anchor(self, value):
        if isinstance(value, str):
            value = processors.Anchor.get_tuple(value.lower())

        error_msg = (
            '"anchor" argument must be a sequence of two float numbers between 0 and 1'
        )
        if not isinstance(value, (tuple, list)):
            raise TypeError(error_msg)

        try:
            value = tuple(float(item) for item in value)
        except (TypeError, ValueError):
            raise TypeError(error_msg)

        if len(value) != 2:
            raise ValueError(error_msg)
        if not all(0 <= i <= 1 for i in value):
            raise ValueError(error_msg)
        self._anchor = value

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, value):
        if not isinstance(value, str):
            raise TypeError('"format" must be a string')

        value = value.upper()
        if value != conf.AUTO_FORMAT and value not in Image.EXTENSION.values():
            raise ValueError('unsupported format: %s' % value)
        self._format = value

    @property
    def preprocessors(self):
        return self._preprocessors

    @preprocessors.setter
    def preprocessors(self, value):
        if value is None:
            value = []
        for proc in value:
            if not hasattr(proc, 'process'):
                raise TypeError('one of preprocessors has no method "process"')
        self._preprocessors = list(value)

    @property
    def postprocessors(self):
        return self._postprocessors

    @postprocessors.setter
    def postprocessors(self, value):
        if value is None:
            value = []
        for proc in value:
            if not hasattr(proc, 'process'):
                raise TypeError('one of postprocessors has no method "process"')
        self._postprocessors = list(value)

    @property
    def extra_context(self):
        return self._extra_context

    @extra_context.setter
    def extra_context(self, value: Dict[str, Any]):
        if not isinstance(value, dict):
            raise TypeError(value)
        self._extra_context = {k.lower(): v for k, v in value.items()}

    def copy(self):
        return copy.deepcopy(self)

    def get_output_size(self, source_size: Size) -> Size:  # noqa
        """
        Вычисление финальных размеров холста по размерам исходного изображения.
        """
        size = Scaler(*source_size, upscale=self.upscale)  # type: ignore
        if self.clip:
            if self.upscale:
                if self.width and self.width > size.width:
                    size.set_width(self.width)
                if self.height and self.height > size.height:
                    size.set_height(self.height)
            width = min(self.width, size.width) if self.width else size.width
            height = min(self.height, size.height) if self.height else size.height
            return width, height
        else:
            max_width = min(self.max_width or self.width, self.width or self.max_width)
            max_height = min(
                self.max_height or self.height, self.height or self.max_height
            )
            if self.upscale:
                if max_width:
                    if max_height:
                        max_aspect_ratio = max_width / max_height
                        if size.ratio > max_aspect_ratio:
                            size.set_width(max_width)
                        else:
                            size.set_height(max_height)
                    else:
                        size.set_width(max_width)
                elif max_height:
                    size.set_height(max_height)
            else:
                if max_width and max_width < size.width:
                    size.set_width(max_width)
                if max_height and max_height < size.height:
                    size.set_height(max_height)
            return self.width or size.width, self.height or size.height

    def get_processor(self, size: Size) -> processors.ProcessorPipeline:
        """
        Получение основного процессора вариации для указанного размера.
        """
        canvas_size = self.get_output_size(size)
        if self.clip:
            proc = processors.FaceDetectionResizeToFill(
                width=canvas_size[0],
                height=canvas_size[1],
                anchor=self.anchor,
                upscale=self._upscale,
                face_detection=self.face_detection,
            )
        else:
            proc = processors.ResizeToFit(
                width=canvas_size[0],
                height=canvas_size[1],
                anchor=self.anchor,
                mat_color=(255, 255, 255, 0),  # not background
                upscale=self._upscale,
            )

        procs = self.preprocessors + [proc] + self.postprocessors
        return processors.ProcessorPipeline(procs)

    def process(self, img: Image) -> Image:
        """
        Обработка изображения.
        """
        return self.get_processor(img.size).process(img)

    def output_format(self, path: PathLike) -> str:
        """
        Определение итогового формата изображения.
        """
        format = self.format or conf.AUTO_FORMAT
        if format == conf.AUTO_FORMAT:
            format = utils.guess_format(path) or conf.FALLBACK_FORMAT
        return format

    def replace_extension(self, path: PathLike) -> str:
        """
        Замена расширения файла в пути path в соответствии с вариацией.
        """
        format = self.output_format(path)
        return utils.replace_extension(path, format)

    def _detect_format(self, outfile: FilePtr) -> str:
        if isinstance(outfile, (str, Path)):
            return self.output_format(outfile)
        elif hasattr(outfile, 'name'):
            return self.output_format(outfile.name)
        elif self.format and self.format != conf.AUTO_FORMAT:
            return self.format
        else:
            return conf.FALLBACK_FORMAT

    def save(self, img: Image, outfile: FilePtr, **options):
        """
        Сохранение картинки в файл.
        """
        opts = options.copy()
        format = opts.pop('format', None)
        if not format:
            format = self._detect_format(outfile)
        format = format.lower()

        # настройки для конкретного формата
        format_options = {}  # type: Dict[str, Any]
        format_options.update(self.extra_context.get(format, {}))
        for k, v in format_options.items():
            opts.setdefault(k, v)

        # включаем autoconvert по умолчанию для всех форматов, кроме WebP
        if format == 'webp':
            autoconvert = opts.pop('autoconvert', False)
        else:
            autoconvert = opts.pop('autoconvert', True)

        if isinstance(outfile, Path):
            outfile = str(outfile)

        save_image(
            img, outfile, format=format, options=opts, autoconvert=autoconvert
        )
