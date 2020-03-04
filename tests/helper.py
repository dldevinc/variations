import os

from pilkit.lib import Image, ImageChops

TESTING_DIR = os.path.abspath(os.path.dirname(__file__))
INPUT_PATH = os.path.join(TESTING_DIR, 'input')
OUTPUT_PATH = os.path.join(TESTING_DIR, 'output')
TARGET_PATH = os.path.join(TESTING_DIR, 'target')


def image_diff(image1_path, image2_path):
    with open(image1_path, 'rb') as result_fp:
        with open(image2_path, 'rb') as target_fp:
            result_img = Image.open(result_fp)
            target_img = Image.open(target_fp)
            return ImageChops.difference(result_img, target_img).getbbox()


def ensure_folder(*args):
    path = os.path.join(*args)
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
