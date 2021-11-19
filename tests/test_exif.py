from pilkit.lib import Image
from variations.utils import prepare_image
from variations.variation import Variation

from . import helper


class TestExifOrientation:
    input_files = ["exif"]

    def test_exif(self, input_file):
        variation = Variation(size=(1024, 768), clip=False, upscale=True)
        input_file_path = str(helper.INPUT_PATH / input_file)
        with open(input_file_path, "rb") as fp:
            img = Image.open(fp)
            img = prepare_image(img)
            new_img = variation.process(img)

            output_path = helper.OUTPUT_PATH / input_file
            if not output_path.parent.is_dir():
                output_path.parent.mkdir(parents=True)

            variation.save(new_img, output_path)

            # check output
            target_path = helper.TARGET_PATH / input_file
            assert helper.image_diff(output_path, target_path) is None
