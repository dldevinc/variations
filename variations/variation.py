import copy
import logging
import warnings
from collections.abc import Collection, Mapping, Set
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from itertools import chain
from numbers import Real
from typing import Any, Dict, Iterable, Union

from PIL import ImageColor
from pilkit.exceptions import UnknownFormat
from pilkit.lib import Image
from pilkit.utils import format_to_extension

from . import conf, processors, utils
from .scaler import Scaler
from .typing import (
    AspectRatio,
    Color,
    Dimension,
    FilePath,
    FilePointer,
    GravityTuple,
    ProcessorProtocol,
    Size,
)

NOT_SET = object()


class Variation:
    """
    Represents an image variation with configurable parameters.

    Parameters:
    - `size` (tuple): Tuple of width and height defining the size of the variation.
    - `aspect_ratio` (float or Fraction, optional): Specifies the aspect ratio of the processed image.
      If provided, it adjusts the size to maintain the specified aspect ratio.
    - `mode` (str, optional): Mode of the variation (fill, fit, crop, none). Defaults to 'fill'.
    - `upscale` (bool, optional): Boolean indicating whether upscaling is allowed. Defaults to False.
    - `gravity` (str or tuple, optional): Gravity of the variation, specifying the position or anchor point.
    - `background` (str or tuple, optional): Background color for the variation.
    - `format` (str, optional): The desired output image format.
    - `preprocessors` (iterable, optional): Iterable of processors to apply before the main processing.
    - `postprocessors` (iterable, optional): Iterable of processors to apply after the main processing.
    - `**kwargs`: Additional options.

    Methods:
    - `process(img: Image) -> Image`: Process an image according to the variation parameters.
    - `save(img: Image, fp: FilePointer, format=None, **options)`: Save the processed image to a file.

    Example:
    ```python
    from PIL import Image
    from variations import Variation, processors

    # Create a variation with specific parameters
    variation = Variation(
        size=(800, 600),
        mode=Variation.Mode.FIT,
        background="#FFFFFF",
        preprocessors=[
            processors.Grayscale()
        ],
    )

    img = Image.open("source.png")

    # Process an image using the variation
    processed_image = variation.process(img)

    # Save the processed image to a destination file
    variation.save(processed_image, "dest.jpg")
    ```

    """
    class Mode(Enum):
        FILL = "fill"
        FIT = "fit"
        CROP = "crop"
        NONE = "none"

    class Gravity(Enum):
        TOP_LEFT = "tl"
        TOP = "t"
        TOP_RIGHT = "tr"
        LEFT = "l"
        CENTER = "c"
        RIGHT = "r"
        BOTTOM_LEFT = "bl"
        BOTTOM = "b"
        BOTTOM_RIGHT = "br"
        AUTO = "auto"

    logger = logging.getLogger("variations")

    def __init__(
        self,
        size: Size = NOT_SET,
        *,
        mode: Mode = NOT_SET,
        upscale: bool = NOT_SET,
        gravity: Gravity = NOT_SET,
        aspect_ratio: AspectRatio = NOT_SET,
        background: Color = NOT_SET,
        max_width: int = NOT_SET,           # deprecated
        max_height: int = NOT_SET,          # deprecated
        clip: bool = NOT_SET,               # deprecated
        anchor: str = NOT_SET,              # deprecated
        face_detection: bool = NOT_SET,     # deprecated
        format: str = None,
        preprocessors: Iterable[ProcessorProtocol] = None,
        postprocessors: Iterable[ProcessorProtocol] = None,
        **kwargs
    ):
        self.legacy_mode = NOT_SET

        if size is NOT_SET:
            if aspect_ratio is NOT_SET:
                raise TypeError(
                    "Either the 'size' parameter or the 'aspect_ratio' parameter must be specified."
                )
            else:
                self.size = (0, 0)
                self.aspect_ratio = aspect_ratio
                self.legacy_mode = False
        else:
            self.size = size

            if aspect_ratio is NOT_SET:
                self.aspect_ratio = None
            elif all(x > 0 for x in self.size):
                raise ValueError(
                    "If 'aspect_ratio' is specified, at least one element in 'size' "
                    "must be equal to 0."
                )

        if mode is NOT_SET:
            self.mode = self.Mode.FILL
        else:
            self.legacy_mode = False
            self.mode = mode

        if gravity is NOT_SET:
            self.gravity = self.Gravity.CENTER
        else:
            if (
                self.legacy_mode is False
                and self.mode is self.Mode.FIT
                and gravity is self.Gravity.AUTO
            ):
                raise ValueError("Cannot use 'AUTO' gravity when 'mode' is set to 'FIT'.")

            self.legacy_mode = False
            self.gravity = gravity

        if background is NOT_SET:
            self.background = None
        else:
            if (
                self.legacy_mode is False
                and self.mode is not self.Mode.FIT
            ):
                self.logger.warning("'background' makes sense only when 'mode' is set to 'FIT'")

            self.legacy_mode = False
            self.background = background

        if clip is NOT_SET:
            self._clip = True
        else:
            if self.legacy_mode is False:
                raise ValueError("Cannot use 'clip' when 'mode' is set.")
            self.legacy_mode = True
            self.clip = clip

        if max_width is NOT_SET:
            self._max_width = 0
        else:
            if self.legacy_mode is False:
                raise ValueError("Cannot use 'max_width' when 'mode' is set.")
            self.legacy_mode = True
            self.max_width = max_width

        if max_height is NOT_SET:
            self._max_height = 0
        else:
            if self.legacy_mode is False:
                raise ValueError("Cannot use 'max_height' when 'mode' is set.")
            self.legacy_mode = True
            self.max_height = max_height

        if anchor is NOT_SET:
            self._anchor = (0.5, 0.5)
        else:
            if self.legacy_mode is False:
                raise ValueError("Cannot use 'anchor' when 'mode' is set.")
            self.legacy_mode = True
            self.anchor = anchor

        if face_detection is NOT_SET:
            self._face_detection = False
        else:
            if self.legacy_mode is False:
                raise ValueError("Cannot use 'face_detection' when 'mode' is set.")
            self.legacy_mode = True 
            self.face_detection = face_detection

        if upscale is NOT_SET:
            self.upscale = False
        else:
            if (
                self.legacy_mode is False
                and self.mode is self.Mode.CROP
                and upscale
            ):
                raise ValueError("Upscaling cannot be enabled when 'mode' is set to 'CROP'.")
            self.upscale = upscale

        if self.legacy_mode is NOT_SET:
            self.legacy_mode = False

        self.format = format
        self.preprocessors = preprocessors
        self.postprocessors = postprocessors
        self.options = kwargs

        # check face_recognition installed
        if self._face_detection:
            try:
                import face_recognition  # noqa
            except ImportError:
                self.logger.warning(
                    "Cannot use face detection because 'face_recognition' is not installed."
                )

    def __getattr__(self, item):
        if item in self._options:
            return self._options[item]

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{item}'"
        )

    @property
    def size(self) -> Size:
        return self._size

    @size.setter
    def size(self, value: Size):
        error_msg = "'size' argument must be a sequence of two non-negative integers"

        if (
            isinstance(value, (Mapping, Set, str, bytes))
            or not isinstance(value, Collection)
            or not all(isinstance(x, int) for x in value)
        ):
            raise TypeError(error_msg)

        formatted_value = tuple(int(x) for x in value)
        if len(formatted_value) != 2:
            raise ValueError(error_msg)

        if not all(x >= 0 for x in formatted_value):
            raise ValueError(error_msg)

        self._size = formatted_value

    @property
    def aspect_ratio(self) -> Union[AspectRatio, None]:
        return self._aspect_ratio

    @aspect_ratio.setter
    def aspect_ratio(self, value: AspectRatio):
        if value is None:
            self._aspect_ratio = value
            return

        if isinstance(value, (int, float)):
            aspect_ratio = Fraction.from_float(value)
        elif isinstance(value, Decimal):
            aspect_ratio = Fraction.from_decimal(value)
        elif isinstance(value, Fraction):
            aspect_ratio = value
        else:
            raise TypeError(
                "Unsupported type for 'aspect_ratio'. "
                "Please provide an int, float, Decimal, or Fraction."
            )

        if aspect_ratio <= 0:
            raise ValueError(
                "Aspect ratio must be greater than 0."
            )

        self._aspect_ratio = aspect_ratio

    @property
    def mode(self) -> Mode:
        return self._mode

    @mode.setter
    def mode(self, value: Union[Mode, str]):
        if isinstance(value, self.Mode):
            self._mode = value
            return

        if isinstance(value, str):
            lower_value = value.lower()
            try:
                self._mode = next(choice for choice in self.Mode if choice.value == lower_value)
                return
            except StopIteration:
                pass

        raise ValueError(
            f"Invalid mode: '{value}'. "
            f"Must be one of {', '.join(choice.value for choice in self.Mode)}."
        )

    @property
    def gravity(self) -> Union[Gravity, GravityTuple]:
        return self._gravity

    @gravity.setter
    def gravity(self, value: Union[str, Gravity, GravityTuple]):
        error_msg = (
            "Invalid value for 'gravity'. "
            "Accepted types: str, Variation.Gravity or tuple of two numbers."
        )

        if isinstance(value, str):
            lower_value = value.lower()
            try:
                value = next(choice for choice in self.Gravity if choice.value == lower_value)
            except StopIteration:
                raise ValueError(error_msg)
        elif (
            isinstance(value, (Mapping, Set, bytes))
            or not isinstance(value, (self.Gravity, Collection))
        ):
            raise TypeError(error_msg)

        if value is self.Gravity.AUTO:
            self._gravity = value
            return

        if isinstance(value, self.Gravity):
            value = processors.Anchor.get_tuple(value.value)

        if isinstance(value, str):
            raise ValueError(error_msg)

        if not all(isinstance(x, Real) for x in value):
            raise TypeError(error_msg)

        value = tuple(float(x) for x in value)
        if len(value) != 2:
            raise ValueError(error_msg)

        if not all(0 <= x <= 1 for x in value):
            raise ValueError(error_msg)

        self._gravity = value

    @property
    def background(self) -> Union[tuple[int, ...], None]:
        return self._background

    @background.setter
    def background(self, value: Union[Color, None]):
        error_msg = (
            "Invalid value for 'background'. It should be an iterable "
            "of integers representing RGB or RGBA values, or a string "
            "specifying a color name or RGB/RGBA values."
        )

        if value is None:
            self._background = value
            return

        if isinstance(value, str):
            try:
                value = ImageColor.getcolor(value, "RGBA")
            except ValueError:
                raise ValueError(error_msg)

        if (
            isinstance(value, (Mapping, Set, bytes))
            or not isinstance(value, Collection)
            or not all(isinstance(x, int) for x in value)
        ):
            raise TypeError(error_msg)

        if len(value) == 3:
            value += (255, )

        if len(value) != 4:
            raise ValueError(error_msg)

        if not all(0 <= x <= 255 for x in value):
            raise ValueError(error_msg)

        self._background = value

    @property
    def clip(self) -> bool:
        return self._clip

    @clip.setter
    def clip(self, value: bool):
        warnings.warn(
            "The 'clip' attribute is deprecated. Use 'mode' attribute instead.",
            DeprecationWarning
        )

        if not isinstance(value, bool):
            raise TypeError(
                "The 'clip' attribute must be a boolean value."
            )

        self._clip = value

    @property
    def upscale(self) -> bool:
        return self._upscale

    @upscale.setter
    def upscale(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(
                "The 'upscale' attribute must be a boolean value."
            )

        self._upscale = value

    @property
    def max_width(self) -> int:
        warnings.warn(
            "The 'max_width' attribute is deprecated. Use 'size' attribute instead.",
            DeprecationWarning
        )
        return self._max_width

    @max_width.setter
    def max_width(self, value: int):
        warnings.warn(
            "The 'max_width' attribute is deprecated. Use 'size' attribute instead.",
            DeprecationWarning
        )

        error_msg = "'max_width' argument must be a non-negative integer"
        if not isinstance(value, int):
            raise TypeError(error_msg)

        if value < 0:
            raise ValueError(error_msg)

        if value and self.clip:
            self.logger.warning("'max_width' makes sense only when 'clip' is False")

        if value and self.width:
            self.logger.warning("'max_width' makes sense only when 'width' is 0")

        self._max_width = value

    @property
    def max_height(self) -> int:
        warnings.warn(
            "The 'max_height' attribute is deprecated. Use 'size' attribute instead.",
            DeprecationWarning
        )
        return self._max_height

    @max_height.setter
    def max_height(self, value: int):
        warnings.warn(
            "The 'max_height' attribute is deprecated. Use 'size' attribute instead.",
            DeprecationWarning
        )

        error_msg = "'max_height' argument must be a non-negative integer"
        if not isinstance(value, int):
            raise TypeError(error_msg)

        if value < 0:
            raise ValueError(error_msg)

        if value and self.clip:
            self.logger.warning("'max_height' makes sense only when 'clip' is False")

        if value and self.height:
            self.logger.warning("`max_height` makes sense only when 'height' is 0")

        self._max_height = value

    @property
    def anchor(self) -> GravityTuple:
        warnings.warn(
            "The 'anchor' attribute is deprecated. Use 'gravity' attribute instead.",
            DeprecationWarning
        )
        return self._anchor

    @anchor.setter
    def anchor(self, value: Union[str, GravityTuple]):
        warnings.warn(
            "The 'anchor' attribute is deprecated. Use 'gravity' attribute instead.",
            DeprecationWarning
        )

        error_msg = (
            "'anchor' argument must be a sequence of two float numbers between 0 and 1"
        )

        if isinstance(value, str):
            value = processors.Anchor.get_tuple(value.lower())

        if isinstance(value, str):
            raise ValueError(error_msg)

        if (
            isinstance(value, (Mapping, Set, bytes))
            or not isinstance(value, Collection)
            or not all(isinstance(x, Real) for x in value)
        ):
            raise TypeError(error_msg)

        value = tuple(float(x) for x in value)
        if len(value) != 2:
            raise ValueError(error_msg)

        if not all(0 <= x <= 1 for x in value):
            raise ValueError(error_msg)

        self._anchor = value

    @property
    def face_detection(self) -> bool:
        warnings.warn(
            "The 'face_detection' attribute is deprecated. Use 'gravity' attribute instead.",
            DeprecationWarning
        )

        return self._face_detection

    @face_detection.setter
    def face_detection(self, value: bool):
        warnings.warn(
            "The 'face_detection' attribute is deprecated. Use 'gravity' attribute instead.",
            DeprecationWarning
        )

        if not isinstance(value, bool):
            raise TypeError(
                "The 'face_detection' attribute must be a boolean value."
            )

        self._face_detection = value

    @property
    def format(self) -> Union[str, None]:
        return self._format

    @format.setter
    def format(self, value: Union[str, None]):
        if value is None:
            self._format = value
        elif not isinstance(value, str):
            raise TypeError(
                "The 'format' attribute must be a string or NOT_SET."
            )
        else:
            value = value.upper()
            if value == "JPG":
                value = "JPEG"

            try:
                format_to_extension(value)
            except UnknownFormat:
                raise ValueError("Unsupported image format: %s" % value)

            self._format = value

    @property
    def preprocessors(self) -> tuple[ProcessorProtocol]:
        return self._preprocessors

    @preprocessors.setter
    def preprocessors(self, value: Iterable[ProcessorProtocol]):
        if value is None:
            value = ()

        if not all(
            isinstance(p, ProcessorProtocol) and type(p) is not type
            for p in value
        ):
            raise TypeError(
                "Each preprocessor must be an instance implementing "
                "the 'ProcessorProtocol' and provide a 'process' method."
            )

        self._preprocessors = tuple(value)

    @property
    def postprocessors(self) -> tuple[ProcessorProtocol]:
        return self._postprocessors

    @postprocessors.setter
    def postprocessors(self, value: Iterable[ProcessorProtocol]):
        if value is None:
            value = ()

        if not all(
            isinstance(p, ProcessorProtocol) and type(p) is not type
            for p in value
        ):
            raise TypeError(
                "Each postprocessors must be an instance implementing "
                "the 'ProcessorProtocol' and provide a 'process' method."
            )

        self._postprocessors = tuple(value)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value: Dict[str, Any]):
        if not isinstance(value, dict):
            raise TypeError(value)
        self._options = {k.lower(): v for k, v in value.items()}

    @property
    def width(self) -> Dimension:
        return self._size[0]

    @property
    def height(self) -> Dimension:
        return self._size[1]

    def copy(self):
        obj = type(self).__new__(type(self))
        obj.__dict__ = copy.deepcopy(self.__dict__)
        return obj

    def get_output_size(self, source_size: Size) -> Size:  # noqa
        """
        Вычисление финальных размеров холста по размерам исходного изображения.
        """
        warnings.warn(
            "The 'get_output_size' method is deprecated.",
            DeprecationWarning
        )

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
        warnings.warn(
            "The 'get_processor' method is deprecated. "
            "Use 'get_pipeline' instead.",
            DeprecationWarning
        )

        canvas_size = self.get_output_size(size)
        if self.clip:
            if self.face_detection:
                from processors.face_detection import ResizeToFillFace
                proc = ResizeToFillFace(
                    width=canvas_size[0],
                    height=canvas_size[1],
                    upscale=self._upscale,
                )
            else:
                proc = processors.ResizeToFill(
                    width=canvas_size[0],
                    height=canvas_size[1],
                    anchor=self.anchor,
                    upscale=self._upscale,
                )
        else:
            proc = processors.ResizeToFit(
                width=canvas_size[0],
                height=canvas_size[1],
                anchor=self.anchor,
                mat_color=(255, 255, 255, 0),  # not background
                upscale=self._upscale,
            )

        pipeline = list(chain(self.preprocessors, [proc], self.postprocessors))
        return processors.ProcessorPipeline(pipeline)

    def _get_fill_processors(self) -> Iterable[ProcessorProtocol]:
        if not self.width or not self.height:
            return [
                # Процессор ResizeToFit без указания mat_color
                # тождественен требуемому процессору Resize,
                # но включает в себя вычисление итоговых размеров.
                processors.ResizeToFit(
                    self.width or None,
                    self.height or None,
                    upscale=self.upscale
                )
            ]

        if self.gravity is self.Gravity.AUTO:
            from processors.face_detection import ResizeToFillFace
            return [
                ResizeToFillFace(
                    self.width or None,
                    self.height or None,
                    upscale=self.upscale
                )
            ]
        else:
            return [
                processors.ResizeToFill(
                    self.width or None,
                    self.height or None,
                    anchor=self.gravity,
                    upscale=self.upscale
                )
            ]

    def _get_fit_processors(self) -> Iterable[ProcessorProtocol]:
        return [
            processors.ResizeToFit(
                self.width or None,
                self.height or None,
                anchor=self.gravity,
                upscale=self.upscale,
                mat_color=self.background
            )
        ]

    def _get_crop_processors(self) -> Iterable[ProcessorProtocol]:
        if self.gravity is self.Gravity.AUTO:
            from processors.face_detection import CropFace
            return [
                CropFace(
                    self.width or None,
                    self.height or None,
                )
            ]
        else:
            return [
                processors.Crop(
                    self.width or None,
                    self.height or None,
                    anchor=self.gravity,
                )
            ]

    def get_pipeline(self) -> processors.ProcessorPipeline:
        pipeline = list(self.preprocessors)

        if self.mode is self.Mode.NONE:
            pass
        elif self.aspect_ratio is None and self.size == (0, 0):
            pass
        elif self.mode is self.Mode.FILL:
            pipeline.extend(self._get_fill_processors())
        elif self.mode is self.Mode.FIT:
            pipeline.extend(self._get_fit_processors())
        else:
            pipeline.extend(self._get_crop_processors())

        pipeline.extend(self.postprocessors)
        return processors.ProcessorPipeline(pipeline)

    def process(self, img: Image) -> Image:
        """
        Обработка изображения в соответствии с вариацией.
        """
        if self.legacy_mode:
            return self.get_processor(img.size).process(img)
        else:
            if self.width and self.height:
                img.draft(img.mode, self.size)
            img = utils.apply_exif_orientation(img)
            return self.get_pipeline().process(img)

    def output_format(self, path: FilePath) -> str:
        """
        Определение итогового формата изображения.
        """
        warnings.warn(
            "The 'output_format' method is deprecated.",
            DeprecationWarning
        )
        return (
            self.format
            or utils.guess_format(path)
        )

    def replace_extension(self, path: FilePath) -> str:
        warnings.warn(
            "The 'replace_extension' method is deprecated. "
            "Use 'utils.replace_extension' instead.",
            DeprecationWarning
        )
        return utils.replace_extension(path, self.format)

    def save(self, img: Image, fp: FilePointer, format=None, **options):
        """
        Saves this image under the given filename. If no format is
        specified, the format to use is determined from the filename
        extension, if possible.

        :param img: The image to save.
        :param fp: A filename (string), pathlib.Path object, or file object.
        :param format: The format to use for saving (optional).
        :param options: Additional options for saving the image.
        """
        opts = options.copy()

        final_format = (
            format
            or self.format
            or utils.guess_format(fp)
            or conf.MODE_TO_FORMAT[img.mode]
        ).upper()

        # Transfer additional parameters specific
        # to a particular image format from the variation.
        format_options = {}
        format_options.update(self.options.get(final_format.lower(), {}))
        for k, v in format_options.items():
            opts.setdefault(k, v)

        utils.save_image(img, fp, final_format, **opts)
