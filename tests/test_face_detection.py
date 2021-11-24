from pilkit.lib import Image
from variations.utils import prepare_image
from variations.variation import Variation

from . import helper


class TestFaceDetection:
    input_files = ["faces"]

    def test_face_detection(self, input_file):
        input_path = helper.INPUT_PATH / input_file

        img = Image.open(input_path)
        img = prepare_image(img)
        variation = Variation(size=(480, 480), face_detection=True)
        new_img = variation.process(img)

        output_path = helper.OUTPUT_PATH / input_file
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True)

        variation.save(new_img, output_path)

        # check output
        target_path = helper.TARGET_PATH / input_file
        assert helper.image_diff(output_path, target_path) is None
