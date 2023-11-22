from typing import ClassVar

import pytest
from pilkit.lib import Image

from variations import Variation, processors
from variations.typing import Color
from variations.variation import NOT_SET

from . import helper

SIZE_MAP = {
    "fill": {
        "upscale": [
            ((0, 0), (300, 600)),
            ((200, 0), (200, 400)),     # legacy: 200x600
            ((400, 0), (400, 800)),
            ((0, 400), (200, 400)),     # legacy: 300x400
            ((0, 800), (400, 800)),
            ((200, 500), (200, 500)),
            ((200, 800), (200, 800)),
            ((400, 500), (400, 500)),
            ((400, 1000), (400, 1000)),
        ],
        "noupscale": [
            ((0, 0), (300, 600)),
            ((200, 0), (200, 400)),     # legacy: 200x600
            ((400, 0), (300, 600)),
            ((0, 400), (200, 400)),     # legacy: 300x400
            ((0, 800), (300, 600)),
            ((200, 500), (200, 500)),
            ((200, 800), (200, 600)),
            ((400, 500), (300, 500)),
            ((400, 1000), (300, 600)),
        ]
    },
    "fit": {
        "upscale": [
            ((0, 0), (300, 600)),
            ((200, 0), (200, 400)),
            ((400, 0), (400, 800)),
            ((0, 400), (200, 400)),
            ((0, 800), (400, 800)),
            ((200, 500), (200, 400)),
            ((200, 800), (200, 400)),
            ((400, 500), (250, 500)),
            ((400, 1000), (400, 800)),
        ],
        "noupscale": [
            ((0, 0), (300, 600)),
            ((200, 0), (200, 400)),
            ((400, 0), (300, 600)),
            ((0, 400), (200, 400)),
            ((0, 800), (300, 600)),
            ((200, 500), (200, 400)),
            ((200, 800), (200, 400)),
            ((400, 500), (250, 500)),
            ((400, 1000), (300, 600)),
        ]
    },
    "fit_bg": {
        "upscale": [
            ((0, 0), (300, 600)),
            ((200, 0), (200, 400)),
            ((400, 0), (400, 800)),
            ((0, 400), (200, 400)),
            ((0, 800), (400, 800)),
            ((200, 500), (200, 500)),
            ((200, 800), (200, 800)),
            ((400, 500), (400, 500)),
            ((400, 1000), (400, 1000)),
        ],
        "noupscale": [
            ((0, 0), (300, 600)),
            ((200, 0), (200, 400)),
            ((400, 0), (400, 600)),
            ((0, 400), (200, 400)),
            ((0, 800), (300, 800)),
            ((200, 500), (200, 500)),
            ((200, 800), (200, 800)),
            ((400, 500), (400, 500)),
            ((400, 1000), (400, 1000)),
        ]
    },
    "crop": [
        ((0, 0), (300, 600)),
        ((200, 0), (200, 600)),
        ((400, 0), (300, 600)),
        ((0, 400), (300, 400)),
        ((0, 800), (300, 600)),
        ((200, 500), (200, 500)),
        ((200, 800), (200, 600)),
        ((400, 500), (300, 500)),
        ((400, 1000), (300, 600)),
    ]
}


class BaseTest:
    prefix: str = ""
    mode: ClassVar[Variation.Mode] = None
    background: ClassVar[Color] = None

    def _test_files(self, file, size, expected_size, upscale=None, preprocessors=None, postprocessors=None):
        filename = ",".join([
            file.stem,
            "x".join(str(x) if x else "0" for x in size),
            "upscale" if upscale is True else ""
        ]).rstrip(",") + file.suffix

        format_folder = file.parent.stem

        if not preprocessors and not postprocessors:
            overlay_folder = "plain"
        elif postprocessors and isinstance(postprocessors[0], processors.ColorOverlay):
            overlay_folder = "overlay"
        elif preprocessors and isinstance(preprocessors[0], processors.MakeOpaque):
            overlay_folder = "opaque"
        else:
            overlay_folder = "other"

        output_path = helper.OUTPUT_PATH / "formats" / format_folder / self.prefix / overlay_folder / filename
        if not output_path.parent.is_dir():
            output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file, "rb") as fp:
            img = Image.open(fp)
            variation = Variation(
                size=size,
                mode=self.mode,
                upscale=upscale if upscale is not None else NOT_SET,
                background=self.background,
                preprocessors=preprocessors,
                postprocessors=postprocessors
            )
            new_img = variation.process(img)
            assert new_img.size == expected_size
            variation.save(new_img, output_path)

        # check output
        target_path = helper.TARGET_PATH / "formats" / format_folder / self.prefix / overlay_folder / filename
        if target_path.exists():
            assert helper.image_diff(output_path, target_path, mode="RGBA") is None
        else:
            print(f"ERROR: {target_path} not exist")


