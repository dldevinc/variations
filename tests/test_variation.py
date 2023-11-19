import io
import pytest
from PIL import Image
from pilkit import processors

from variations import processors
from variations.variation import Variation

from . import helper


class TestSize:
    def test_empty_size(self):
        with pytest.raises(ValueError, match="'size' parameter is required"):
            Variation()

    @pytest.mark.parametrize("size", [
        None,
        "800,600",
        b"800,600",
        {100, 200},
        [10, -1.6],
        ("-100", "200"),
        {100: 10, 200: 20},
    ])
    def test_invalid_size_types(self, size):
        with pytest.raises(TypeError, match="argument must be a sequence"):
            Variation(size)

    @pytest.mark.parametrize("size", [
        (),
        [],
        (100,),
        (-100, -200),
        [100, 200, 300],
        (x for x in [100, 200]),
    ])
    def test_invalid_size_value(self, size):
        with pytest.raises(ValueError, match="argument must be a sequence"):
            Variation(size)

    @pytest.mark.parametrize("size", [
        (0, 0),
        (100, 200),
        [100, 200],
    ])
    def test_valid_size(self, size):
        Variation(size)


class TestMode:
    def test_default_value(self):
        v = Variation(size=(640, 480))
        assert v.mode is Variation.Mode.FILL

    def test_enum_value(self):
        v = Variation(size=(640, 480), mode=Variation.Mode.FIT)
        assert v.mode is Variation.Mode.FIT

    @pytest.mark.parametrize("mode_string,expected", [
        ("Fill", Variation.Mode.FILL),
        ("fit", Variation.Mode.FIT),
        ("crop", Variation.Mode.CROP),
        ("none", Variation.Mode.NONE),
    ])
    def test_valid_string(self, mode_string, expected):
        v = Variation(size=(640, 480), mode=mode_string)
        assert v.mode is expected

    def test_invalid_mode_value(self):
        with pytest.raises(ValueError, match="Invalid mode"):
            Variation(size=(640, 480), mode="unknown")


class TestGravity:
    def test_default_value(self):
        v = Variation(size=(640, 480))
        assert v.gravity == (0.5, 0.5)

    def test_enum_value(self):
        v = Variation(size=(640, 480), gravity=Variation.Gravity.BOTTOM_RIGHT)
        assert v.gravity == (1, 1)

    def test_valid_iterable(self):
        v = Variation(size=(640, 480), gravity=[0.1, 0.75])
        assert v.gravity == (0.1, 0.75)

    @pytest.mark.parametrize("gravity_string,expected", [
        ("TL", (0, 0)),
        ("t", (0.5, 0)),
        ("tr", (1, 0)),
        ("l", (0, 0.5)),
        ("c", (0.5, 0.5)),
        ("r", (1, 0.5)),
        ("bl", (0, 1)),
        ("b", (0.5, 1)),
        ("br", (1, 1)),
        ("auto", Variation.Gravity.AUTO),
    ])
    def test_valid_string(self, gravity_string, expected):
        v = Variation(size=(640, 480), gravity=gravity_string)
        assert v.gravity == expected

    @pytest.mark.parametrize("gravity", [
        1,
        [0.12, "0.8"],
        ("1", "0.75"),
        {0.10, 0.14},
        {"x": 0.5, "y": 0.5},
        ["one", 0.5]
    ])
    def test_invalid_type(self, gravity):
        with pytest.raises(TypeError, match="Invalid value for 'gravity'"):
            Variation(size=(640, 480), gravity=gravity)

    @pytest.mark.parametrize("gravity", [
        (),
        "",
        "brc",
        "0, 0",
        (0.3,),
        (1.5, 2),
        (-8, 2),
        (0, 0, 0),
    ])
    def test_invalid_value(self, gravity):
        with pytest.raises(ValueError, match="Invalid value for 'gravity'"):
            Variation(size=(640, 480), gravity=gravity)

    def test_fit_mode(self):
        with pytest.raises(ValueError, match="Cannot use 'AUTO' gravity"):
            Variation(size=(640, 480), mode=Variation.Mode.FIT, gravity=Variation.Gravity.AUTO)


