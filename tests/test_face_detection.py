import os
import unittest
from pilkit.lib import Image
from variations.variation import Variation
from variations.utils import prepare_image
from . import helper


class TestFaceDetection(unittest.TestCase):
    def test_faces(self):
        path = os.path.join(helper.INPUT_PATH, 'faces')
        for filename in sorted(os.listdir(path)):
            variation = Variation(
                size=(480, 480),
                face_detection=True
            )
            img = Image.open(os.path.join(path, filename))
            img = prepare_image(img)
            new_img = variation.process(img)

            output_path = os.path.join(helper.OUTPUT_PATH, 'faces')
            if not os.path.isdir(output_path):
                os.makedirs(output_path)

            variation.save(new_img, os.path.join(output_path, filename))

            # check output
            with self.subTest(filename):
                result_path = os.path.join(helper.OUTPUT_PATH, 'faces', filename)
                target_path = os.path.join(helper.TARGET_PATH, 'faces', filename)
                self.assertIsNone(helper.image_diff(result_path, target_path))
