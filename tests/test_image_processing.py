import os
from pathlib import Path

import pytest
from pilkit.lib import Image
from variations import processors
from variations.utils import prepare_image
from variations.variation import Variation

from . import helper


CLIP = True
NOCLIP = False
UPSCALE = True
NOUPSCALE = False
SIZE_MAP = {
    CLIP: {
        NOUPSCALE: {
            (0, 0): (300, 600),
            (200, 0): (200, 600),
            (400, 0): (300, 600),
            (0, 400): (300, 400),
            (0, 800): (300, 600),
            (200, 500): (200, 500),
            (200, 800): (200, 600),
            (400, 500): (300, 500),
            (400, 1000): (300, 600),
        },
        UPSCALE: {
            (0, 0): (300, 600),
            (200, 0): (200, 600),
            (400, 0): (400, 800),
            (0, 400): (300, 400),
            (0, 800): (400, 800),
            (200, 500): (200, 500),
            (200, 800): (200, 800),
            (400, 500): (400, 500),
            (400, 1000): (400, 1000),
        },
    },
    NOCLIP: {
        NOUPSCALE: {
            (0, 0): (300, 600),
            (200, 0): (200, 400),
            (400, 0): (400, 600),
            (0, 400): (200, 400),
            (0, 800): (300, 800),
            (200, 500): (200, 500),
            (200, 800): (200, 800),
            (400, 500): (400, 500),
            (400, 1000): (400, 1000),
        },
        UPSCALE: {
            (0, 0): (300, 600),
            (200, 0): (200, 400),
            (400, 0): (400, 800),
            (0, 400): (200, 400),
            (0, 800): (400, 800),
            (200, 500): (200, 500),
            (200, 800): (200, 800),
            (400, 500): (400, 500),
            (400, 1000): (400, 1000),
        },
    },
}


class TestVariationProcess:
    input_files = ["jpg", "png", "gif", "webp"]

    def _iterate_sizes(self, img: Image, input_file: Path, clip: bool, upscale: bool):
        results = []
        source_size = img.size
        filename, ext = os.path.splitext(input_file.name)

        for size, canvas in SIZE_MAP[clip][upscale].items():
            filename_parts = [
                filename,
                "x".join(map(str, size)),
                "noclip" if not clip else "",
                "upscale" if upscale else "",
            ]
            output_filename = ",".join(filter(bool, filename_parts)) + ext
            relative_path = input_file.parent / "plain" / output_filename

            variation = Variation(
                size=size,
                clip=clip,
                upscale=upscale
            )
            assert variation.get_output_size(source_size) == canvas

            output_path = helper.OUTPUT_PATH / relative_path
            if not output_path.parent.is_dir():
                output_path.parent.mkdir(parents=True)

            new_img = variation.process(img)
            assert new_img.size == canvas

            variation.save(new_img, output_path)

            target_path = helper.TARGET_PATH / relative_path

            results.append((output_path, target_path))

        for output_path, target_path in results:
            assert helper.image_diff(output_path, target_path) is None

    @pytest.mark.parametrize("upscale", [True, False])
    @pytest.mark.parametrize("clip", [True, False])
    def test_file(self, input_file, clip, upscale):
        input_file_path = str(helper.INPUT_PATH / input_file)
        with open(input_file_path, "rb") as fp:
            img = Image.open(fp)
            img = prepare_image(img)
            self._iterate_sizes(img, input_file, clip, upscale)


class TestOverlayedVariationProcess(TestVariationProcess):
    def _iterate_sizes(self, img: Image, input_file: Path, clip: bool, upscale: bool):
        results = []
        source_size = img.size
        filename, ext = os.path.splitext(input_file.name)

        for size, canvas in SIZE_MAP[clip][upscale].items():
            filename_parts = [
                filename,
                "x".join(map(str, size)),
                "noclip" if not clip else "",
                "upscale" if upscale else "",
            ]
            output_filename = ",".join(filter(bool, filename_parts)) + ext
            relative_path = input_file.parent / "overlay" / output_filename

            variation = Variation(
                size=size,
                clip=clip,
                upscale=upscale,
                postprocessors=[
                    processors.ColorOverlay("#0000FF", 0.10)
                ]
            )
            assert variation.get_output_size(source_size) == canvas

            output_path = helper.OUTPUT_PATH / relative_path
            if not output_path.parent.is_dir():
                output_path.parent.mkdir(parents=True)

            new_img = variation.process(img)
            assert new_img.size == canvas

            variation.save(new_img, output_path)

            target_path = helper.TARGET_PATH / relative_path

            results.append((output_path, target_path))

        for output_path, target_path in results:
            assert helper.image_diff(output_path, target_path) is None