class TestBackground:
    def test_default_value(self):
        v = Variation(size=(640, 480))
        assert v.background is None

    @pytest.mark.parametrize("background,expected", [
        ("aliceblue", (240, 248, 255, 255)),
        ("#FFFF00", (255, 255, 0, 255)),
        ("#FFFF0080", (255, 255, 0, 128)),
        ((255, 255, 0), (255, 255, 0, 255)),
        ((255, 255, 0, 0), (255, 255, 0, 0)),
    ])
    def test_valid_color(self, background, expected):
        v = Variation(size=(640, 480), background=background)
        assert v.background == expected

    @pytest.mark.parametrize("background", [
        1,
        [255, "0.8"],
        ("255", "255", "255"),
        {0.10, 0.14},
        {"x": 0.5, "y": 0.5},
    ])
    def test_invalid_type(self, background):
        with pytest.raises(TypeError, match="Invalid value for 'background'"):
            Variation(size=(640, 480), background=background)

    @pytest.mark.parametrize("background", [
        "unknown",
        "#FF",
        (255, 255),
        (255, 255, 255, 0, 0),
        (999, 999, 999),
        (-1, -1, -1, 0)
    ])
    def test_invalid_value(self, background):
        with pytest.raises(ValueError, match="Invalid value for 'background'"):
            Variation(size=(640, 480), background=background)


class TestClip:
    def test_default_value(self):
        v = Variation(size=(640, 480))
        assert v.clip is True

    def test_bool_value(self):
        v = Variation(size=(640, 480), clip=False)
        assert v.clip is False

    def test_invalid_value(self):
        with pytest.raises(TypeError, match="must be a boolean value"):
            Variation(size=(640, 480), clip="yes")

    def test_modern_mode(self):
        with pytest.raises(ValueError, match="when 'mode' is set"):
            Variation(size=(640, 480), mode=Variation.Mode.FILL, clip=True)


class TestUpscale:
    def test_default_value(self):
        v = Variation(size=(640, 480))
        assert v.upscale is False

    def test_bool_value(self):
        v = Variation(size=(640, 480), upscale=True)
        assert v.upscale is True

    def test_invalid_value(self):
        with pytest.raises(TypeError, match="must be a boolean value"):
            Variation(size=(640, 480), upscale="yes")

    def test_modern_mode(self):
        Variation(size=(640, 480), mode=Variation.Mode.FILL, upscale=True)

    def test_crop_mode(self):
        with pytest.raises(ValueError, match="Upscaling cannot be enabled"):
            Variation(size=(640, 480), mode=Variation.Mode.CROP, upscale=True)


class TestMaxWidth:
    def test_default_value(self):
        v = Variation(size=(640, 480))
        assert v.max_width == 0

    def test_int_value(self):
        v = Variation(size=(640, 480), max_width=400)
        assert v.max_width == 400

    def test_float_value(self):
        with pytest.raises(TypeError, match="must be a non-negative integer"):
            Variation(size=(640, 480), max_width=400.5)

    def test_string_value(self):
        with pytest.raises(TypeError, match="must be a non-negative integer"):
            Variation(size=(640, 480), max_width="400")

    def test_negative_value(self):
        with pytest.raises(ValueError, match="must be a non-negative integer"):
            Variation(size=(640, 480), max_width=-400)

    def test_modern_mode(self):
        with pytest.raises(ValueError, match="when 'mode' is set"):
            Variation(size=(640, 480), mode=Variation.Mode.FILL, max_width=400)


class TestMaxHeight:
    def test_default_value(self):
        v = Variation(size=(640, 480))
        assert v.max_height == 0

    def test_int_value(self):
        v = Variation(size=(640, 480), max_height=400)
        assert v.max_height == 400

    def test_float_value(self):
        with pytest.raises(TypeError, match="must be a non-negative integer"):
            Variation(size=(640, 480), max_height=400.5)

    def test_string_value(self):
        with pytest.raises(TypeError, match="must be a non-negative integer"):
            Variation(size=(640, 480), max_height="400")

    def test_negative_value(self):
        with pytest.raises(ValueError, match="must be a non-negative integer"):
            Variation(size=(640, 480), max_height=-400)

    def test_modern_mode(self):
        with pytest.raises(ValueError, match="when 'mode' is set"):
            Variation(size=(640, 480), mode=Variation.Mode.FILL, max_height=400)


class TestAnchor:
    def test_default_value(self):
        v = Variation(size=(640, 480))
        assert v.anchor == (0.5, 0.5)

    def test_valid_string(self):
        v = Variation(size=(640, 480), anchor="BR")
        assert v.anchor == (1, 1)

    def test_valid_iterable(self):
        v = Variation(size=(640, 480), anchor=[0.1, 0.75])
        assert v.anchor == (0.1, 0.75)

    @pytest.mark.parametrize("anchor", [
        1,
        [0.12, "0.8"],
        ("1", "0.75"),
        {0.10, 0.14},
        {"x": 0.5, "y": 0.5},
        ["one", 0.5]
    ])
    def test_invalid_type(self, anchor):
        with pytest.raises(TypeError, match="must be a sequence of two float"):
            Variation(size=(640, 480), anchor=anchor)

    @pytest.mark.parametrize("anchor", [
        (),
        "",
        "brc",
        "0, 0",
        (0.3,),
        (1.5, 2),
        (-8, 2),
        (0, 0, 0),
    ])
    def test_invalid_value(self, anchor):
        with pytest.raises(ValueError, match="must be a sequence of two float"):
            Variation(size=(640, 480), anchor=anchor)

    def test_modern_mode(self):
        with pytest.raises(ValueError, match="when 'mode' is set"):
            Variation(size=(640, 480), mode=Variation.Mode.FILL, anchor="br")


