import io
from pathlib import Path

import pytest
from PIL import Image
from pilkit.exceptions import UnknownFormat

from variations import utils

from . import helper


def test_guess_format():
    assert utils.guess_format("image.jpg") == "JPEG"
    assert utils.guess_format("image.jpeg") == "JPEG"
    assert utils.guess_format("image.WebP") == "WEBP"
    assert utils.guess_format("image") is None
    assert utils.guess_format("image.mp3") is None

    assert utils.guess_format(Path("/tmp/image.png")) == "PNG"
    assert utils.guess_format(Path("/tmp/image.webP")) == "WEBP"
    assert utils.guess_format(Path("/tmp/image")) is None
    assert utils.guess_format(Path("/tmp/image.mp3")) is None

    with io.BytesIO() as file:
        with pytest.raises(ValueError):
            utils.guess_format(file)

        file.name = "image.gif"
        assert utils.guess_format(file) == "GIF"

        file.name = "image.mp3"
        assert utils.guess_format(file) is None


def test_replace_extension():
    with pytest.raises(UnknownFormat):
        utils.replace_extension("image.jpg", "jpg")
        utils.replace_extension("image.jpg", "mp3")
        utils.replace_extension(Path("image.jpg"), "jpg")

    assert utils.replace_extension("image.jpg", "jpeg") == "image.jpg"
    assert utils.replace_extension("image.jpg", "PNG") == "image.png"
    assert utils.replace_extension("image.jpg", "JPEG2000") == "image.jp2"
    assert utils.replace_extension("image.jpg", "webp") == "image.webp"
    assert utils.replace_extension("image.jpg", "tiff") == "image.tif"
    assert utils.replace_extension("image", "png") == "image.png"

    assert utils.replace_extension(Path("image.jpg"), "jpeg") == Path("image.jpg")
    assert utils.replace_extension(Path("image.jpg"), "PNG") == Path("image.png")
    assert utils.replace_extension(Path("image"), "webp") == Path("image.webp")


class TestSaveBase:
    file = None

    def _test_file(self, to_format):
        if to_format == "JPEG":
            suffix = ".jpg"
        else:
            suffix = f".{to_format.lower()}"

        output_path = helper.OUTPUT_PATH / "save" / self.file.stem / self.file.name
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path = output_path.with_suffix(suffix)

        img = Image.open(self.file)
        utils.save_image(img, output_path, to_format)

        target_path = helper.TARGET_PATH / "save" / self.file.stem / output_path.name
        if target_path.exists():
            assert helper.image_diff(output_path, target_path) is None
        else:
            print(f"ERROR: {target_path} not exist")


class TestSave1(TestSaveBase):
    file = helper.INPUT_PATH / "formats/png/1.png"

    def test_jpg(self):
        self._test_file("JPEG")

    def test_gif(self):
        self._test_file("GIF")

    def test_png(self):
        self._test_file("PNG")

    def test_webp(self):
        self._test_file("WEBP")


class TestSaveL(TestSaveBase):
    file = helper.INPUT_PATH / "formats/png/L.png"

    def test_jpg(self):
        self._test_file("JPEG")

    def test_gif(self):
        self._test_file("GIF")

    def test_png(self):
        self._test_file("PNG")

    def test_webp(self):
        self._test_file("WEBP")


class TestSaveLA(TestSaveBase):
    file = helper.INPUT_PATH / "formats/png/LA.png"

    def test_jpg(self):
        self._test_file("JPEG")

    def test_gif(self):
        self._test_file("GIF")

    def test_png(self):
        self._test_file("PNG")

    def test_webp(self):
        self._test_file("WEBP")


class TestSaveLA2(TestSaveBase):
    file = helper.INPUT_PATH / "formats/png/LA2.png"

    def test_jpg(self):
        self._test_file("JPEG")

    def test_gif(self):
        self._test_file("GIF")

    def test_png(self):
        self._test_file("PNG")

    def test_webp(self):
        self._test_file("WEBP")


class TestSaveP(TestSaveBase):
    file = helper.INPUT_PATH / "formats/png/P.png"

    def test_jpg(self):
        self._test_file("JPEG")

    def test_gif(self):
        self._test_file("GIF")

    def test_png(self):
        self._test_file("PNG")

    def test_webp(self):
        self._test_file("WEBP")


class TestSavePA(TestSaveBase):
    file = helper.INPUT_PATH / "formats/png/PA.png"

    def test_jpg(self):
        self._test_file("JPEG")

    def test_gif(self):
        self._test_file("GIF")

    def test_png(self):
        self._test_file("PNG")

    def test_webp(self):
        self._test_file("WEBP")


class TestSaveRGB(TestSaveBase):
    file = helper.INPUT_PATH / "formats/png/RGB.png"

    def test_jpg(self):
        self._test_file("JPEG")

    def test_gif(self):
        self._test_file("GIF")

    def test_png(self):
        self._test_file("PNG")

    def test_webp(self):
        self._test_file("WEBP")


class TestSaveRGBA(TestSaveBase):
    file = helper.INPUT_PATH / "formats/png/RGBA.png"

    def test_jpg(self):
        self._test_file("JPEG")

    def test_gif(self):
        self._test_file("GIF")

    def test_png(self):
        self._test_file("PNG")

    def test_webp(self):
        self._test_file("WEBP")


class TestSaveRGBA2(TestSaveBase):
    file = helper.INPUT_PATH / "formats/png/RGBA2.png"

    def test_jpg(self):
        self._test_file("JPEG")

    def test_gif(self):
        self._test_file("GIF")

    def test_png(self):
        self._test_file("PNG")

    def test_webp(self):
        self._test_file("WEBP")
