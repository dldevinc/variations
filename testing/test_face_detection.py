import os
import unittest
from PIL import Image, ImageChops
from variations.variation import Variation
from variations.utils import prepare_image

TEST_IMAGES = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.join(TEST_IMAGES, 'output')
TARGET_PATH = os.path.join(TEST_IMAGES, 'target')


class TestFaceDetection(unittest.TestCase):
    def test_faces(self):
        path = os.path.join(TEST_IMAGES, 'faces')
        for filename in sorted(os.listdir(path)):
            variation = Variation(
                size=(480, 480),
                face_detection=True
            )
            img = Image.open(os.path.join(path, filename))
            img = prepare_image(img)
            new_img = variation.process(img)

            output_path = os.path.join(OUTPUT_PATH, 'faces')
            if not os.path.isdir(output_path):
                os.makedirs(output_path)

            variation.save(
                new_img,
                os.path.join(output_path, filename)
            )

            # check output
            with self.subTest(filename):
                result_path = os.path.join(OUTPUT_PATH, 'faces', filename)
                target_path = os.path.join(TARGET_PATH, 'faces', filename)
                with open(result_path, 'rb') as result_fp:
                    with open(target_path, 'rb') as target_fp:
                        result_img = Image.open(result_fp)
                        target_img = Image.open(target_fp)
                        diff = ImageChops.difference(result_img, target_img)
                        self.assertIsNone(diff.getbbox())
