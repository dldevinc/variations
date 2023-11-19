import pytest
from pilkit.lib import Image

from variations.variation import Variation

from . import helper


class TestExifOrientation:
    @pytest.mark.iterdir("file", "tests/input/exif")
    def test_exif(self, file):
        output_path = helper.OUTPUT_PATH / "exif" / file.name
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        variation = Variation(size=(1024, 768))
        with open(file, "rb") as fp:
            img = Image.open(fp)
            new_img = variation.process(img)
        variation.save(new_img, output_path)

        # check output
        target_path = helper.TARGET_PATH / "exif" / file.name
        if target_path.exists():
            assert helper.image_diff(output_path, target_path) is None
        else:
            print(f"ERROR: {target_path} not exist")
