import os

from pilkit.lib import Image
from variations import processors
from variations.utils import prepare_image, replace_extension
from variations.variation import Variation

from . import helper


class TestVariationProcess:
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

    def _process_variation(self, img, dirname, filename, clip, upscale):
        source_size = img.size
        fileroot, ext = os.path.splitext(filename)

        def process(variation, folder):
            output_path = os.path.join(
                helper.OUTPUT_PATH, dirname, folder, output_filename
            )
            helper.ensure_folder(output_path)

            assert variation.get_output_size(source_size) == canvas
            new_img = variation.process(img)
            assert new_img.size == canvas

            variation.save(new_img, output_path)

            # check output
            target_path = os.path.join(
                helper.TARGET_PATH, dirname, folder, output_filename
            )
            assert helper.image_diff(output_path, target_path) is None

        for size, canvas in self.SIZE_MAP[clip][upscale].items():
            filename_params = [
                fileroot,
                'x'.join(map(str, size)),
                'noclip' if not clip else '',
                'upscale' if upscale else '',
            ]
            output_filename = ','.join(p for p in filename_params if p) + ext

            plain_variation = Variation(size=size, clip=clip, upscale=upscale,)
            overlay_variation = plain_variation.copy()
            overlay_variation.postprocessors.append(
                processors.ColorOverlay('#0000FF', 0.10)
            )

            process(plain_variation, 'plain')
            process(overlay_variation, 'overlay')

    def _test_files(self, dirname, filename):
        path = os.path.join(helper.INPUT_PATH, dirname)
        with open(os.path.join(path, filename), 'rb') as fp:
            img = Image.open(fp)
            img = prepare_image(img)
            self._process_variation(img, dirname, filename, self.CLIP, self.NOUPSCALE)
            self._process_variation(img, dirname, filename, self.CLIP, self.UPSCALE)
            self._process_variation(img, dirname, filename, self.NOCLIP, self.NOUPSCALE)
            self._process_variation(img, dirname, filename, self.NOCLIP, self.UPSCALE)

    def test_jpeg(self, jpeg_image_filename):
        self._test_files('jpg', jpeg_image_filename)

    def test_png(self, png_image_filename):
        self._test_files('png', png_image_filename)

    def test_gif(self, gif_image_filename):
        self._test_files('gif', gif_image_filename)

    def test_webp(self, webp_image_filename):
        self._test_files('webp', webp_image_filename)


class TestExifOrientation:
    def test_variation_exif(self, exif_image_filename):
        variation = Variation(size=(1024, 768), clip=False, upscale=True,)
        path = os.path.join(helper.INPUT_PATH, 'exif')
        with open(os.path.join(path, exif_image_filename), 'rb') as fp:
            img = Image.open(fp)
            img = prepare_image(img)
            new_img = variation.process(img)

            output_path = os.path.join(helper.OUTPUT_PATH, 'exif', exif_image_filename)
            helper.ensure_folder(output_path)

            variation.save(new_img, output_path)

            # check output
            target_path = os.path.join(helper.TARGET_PATH, 'exif', exif_image_filename)
            assert helper.image_diff(output_path, target_path) is None


class TestFilters:
    def _test_filter(self, dirname, filename, postprocessors=()):
        variation = Variation(size=(0, 0), postprocessors=postprocessors)
        input_path = os.path.join(helper.INPUT_PATH, 'filters', filename)
        with open(input_path, 'rb') as fp:
            img = Image.open(fp)
            img = prepare_image(img)
            new_img = variation.process(img)

            output_path = os.path.join(helper.OUTPUT_PATH, 'filters', dirname, filename)
            helper.ensure_folder(output_path)

            variation.save(new_img, output_path)

            # check output
            target_path = os.path.join(helper.TARGET_PATH, 'filters', dirname, filename)
            assert helper.image_diff(output_path, target_path) is None

    def test_grayscale(self, filter_image_filename):
        self._test_filter('grayscale', filter_image_filename, [processors.Grayscale()])

    def test_posterize(self, filter_image_filename):
        self._test_filter(
            'posterize',
            filter_image_filename,
            [processors.MakeOpaque(), processors.Posterize(4)],
        )

    def test_solarize(self, filter_image_filename):
        self._test_filter(
            'solarize',
            filter_image_filename,
            [processors.MakeOpaque(), processors.Solarize()],
        )

    def test_blur(self, filter_image_filename):
        self._test_filter('blur', filter_image_filename, [processors.Blur()])

    def test_sharpen(self, filter_image_filename):
        self._test_filter('sharpen', filter_image_filename, [processors.Sharpen()])

    def test_smooth(self, filter_image_filename):
        self._test_filter('smooth', filter_image_filename, [processors.Smooth()])

    def test_edge_enchance(self, filter_image_filename):
        self._test_filter(
            'edge_enchance', filter_image_filename, [processors.EdgeEnhance()]
        )

    def test_unsharp_mask(self, filter_image_filename):
        self._test_filter(
            'unsharp_mask', filter_image_filename, [processors.UnsharpMask()]
        )

    def test_box_blur(self, filter_image_filename):
        self._test_filter('box_blur', filter_image_filename, [processors.BoxBlur(10)])

    def test_gaussian_blur(self, filter_image_filename):
        self._test_filter(
            'gaussian_blur', filter_image_filename, [processors.GaussianBlur(10)]
        )

    def test_stack_blur(self, filter_image_filename):
        if processors.STACK_BLUR_SUPPORT:
            self._test_filter(
                'stack_blur', filter_image_filename, [processors.StackBlur(10)]
            )

    def test_custom(self, filter_image_filename):
        if not processors.STACK_BLUR_SUPPORT:
            return

        variation = Variation(
            size=(120, 80),
            face_detection=True,
            format='webp',
            webp=dict(quality=0,),
            preprocessors=[processors.MakeOpaque('#FFFF00')],
            postprocessors=[processors.StackBlur(8)],
        )
        input_path = os.path.join(helper.INPUT_PATH, 'filters', filter_image_filename)
        with open(input_path, 'rb') as fp:
            img = Image.open(fp)
            img = prepare_image(img)
            new_img = variation.process(img)

            output_path = os.path.join(
                helper.OUTPUT_PATH, 'filters/custom', filter_image_filename
            )
            output_path = variation.replace_extension(output_path)
            helper.ensure_folder(output_path)

            variation.save(new_img, output_path)

            # check output
            target_path = replace_extension(
                os.path.join(
                    helper.TARGET_PATH, 'filters/custom', filter_image_filename
                ),
                'webp',
            )
            helper.ensure_folder(target_path)
            assert helper.image_diff(output_path, target_path) is None
