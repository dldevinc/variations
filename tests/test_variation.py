import io
import pytest
from pathlib import Path
from PIL import Image
from pilkit import processors

from variations import processors
from variations.variation import Variation

from . import helper


class TestVariation:
    def test_default_size(self):
        v = Variation()
        assert v.size == (0, 0)

    def test_fail_setters(self):
        v = Variation()
        with pytest.raises(TypeError):
            v.clip = "yes"

        with pytest.raises(TypeError):
            v.upscale = "yes"

        with pytest.raises(TypeError):
            v.face_detection = "yes"

        with pytest.raises(TypeError):
            v.format = ["JPG"]

        with pytest.raises(ValueError):
            v.format = "MP4"

        with pytest.raises(TypeError):
            v.preprocessors = [{"process": None}]

        with pytest.raises(TypeError):
            v.postprocessors = [{"process": None}]

        with pytest.raises(TypeError):
            v.extra_context = ["data", "extras"]

    def test_output_format(self):
        variation = Variation()
        assert variation.output_format("image.Webp") == "WEBP"
        assert variation.output_format("image.mp3") == "JPEG"

        variation = Variation(format="PNG")
        assert variation.output_format("image.Webp") == "PNG"
        assert variation.output_format("image.mp3") == "PNG"

    def test_detect_format(self):
        variation = Variation()
        assert variation._detect_format("image.jpg") == "JPEG"
        assert variation._detect_format("image.jpeg") == "JPEG"
        assert variation._detect_format("image.mp3") == "JPEG"

        assert variation._detect_format(Path("image.jpg")) == "JPEG"
        assert variation._detect_format(Path("image.mp3")) == "JPEG"

        with io.BytesIO() as file:
            assert variation._detect_format(file) == "JPEG"  # FALLBACK_FORMAT

            file.name = "image.png"
            assert variation._detect_format(file) == "PNG"

        gif_variation = Variation(format="GIF")
        with io.BytesIO() as file:
            assert gif_variation._detect_format(file) == "GIF"

            file.name = "image.mp3"
            assert gif_variation._detect_format(file) == "GIF"

    @pytest.mark.parametrize("size", [
        None,
        "65",
        {100, 200},
        {100: 10, 200: 20},
    ])
    def test_size_invalid_type(self, size):
        with pytest.raises(TypeError):
            Variation(size)

    @pytest.mark.parametrize("size", [
        (),
        [],
        (100,),
        [10, -1.6],
        (-100, -200),
        ("-100", "200"),
        [100, 200, 300],
    ])
    def test_size_invalid_value(self, size):
        with pytest.raises(ValueError):
            Variation(size)

    @pytest.mark.parametrize("size", [
        (0, 0),
        (100, 200),
        ("100", "200"),
        [100, 200],
        ["100", "200"],
        (100.6, 200.7),
        (x for x in [100, 200]),
    ])
    def test_valid_sizes(self, size):
        Variation(size)

    def test_size_properties(self):
        v = Variation(["123", 456.6])
        assert v.width == 123
        assert v.height == 456

    @pytest.mark.parametrize("limits", [
        {"max_width": "a"},
        {"max_width": [0, 200]},
        {"max_height": "b"},
        {"max_height": [10, 50]},
    ])
    def test_limits_invalid_type(self, limits):
        with pytest.raises(TypeError):
            Variation([100, 100], **limits)

    @pytest.mark.parametrize("limits", [
        {"max_width": "-100"},
        {"max_height": "-100"},
    ])
    def test_limits_invalid_value(self, limits):
        with pytest.raises(ValueError):
            Variation([100, 100], **limits)

    @pytest.mark.parametrize("limits", [
        {"max_width": 100},
        {"max_height": 200},
        {"max_width": "0", "max_height": 0},
        {"max_width": "100", "max_height": 200},
    ])
    def test_valid_limits(self, limits):
        Variation([100, 100], **limits)

    def test_limits_properties(self):
        v = Variation([100, 100], max_width=350, max_height=450.75)
        assert v.max_width == 350
        assert v.max_height == 450

    def test_variation_copy(self):
        v = Variation(
            size=[0, 0],
            clip=False,
            max_width=350,
            max_height=450.75,
            preprocessors=[processors.Crop(width=200, height=120, x=50, y=50)],
            postprocessors=[processors.ColorOverlay("#0000FF", 0.10)],
            extra=dict(key="SomeWhat", inner_list=[1, 2, 3]),
        )

        clone = v.copy()
        assert clone is not v
        assert clone.preprocessors is not v.preprocessors
        assert clone.postprocessors is not v.postprocessors
        assert clone.extra_context is not v.extra_context
        assert (
            clone.extra_context["extra"]["inner_list"]
            is not v.extra_context["extra"]["inner_list"]
        )

    @pytest.mark.parametrize("anchor", [
        1,
        {0.10, 0.14},
        "xxx",
        "0, 0",
        ["one", 2]
    ])
    def test_anchor_invalid_type(self, anchor):
        with pytest.raises(TypeError):
            Variation([100, 100], anchor=anchor)

    @pytest.mark.parametrize("anchor", [
        (),
        (-8, 2),
        [0, 0, 0],
        (0, 0, 0),
    ])
    def test_anchor_invalid_value(self, anchor):
        with pytest.raises(ValueError):
            Variation([100, 100], anchor=anchor)

    @pytest.mark.parametrize("anchor", [
        "c",
        "tl",
        [0.12, "0.8"],
        (0, 0.15),
        ("1", "0.75"),
    ])
    def test_valid_anchor(self, anchor):
        Variation([100, 100], anchor=anchor)

    def test_anchor_property(self):
        v = Variation([100, 200])
        assert v.anchor == (0.5, 0.5)

        v = Variation([100, 200], anchor="TL")
        assert v.anchor == (0, 0)

        v = Variation([100, 200], anchor=[0.1, 0.75])
        assert v.anchor == (0.1, 0.75)

    def test_save_string(self):
        img = Image.new("RGB", (640, 480), color="red")

        v = Variation([100, 200])

        output_path = helper.OUTPUT_PATH / "save/str.jpg"
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True)

        v.save(img, str(output_path))

    def test_save_path(self):
        img = Image.new("RGB", (640, 480), color="red")

        v = Variation([100, 200])

        output_path = helper.OUTPUT_PATH / "save/path.jpg"
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True)

        v.save(img, output_path)

    def test_save_io(self):
        img = Image.new("RGB", (640, 480), color="red")

        v = Variation([100, 200])

        output_path = helper.OUTPUT_PATH / "save/io.jpg"
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True)

        buffer = io.BytesIO()
        v.save(img, buffer)

        buffer.seek(0)
        with open(str(output_path), "wb+") as fp:
            for chunk in buffer:
                fp.write(chunk)
        buffer.close()
