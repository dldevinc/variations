import os

from pilkit.lib import Image
from variations.utils import prepare_image
from variations.variation import Variation

from . import helper


def test_face_detection(face_image_filename):
    input_path = os.path.join(helper.INPUT_PATH, 'faces', face_image_filename)

    img = Image.open(input_path)
    img = prepare_image(img)
    variation = Variation(size=(480, 480), face_detection=True)
    new_img = variation.process(img)

    output_path = os.path.join(helper.OUTPUT_PATH, 'faces', face_image_filename)
    helper.ensure_folder(output_path)
    variation.save(new_img, output_path)

    # check output
    target_path = os.path.join(helper.TARGET_PATH, 'faces', face_image_filename)
    assert helper.image_diff(output_path, target_path) is None