class TestFaceDetection:
    def test_default_value(self):
        v = Variation(size=(640, 480))
        assert v.face_detection is False

    def test_bool_value(self):
        v = Variation(size=(640, 480), face_detection=True)
        assert v.face_detection is True

    def test_invalid_value(self):
        with pytest.raises(TypeError, match="must be a boolean value"):
            Variation(size=(640, 480), face_detection="yes")

    def test_modern_mode(self):
        with pytest.raises(ValueError, match="when 'mode' is set"):
            Variation(size=(640, 480), mode=Variation.Mode.FILL, face_detection=True)


class TestFormat:
    def test_default_value(self):
        v = Variation(size=(640, 480))
        assert v.format is None

    @pytest.mark.parametrize("format_input,output", [
        ("jpg", "JPEG"),
        ("jpeg", "JPEG"),
        ("Png", "PNG"),
        ("WEBP", "WEBP"),
    ])
    def test_valid_string(self, format_input, output):
        v = Variation(size=(640, 480), format=format_input)
        assert v.format == output

    def test_invalid_value(self):
        with pytest.raises(ValueError, match="Unsupported image format"):
            Variation(size=(640, 480), format="mp3")


class TestPreprocessors:
    def test_default_value(self):
        v = Variation(size=(640, 480))
        assert v.preprocessors == ()

    def test_valid_iterable(self):
        v = Variation(
            size=(640, 480),
            preprocessors=[
                processors.MakeOpaque(),
                processors.Reflection()
            ]
        )
        assert type(v.preprocessors) is tuple

    def test_invalid_iterable(self):
        with pytest.raises(TypeError, match="Each preprocessor must be an instance"):
            Variation(
                size=(640, 480),
                preprocessors=[
                    processors.MakeOpaque,
                ]
            )


class TestPostprocessors:
    def test_default_value(self):
        v = Variation(size=(640, 480))
        assert v.postprocessors == ()

    def test_valid_iterable(self):
        v = Variation(
            size=(640, 480),
            postprocessors=[
                processors.MakeOpaque(),
                processors.Reflection()
            ]
        )
        assert type(v.postprocessors) is tuple

    def test_invalid_iterable(self):
        with pytest.raises(TypeError, match="Each postprocessors must be an instance"):
            Variation(
                size=(640, 480),
                postprocessors=[
                    processors.MakeOpaque,
                ]
            )


class TestOptions:
    def test_default_value(self):
        v = Variation(size=(640, 480))
        assert v.options == {}

    def test_options(self):
        v = Variation(
            size=(640, 480),
            webp=dict(
                lossless=True,
                quality=90,
            ),
        )

        with pytest.raises(AttributeError):
            v.jpeg

        assert v.webp == {
            "lossless": True,
            "quality": 90,
        }


class TestWidth:
    def test_value(self):
        v = Variation(size=(640, 480))
        assert v.width == 640


class TestHeight:
    def test_value(self):
        v = Variation(size=(640, 480))
        assert v.height == 480


class TestCopy:
    def test_copy(self):
        v1 = Variation(
            size=(640, 480),
            jpeg=[1, 2, 3]
        )
        v2 = v1.copy()
        v2.jpeg.append(4)
        assert len(v1.jpeg) == 3


class TestSave:
    def test_save_string(self):
        v = Variation(size=(100, 200))
        img = Image.new("RGB", (640, 480), color="red")

        output_path = helper.OUTPUT_PATH / "save/output/str.jpg"
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        v.save(img, output_path)

    def test_save_path(self):
        v = Variation(size=(100, 200))
        img = Image.new("RGB", (640, 480), color="red")

        output_path = helper.OUTPUT_PATH / "save/output/path.jpg"
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        v.save(img, output_path)

    def test_save_io(self):
        v = Variation(size=(100, 200))
        img = Image.new("RGB", (640, 480), color="red")

        output_path = helper.OUTPUT_PATH / "save/output/io.jpg"
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        with io.BytesIO() as buffer:
            buffer.name = str(output_path)
            v.save(img, buffer)

            buffer.seek(0)
            with output_path.open("wb+") as fp:
                for chunk in buffer:
                    fp.write(chunk)
