from pathlib import Path

from pilkit.lib import Image, ImageChops

TESTING_DIR = Path(__file__).parent
INPUT_PATH = TESTING_DIR / "input"
OUTPUT_PATH = TESTING_DIR / "output"
TARGET_PATH = TESTING_DIR / "target"


def image_diff(image1_path, image2_path):
    with open(str(image1_path), "rb") as result_fp:
        with open(str(image2_path), "rb") as target_fp:
            result_img = Image.open(result_fp)
            target_img = Image.open(target_fp)
            return ImageChops.difference(result_img, target_img).getbbox()
