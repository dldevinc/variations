from pilkit.lib import Image

from variations.processors import ColorOverlay, MakeOpaque, ResizeToFillFace

from . import helper


class TestMakeOpaque:
    input_files = ["processors"]

    def test_files(self, input_file):
        input_file_path = str(helper.INPUT_PATH / input_file)
        with open(input_file_path, "rb") as fp:
            output_path = helper.OUTPUT_PATH / "processors/opaque" / input_file.name
            if not output_path.parent.is_dir():
                output_path.parent.mkdir(parents=True, exist_ok=True)

            img = Image.open(fp)
            new_img = MakeOpaque("#FFFF00").process(img)
            new_img.save(output_path)

            # check output
            target_path = helper.TARGET_PATH / "processors/opaque" / input_file.name
            assert helper.image_diff(output_path, target_path) is None


class TestColorOverlay:
    input_files = ["processors"]

    def test_files(self, input_file):
        input_file_path = str(helper.INPUT_PATH / input_file)
        with open(input_file_path, "rb") as fp:
            output_path = helper.OUTPUT_PATH / "processors/overlay" / input_file.name
            if not output_path.parent.is_dir():
                output_path.parent.mkdir(parents=True, exist_ok=True)

            img = Image.open(fp)
            new_img = ColorOverlay("#FFFF00CA").process(img)

            if output_path.suffix == ".jpg":
                new_img = new_img.convert("RGB")

            new_img.save(output_path)

            # check output
            target_path = helper.TARGET_PATH / "processors/overlay" / input_file.name
            assert helper.image_diff(output_path, target_path) is None


class TestResizeToFillFace:
    input_files = ["faces"]

    def test_files(self, input_file):
        input_file_path = str(helper.INPUT_PATH / input_file)
        with open(input_file_path, "rb") as fp:
            output_path = helper.OUTPUT_PATH / "processors/faces" / input_file.name
            if not output_path.parent.is_dir():
                output_path.parent.mkdir(parents=True, exist_ok=True)

            img = Image.open(fp)
            new_img = ResizeToFillFace(600, 600).process(img)

            if output_path.suffix == ".jpg":
                new_img = new_img.convert("RGB")

            new_img.save(output_path)

            # check output
            target_path = helper.TARGET_PATH / "processors/faces" / input_file.name
            assert helper.image_diff(output_path, target_path) is None
