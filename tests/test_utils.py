import io
from pathlib import Path

import pytest
from PIL import Image
from pilkit.utils import save_image
from variations import utils

from . import helper


def test_guess_format():
    assert utils.guess_format("image.jpg") == "JPEG"
    assert utils.guess_format("image.jpeg") == "JPEG"
    assert utils.guess_format("image.WebP") == "WEBP"
    assert utils.guess_format("image") is None
    assert utils.guess_format("image.mp3") is None

    assert utils.guess_format(Path("/tmp/image.jpeg")) == "JPEG"
    assert utils.guess_format(Path("/tmp/image")) is None
    assert utils.guess_format(Path("/tmp/image.mp3")) is None

    with io.BytesIO() as file:
        assert utils.guess_format(file) is None

        file.name = "image.gif"
        assert utils.guess_format(file) == "GIF"

        file.name = "image.mp3"
        assert utils.guess_format(file) is None


def test_replace_extension():
    assert utils.replace_extension("image.jpg", "jpg") == "image.jpg"
    assert utils.replace_extension("image.jpg", "jpeg") == "image.jpg"
    assert utils.replace_extension("image.jpg", "PNG") == "image.png"
    assert utils.replace_extension("image.jpg", "JPEG2000") == "image.j2k"
    assert utils.replace_extension("image.jpg", "webp") == "image.webp"
    assert utils.replace_extension("image.jpg", "mp3") == "image.jpg"

    assert utils.replace_extension(Path("image.jpg"), "jpg") == "image.jpg"
    assert utils.replace_extension(Path("image.jpg"), "PNG") == "image.png"


@pytest.mark.parametrize("format", ["png", "jpeg", "tiff", "gif", "webp"])
@pytest.mark.parametrize("source_folder", ["png", "jpg", "gif", "webp"])
def test_opaque_background(source_folder, format):
    results = []

    input_folder = helper.INPUT_PATH / source_folder
    for input_path in sorted(input_folder.iterdir()):
        original = Image.open(input_path)
        img = utils.prepare_image(original, background_color=(255, 0, 0, 128))

        relative_path = Path("opaque") / source_folder / format / input_path.relative_to(input_folder)
        output_path = helper.OUTPUT_PATH / relative_path
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True)

        output_path = utils.replace_extension(output_path, format)
        save_image(img, output_path, format=format)

        target_path = helper.TARGET_PATH / relative_path
        target_path = utils.replace_extension(target_path, format)

        results.append((output_path, target_path))

    for output_path, target_path in results:
        assert helper.image_diff(output_path, target_path) is None
