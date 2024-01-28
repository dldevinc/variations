import pytest
from pilkit.lib import Image

from variations.processors import *
from variations.processors.face_detection import CropFace, ResizeToFillFace
from variations.utils import save_image

from . import helper


@pytest.mark.iterdir("file", "tests/input/processors")
class TestMakeOpaque:
    def test_processor(self, file):
        output_path = helper.OUTPUT_PATH / "processors/opaque" / file.name
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        img = Image.open(file)
        new_img = MakeOpaque("#FFFF00").process(img)
        new_img.save(output_path)

        # check output
        target_path = helper.TARGET_PATH / "processors/opaque" / file.name
        if target_path.exists():
            assert helper.image_diff(output_path, target_path) is None
        else:
            print(f"ERROR: {target_path} not exist")


@pytest.mark.iterdir("file", "tests/input/processors")
@pytest.mark.parametrize("size", (
    (200, None),
    (400, None),
    (None, 200),
    (None, 800),
    (200, 500),
    (200, 800),
    (400, 500),
    (400, 1000),
))
class TestCrop:
    def test_processor(self, file, size):
        folder = "x".join(str(x) if x else "0" for x in size)

        output_path = helper.OUTPUT_PATH / "processors/crop" / folder / file.name
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        img = Image.open(file)
        new_img = Crop(*size).process(img)

        if new_img.mode == "RGBA" and output_path.suffix == ".jpg":
            new_img = new_img.convert("RGB")

        new_img.save(output_path)

        # check output
        target_path = helper.TARGET_PATH / "processors/crop" / folder / file.name
        if target_path.exists():
            assert helper.image_diff(output_path, target_path, mode="RGBA") is None
        else:
            print(f"ERROR: {target_path} not exist")


@pytest.mark.iterdir("file", "tests/input/processors")
class TestColorOverlay:
    def test_processor(self, file):
        output_path = helper.OUTPUT_PATH / "processors/overlay" / file.name
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        img = Image.open(file)
        new_img = ColorOverlay("#FFFF00").process(img)

        if new_img.mode == "RGBA" and output_path.suffix == ".jpg":
            new_img = new_img.convert("RGB")

        new_img.save(output_path)

        # check output
        target_path = helper.TARGET_PATH / "processors/overlay" / file.name
        if target_path.exists():
            assert helper.image_diff(output_path, target_path) is None
        else:
            print(f"ERROR: {target_path} not exist")


@pytest.mark.iterdir("file", "tests/input/faces")
@pytest.mark.parametrize("size", (
    (200, None),
    (400, None),
    (None, 200),
    (None, 800),
    (200, 500),
    (200, 800),
    (400, 500),
    (400, 1000),
))
class TestCropFace:
    def test_processor(self, file, size):
        folder = "x".join(str(x) if x else "0" for x in size)

        output_path = helper.OUTPUT_PATH / "processors/crop_face" / folder / file.name
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        img = Image.open(file)
        new_img = CropFace(*size).process(img)

        if new_img.mode == "RGBA" and output_path.suffix == ".jpg":
            new_img = new_img.convert("RGB")

        new_img.save(output_path)

        # check output
        target_path = helper.TARGET_PATH / "processors/crop_face" / folder / file.name
        if target_path.exists():
            assert helper.image_diff(output_path, target_path) is None
        else:
            print(f"ERROR: {target_path} not exist")


@pytest.mark.iterdir("file", "tests/input/processors")
@pytest.mark.parametrize("size", (
    (200, None),
    (400, None),
    (None, 200),
    (None, 800),
    (200, 500),
    (200, 800),
    (400, 500),
    (400, 1000),
))
class TestResizeToFit:
    def test_processor(self, file, size):
        folder = "x".join(str(x) if x else "0" for x in size)

        output_path = helper.OUTPUT_PATH / "processors/fit" / folder / file.name
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        img = Image.open(file)
        new_img = ResizeToFit(
            *size,
            upscale=True,
            mat_color=(255, 255, 0)
        ).process(img)

        if new_img.mode == "RGBA" and output_path.suffix == ".jpg":
            new_img = new_img.convert("RGB")

        new_img.save(output_path)

        # check output
        target_path = helper.TARGET_PATH / "processors/fit" / folder / file.name
        if target_path.exists():
            assert helper.image_diff(output_path, target_path) is None
        else:
            print(f"ERROR: {target_path} not exist")


@pytest.mark.iterdir("file", "tests/input/faces")
@pytest.mark.parametrize("size", ([400, 400], [200, 200]))
@pytest.mark.parametrize("upscale", (False, True))
class TestResizeToFillFace:
    def test_processor(self, file, size, upscale):
        folder = "x".join(str(x) if x else "0" for x in size) + (" (upscale)" if upscale else "")

        output_path = helper.OUTPUT_PATH / "processors/fill_face" / folder / file.name
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        img = Image.open(file)
        new_img = ResizeToFillFace(*size, upscale=upscale).process(img)

        if new_img.mode == "RGBA" and output_path.suffix == ".jpg":
            new_img = new_img.convert("RGB")

        new_img.save(output_path)

        # check output
        target_path = helper.TARGET_PATH / "processors/fill_face" / folder / file.name
        if target_path.exists():
            assert helper.image_diff(output_path, target_path) is None
        else:
            print(f"ERROR: {target_path} not exist")


class TestFilters:
    def _test_processor(self, file, filter, folder):
        output_path = helper.OUTPUT_PATH / "processors/filters" / folder / file.name
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        img = Image.open(file)
        new_img = filter.process(img)
        save_image(new_img, output_path)

        # check output
        target_path = helper.TARGET_PATH / "processors/filters" / folder / file.name
        if target_path.exists():
            assert helper.image_diff(output_path, target_path) is None
        else:
            print(f"ERROR: {target_path} not exist")

    @pytest.mark.iterdir("file", "tests/input/processors")
    def test_grayscale(self, file):
        self._test_processor(file, Grayscale(), folder="grayscale")

    @pytest.mark.iterdir("file", "tests/input/processors")
    def test_gaussian_blur(self, file):
        with open(file, "rb") as fp:
            mode = Image.open(fp).mode

        if mode != "1":
            self._test_processor(file, GaussianBlur(5), folder="gaussian_blur")

    @pytest.mark.iterdir("file", "tests/input/processors")
    def test_box_blur(self, file):
        with open(file, "rb") as fp:
            mode = Image.open(fp).mode

        if mode != "1":
            self._test_processor(file, BoxBlur(2), folder="box_blur")

    @pytest.mark.iterdir("file", "tests/input/processors")
    def test_stack_blur(self, file):
        self._test_processor(file, StackBlur(10), folder="stack_blur")