class TestJpegFill(BaseTest):
    root = "tests/input/formats/jpg"
    prefix = "fill"
    mode = Variation.Mode.FILL

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])


class TestPngFill(BaseTest):
    root = "tests/input/formats/png"
    prefix = "fill"
    mode = Variation.Mode.FILL

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])


class TestWebpFill(BaseTest):
    root = "tests/input/formats/webp"
    prefix = "fill"
    mode = Variation.Mode.FILL

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])


class TestGifFill(BaseTest):
    root = "tests/input/formats/gif"
    prefix = "fill"
    mode = Variation.Mode.FILL

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])


class TestJpegFit(BaseTest):
    root = "tests/input/formats/jpg"
    prefix = "fit"
    mode = Variation.Mode.FIT

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])


class TestPngFit(BaseTest):
    root = "tests/input/formats/png"
    prefix = "fit"
    mode = Variation.Mode.FIT

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])


class TestWebpFit(BaseTest):
    root = "tests/input/formats/webp"
    prefix = "fit"
    mode = Variation.Mode.FIT

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])


class TestGifFit(BaseTest):
    root = "tests/input/formats/gif"
    prefix = "fit"
    mode = Variation.Mode.FIT

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])


class TestJpegFitBg(BaseTest):
    root = "tests/input/formats/jpg"
    prefix = "fit_bg"
    mode = Variation.Mode.FIT
    background = "#FFFF0080"

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])


class TestPngFitBg(BaseTest):
    root = "tests/input/formats/png"
    prefix = "fit_bg"
    mode = Variation.Mode.FIT
    background = "#FFFF0080"

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])


class TestWebpFitBg(BaseTest):
    root = "tests/input/formats/webp"
    prefix = "fit_bg"
    mode = Variation.Mode.FIT
    background = "#FFFF0080"

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])


class TestGifFitBg(BaseTest):
    root = "tests/input/formats/gif"
    prefix = "fit_bg"
    mode = Variation.Mode.FIT
    background = "#FFFF0080"

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["noupscale"])
    def test_noupscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=False, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix]["upscale"])
    def test_upscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, upscale=True, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])


class TestJpegCrop(BaseTest):
    root = "tests/input/formats/jpg"
    prefix = "crop"
    mode = Variation.Mode.CROP

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix])
    def test_plain(self, file, size, expected_size):
        self._test_files(file, size, expected_size)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix])
    def test_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.20)
        ])


class TestPngCrop(BaseTest):
    root = "tests/input/formats/png"
    prefix = "crop"
    mode = Variation.Mode.CROP

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix])
    def test_plain(self, file, size, expected_size):
        self._test_files(file, size, expected_size)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix])
    def test_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix])
    def test_noupscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])


class TestWebpCrop(BaseTest):
    root = "tests/input/formats/webp"
    prefix = "crop"
    mode = Variation.Mode.CROP

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix])
    def test_plain(self, file, size, expected_size):
        self._test_files(file, size, expected_size)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix])
    def test_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix])
    def test_noupscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])


class TestGifCrop(BaseTest):
    root = "tests/input/formats/gif"
    prefix = "crop"
    mode = Variation.Mode.CROP

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix])
    def test_plain(self, file, size, expected_size):
        self._test_files(file, size, expected_size)

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix])
    def test_overlay(self, file, size, expected_size):
        self._test_files(file, size, expected_size, postprocessors=[
            processors.ColorOverlay("#0000FF", 0.10)
        ])

    @pytest.mark.iterdir("file", root)
    @pytest.mark.parametrize("size,expected_size", SIZE_MAP[prefix])
    def test_noupscale_opaque(self, file, size, expected_size):
        self._test_files(file, size, expected_size, preprocessors=[
            processors.MakeOpaque("#FA0000")
        ])
