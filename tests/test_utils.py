import io
import os
from pathlib import Path

import pytest
from PIL import Image
from pilkit.utils import save_image
from variations import utils

from . import helper


def test_guess_format():
    assert utils.guess_format('image.jpg') == 'JPEG'
    assert utils.guess_format('image.jpeg') == 'JPEG'
    assert utils.guess_format('image.WebP') == 'WEBP'
    assert utils.guess_format('image') is None
    assert utils.guess_format('image.mp3') is None

    assert utils.guess_format(Path('/tmp/image.jpeg')) == 'JPEG'
    assert utils.guess_format(Path('/tmp/image')) is None
    assert utils.guess_format(Path('/tmp/image.mp3')) is None

    with io.BytesIO() as file:
        assert utils.guess_format(file) is None

        file.name = 'image.gif'
        assert utils.guess_format(file) == 'GIF'

        file.name = 'image.mp3'
        assert utils.guess_format(file) is None


def test_replace_extension():
    assert utils.replace_extension('image.jpg', 'jpg') == 'image.jpg'
    assert utils.replace_extension('image.jpg', 'jpeg') == 'image.jpg'
    assert utils.replace_extension('image.jpg', 'PNG') == 'image.png'
    assert utils.replace_extension('image.jpg', 'JPEG2000') == 'image.j2k'
    assert utils.replace_extension('image.jpg', 'webp') == 'image.webp'
    assert utils.replace_extension('image.jpg', 'mp3') == 'image.jpg'

    assert utils.replace_extension(Path('image.jpg'), 'jpg') == 'image.jpg'
    assert utils.replace_extension(Path('image.jpg'), 'PNG') == 'image.png'


@pytest.mark.parametrize('format', ['png', 'jpeg', 'tiff', 'gif', 'webp'])
@pytest.mark.parametrize('source_folder', ['png', 'jpg', 'gif', 'webp'])
def test_opaque_background(source_folder, format):
    input_folder = os.path.join(helper.INPUT_PATH, source_folder)
    for filename in sorted(os.listdir(input_folder)):
        input_path = os.path.join(input_folder, filename)

        output_path = os.path.join(
            helper.OUTPUT_PATH, 'opaque', source_folder, format, filename
        )
        output_path = utils.replace_extension(output_path, format)
        helper.ensure_folder(output_path)

        original = Image.open(input_path)
        img = utils.prepare_image(original, background_color=(255, 0, 0, 128))
        save_image(img, output_path, format=format)

        target_path = os.path.join(
            helper.TARGET_PATH, 'opaque', source_folder, format, filename
        )
        target_path = utils.replace_extension(target_path, format)
        assert helper.image_diff(output_path, target_path) is None
