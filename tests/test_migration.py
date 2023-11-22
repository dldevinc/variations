from abc import ABC, abstractmethod

import pytest
from pilkit.lib import Image

from variations import Variation

from . import helper


class MigrationBase(ABC):
    folder = ""

    @abstractmethod
    def get_legacy_variation(self, size, upscale):
        raise NotImplementedError

    @abstractmethod
    def get_modern_variation(self, size, upscale):
        raise NotImplementedError

    def make_legacy_file(self, file, size, upscale):
        variation = self.get_legacy_variation(size, upscale)

        folder = self.folder + ("-upscale" if upscale else "")
        filename = file.stem + ", " + "x".join(str(x) if x else "0" for x in size) + file.suffix

        legacy_output_path = helper.OUTPUT_PATH / "migration/legacy" / folder / filename
        if not legacy_output_path.parent.is_dir():
            legacy_output_path.parent.mkdir(parents=True, exist_ok=True)

        new_img = variation.process(Image.open(file))
        variation.save(new_img, legacy_output_path)
        return legacy_output_path

    def make_modern_file(self, file, size, upscale):
        variation = self.get_modern_variation(size, upscale)

        folder = self.folder + ("-upscale" if upscale else "")
        filename = file.stem + ", " + "x".join(str(x) if x else "0" for x in size) + file.suffix

        modern_output_path = helper.OUTPUT_PATH / "migration/modern" / folder / filename
        if not modern_output_path.parent.is_dir():
            modern_output_path.parent.mkdir(parents=True, exist_ok=True)

        new_img = variation.process(Image.open(file))
        variation.save(new_img, modern_output_path)
        return modern_output_path

    def test_processing(self, file, size, upscale):
        assert helper.image_diff(
            self.make_legacy_file(file, size, upscale),
            self.make_modern_file(file, size, upscale)
        ) is None


@pytest.mark.iterdir("file", "tests/input/migration")
@pytest.mark.parametrize("size", (
    (200, 500),
    (200, 800),
    (400, 500),
    (400, 1000),
))
@pytest.mark.parametrize("upscale", (False, True))
class TestClip(MigrationBase):
    folder = "clip"

    def get_legacy_variation(self, size, upscale):
        return Variation(
            size=size,
            clip=True,
            upscale=upscale
        )

    def get_modern_variation(self, size, upscale):
        return Variation(
            size=size,
            mode=Variation.Mode.FILL,
            upscale=upscale
        )


@pytest.mark.iterdir("file", "tests/input/migration")
@pytest.mark.parametrize("size", (
    (200, 0),
    (400, 0),
    (0, 200),
    (0, 800),
))
@pytest.mark.parametrize("upscale", (False,))
class TestClipNoUpscaleOneDimension(MigrationBase):
    folder = "clip-1dim"

    def get_legacy_variation(self, size, upscale):
        return Variation(
            size=size,
            clip=True,
            upscale=upscale
        )

    def get_modern_variation(self, size, upscale):
        return Variation(
            size=size,
            mode=Variation.Mode.CROP,
        )

    def test_processing(self, file, size, upscale):
        assert helper.image_diff(
            self.make_legacy_file(file, size, upscale),
            self.make_modern_file(file, size, upscale),
            mode="RGBA"
        ) is None


@pytest.mark.iterdir("file", "tests/input/migration")
@pytest.mark.parametrize("size", (
    (200, 0),
    (0, 200),
))
@pytest.mark.parametrize("upscale", (True,))
class TestClipUpscaleOneDimensionCrop(MigrationBase):
    folder = "clip-1dim"

    def get_legacy_variation(self, size, upscale):
        return Variation(
            size=size,
            clip=True,
            upscale=upscale
        )

    def get_modern_variation(self, size, upscale):
        return Variation(
            size=size,
            mode=Variation.Mode.CROP
        )


@pytest.mark.iterdir("file", "tests/input/migration")
@pytest.mark.parametrize("size", (
    (400, 0),
    (0, 800),
))
@pytest.mark.parametrize("upscale", (True,))
class TestClipUpscaleOneDimensionFill(MigrationBase):
    folder = "clip-1dim"

    def get_legacy_variation(self, size, upscale):
        return Variation(
            size=size,
            clip=True,
            upscale=upscale
        )

    def get_modern_variation(self, size, upscale):
        return Variation(
            size=size,
            mode=Variation.Mode.FILL,
            upscale=upscale
        )


@pytest.mark.iterdir("file", "tests/input/migration")
@pytest.mark.parametrize("size", (
    (200, 0),
    (400, 0),
    (0, 200),
    (0, 800),
    (200, 500),
    (200, 800),
    (400, 500),
    (400, 1000),
))
@pytest.mark.parametrize("upscale", (False, True))
class TestNoclip(MigrationBase):
    folder = "noclip"

    def get_legacy_variation(self, size, upscale):
        return Variation(
            size=size,
            clip=False,
            upscale=upscale
        )

    def get_modern_variation(self, size, upscale):
        return Variation(
            size=size,
            mode=Variation.Mode.FIT,
            background=(255, 255, 255, 0),
            upscale=upscale
        )


@pytest.mark.iterdir("file", "tests/input/migration")
@pytest.mark.parametrize("size", (
    (200, 0),
    (400, 0),
    (0, 200),
    (0, 800),
    (200, 500),
    (200, 800),
    (400, 500),
    (400, 1000),
))
@pytest.mark.parametrize("upscale", (False, True))
class TestNoclipMaxWidthMaxHeight(MigrationBase):
    folder = "noclip-max-wh"

    def get_legacy_variation(self, size, upscale):
        return Variation(
            size=(0, 0),
            clip=False,
            max_width=size[0],
            max_height=size[1],
            upscale=upscale
        )

    def get_modern_variation(self, size, upscale):
        return Variation(
            size=size,
            mode=Variation.Mode.FIT,
            upscale=upscale
        )

    def test_processing(self, file, size, upscale):
        assert helper.image_diff(
            self.make_legacy_file(file, size, upscale),
            self.make_modern_file(file, size, upscale),
            mode="RGBA"
        ) is None
