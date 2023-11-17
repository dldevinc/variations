import io
from pathlib import Path

import pytest
from PIL import Image
from pilkit.exceptions import UnknownFormat
from pilkit.utils import save_image
from variations import utils, conf

from . import helper


def test_guess_format():
    assert utils.guess_format("image.jpg") == "JPEG"
    assert utils.guess_format("image.jpeg") == "JPEG"
    assert utils.guess_format("image.WebP") == "WEBP"
    assert utils.guess_format("image") == conf.FALLBACK_FORMAT
    assert utils.guess_format("image.mp3") == conf.FALLBACK_FORMAT

    assert utils.guess_format(Path("/tmp/image.png")) == "PNG"
    assert utils.guess_format(Path("/tmp/image.webP")) == "WEBP"
    assert utils.guess_format(Path("/tmp/image")) == conf.FALLBACK_FORMAT
    assert utils.guess_format(Path("/tmp/image.mp3")) == conf.FALLBACK_FORMAT

    with io.BytesIO() as file:
        with pytest.raises(ValueError):
            utils.guess_format(file)

        file.name = "image.gif"
        assert utils.guess_format(file) == "GIF"

        file.name = "image.mp3"
        assert utils.guess_format(file) == conf.FALLBACK_FORMAT


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


@pytest.mark.parametrize("format", ["png", "jpeg", "tiff", "gif", "webp"])
@pytest.mark.parametrize("source_folder", ["png", "jpg", "gif", "webp"])
def test_opaque_background(source_folder, format):  # TODO: зачем это?
    results = []

    input_folder = helper.INPUT_PATH / source_folder
    for input_path in sorted(input_folder.iterdir()):
        original = Image.open(input_path)
        img = utils.prepare_image(original, background_color=(255, 0, 0, 128))

        relative_path = Path("opaque") / source_folder / format / input_path.relative_to(input_folder)
        output_path = helper.OUTPUT_PATH / relative_path
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path = utils.replace_extension(output_path, format)
        save_image(img, str(output_path), format=format)

        target_path = helper.TARGET_PATH / relative_path
        target_path = utils.replace_extension(target_path, format)

        results.append((output_path, target_path))

    for output_path, target_path in results:
        assert helper.image_diff(output_path, target_path) is None
