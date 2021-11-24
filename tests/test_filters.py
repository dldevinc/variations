from pathlib import Path

from pilkit.lib import Image
from variations import processors
from variations.utils import prepare_image, replace_extension
from variations.variation import Variation

from . import helper


class TestFilters:
    input_files = ["filters"]

    def _test_filter(self, dirname: str, input_file: Path, postprocessors=()):
        variation = Variation(size=(0, 0), postprocessors=postprocessors)
        input_path = str(helper.INPUT_PATH / input_file)
        with open(input_path, "rb") as fp:
            img = Image.open(fp)
            img = prepare_image(img)
            new_img = variation.process(img)

            relative_path = Path("filters") / dirname / input_file.name
            output_path = helper.OUTPUT_PATH / relative_path
            if not output_path.parent.is_dir():
                output_path.parent.mkdir(parents=True)

            variation.save(new_img, output_path)

            # check output
            target_path = helper.TARGET_PATH / relative_path
            assert helper.image_diff(output_path, target_path) is None

    def test_grayscale(self, input_file):
        self._test_filter("grayscale", input_file, [processors.Grayscale()])

    def test_posterize(self, input_file):
        self._test_filter(
            "posterize",
            input_file,
            [processors.MakeOpaque(), processors.Posterize(4)],
        )

    def test_solarize(self, input_file):
        self._test_filter(
            "solarize",
            input_file,
            [processors.MakeOpaque(), processors.Solarize()],
        )

    def test_blur(self, input_file):
        self._test_filter("blur", input_file, [processors.Blur()])

    def test_sharpen(self, input_file):
        self._test_filter("sharpen", input_file, [processors.Sharpen()])

    def test_smooth(self, input_file):
        self._test_filter("smooth", input_file, [processors.Smooth()])

    def test_edge_enchance(self, input_file):
        self._test_filter(
            "edge_enchance", input_file, [processors.EdgeEnhance()]
        )

    def test_unsharp_mask(self, input_file):
        self._test_filter(
            "unsharp_mask", input_file, [processors.UnsharpMask()]
        )

    def test_box_blur(self, input_file):
        self._test_filter("box_blur", input_file, [processors.BoxBlur(10)])

    def test_gaussian_blur(self, input_file):
        self._test_filter(
            "gaussian_blur", input_file, [processors.GaussianBlur(10)]
        )

    def test_stack_blur(self, input_file):
        if processors.STACK_BLUR_SUPPORT:
            self._test_filter(
                "stack_blur", input_file, [processors.StackBlur(10)]
            )


class TestCustomFilter:
    input_files = ["filters"]

    def test_custom(self, input_file: Path):
        if not processors.STACK_BLUR_SUPPORT:
            return

        variation = Variation(
            size=(120, 80),
            face_detection=True,
            format="webp",
            webp=dict(quality=0,),
            preprocessors=[processors.MakeOpaque("#FFFF00")],
            postprocessors=[processors.StackBlur(10)],
        )

        input_path = str(helper.INPUT_PATH / input_file)
        with open(input_path, "rb") as fp:
            img = Image.open(fp)
            img = prepare_image(img)
            new_img = variation.process(img)

            relative_path = Path("filters/custom") / input_file.name
            output_path = helper.OUTPUT_PATH / relative_path
            if not output_path.parent.is_dir():
                output_path.parent.mkdir(parents=True)

            output_path = variation.replace_extension(output_path)
            variation.save(new_img, output_path)

            # check output
            target_path = helper.TARGET_PATH / relative_path
            target_path = replace_extension(target_path, "webp")
            assert helper.image_diff(output_path, target_path) is None
