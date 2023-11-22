from pathlib import Path

from pilkit.lib import Image, ImageChops

TESTING_DIR = Path(__file__).parent
INPUT_PATH = TESTING_DIR / "input"
OUTPUT_PATH = TESTING_DIR / "output"
TARGET_PATH = TESTING_DIR / "target"


def image_diff(image1_path, image2_path, mode=None):
    result_img = Image.open(image1_path)
    target_img = Image.open(image2_path)
    if mode is not None:
        result_img = result_img.convert(mode)
        target_img = target_img.convert(mode)
    return ImageChops.difference(result_img, target_img).getbbox()
