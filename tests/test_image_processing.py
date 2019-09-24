import os
import unittest
from pilkit.lib import Image
from variations import processors
from variations.variation import Variation
from variations.utils import prepare_image, replace_extension
from . import helper


class TestVariationProcess(unittest.TestCase):
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
            }
        }
    }

    def _process_variation(self, img, dirname, filename, clip, upscale):
        source_size = img.size
        fileroot, ext = os.path.splitext(filename)

        def process(variation, folder):
            output_dir = os.path.join(helper.OUTPUT_PATH, dirname, folder)
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)

            with self.subTest(output_filename):
                self.assertEqual(variation.get_output_size(source_size), canvas)

                new_img = variation.process(img)
                self.assertEqual(new_img.size, canvas)

                output_path = os.path.join(output_dir, output_filename)
                variation.save(new_img, output_path)

                # check output
                result_path = os.path.join(helper.OUTPUT_PATH, dirname, folder, output_filename)
                target_path = os.path.join(helper.TARGET_PATH, dirname, folder, output_filename)
                self.assertIsNone(helper.image_diff(result_path, target_path))

        for size, canvas in self.SIZE_MAP[clip][upscale].items():
            filename_params = [
                fileroot,
                'x'.join(map(str, size)),
                'noclip' if not clip else '',
                'upscale' if upscale else ''
            ]
            output_filename = ','.join(p for p in filename_params if p) + ext

            plain_variation = Variation(
                size=size,
                clip=clip,
                upscale=upscale,
            )
            overlay_variation = plain_variation.copy()
            overlay_variation.postprocessors.append(processors.ColorOverlay('#0000FF', 0.10))

            process(plain_variation, 'plain')
            process(overlay_variation, 'overlay')

    def _test_format(self, dirname):
        path = os.path.join(helper.INPUT_PATH, dirname)
        for filename in os.listdir(path):
            with open(os.path.join(path, filename), 'rb') as fp:
                img = Image.open(fp)
                img = prepare_image(img)
                self._process_variation(img, dirname, filename, self.CLIP, self.NOUPSCALE)
                self._process_variation(img, dirname, filename, self.CLIP, self.UPSCALE)
                self._process_variation(img, dirname, filename, self.NOCLIP, self.NOUPSCALE)
                self._process_variation(img, dirname, filename, self.NOCLIP, self.UPSCALE)

    def test_jpeg(self):
        self._test_format('jpg')

    def test_png(self):
        self._test_format('png')

    def test_gif(self):
        self._test_format('gif')

    def test_webp(self):
        self._test_format('webp')


class TestExifOrientation(unittest.TestCase):
    def test_variation_exif(self):
        path = os.path.join(helper.INPUT_PATH, 'exif')
        for filename in os.listdir(path):
            variation = Variation(
                size=(1024, 768),
                clip=False,
                upscale=True,
            )
            with open(os.path.join(path, filename), 'rb') as fp:
                img = Image.open(fp)
                img = prepare_image(img)
                new_img = variation.process(img)

                output_path = os.path.join(helper.OUTPUT_PATH, 'exif')
                if not os.path.isdir(output_path):
                    os.makedirs(output_path)

                variation.save(new_img, os.path.join(output_path, filename))

                # check output
                with self.subTest(filename):
                    result_path = os.path.join(helper.OUTPUT_PATH, 'exif', filename)
                    target_path = os.path.join(helper.TARGET_PATH, 'exif', filename)
                    self.assertIsNone(helper.image_diff(result_path, target_path))


class TestFilters(unittest.TestCase):
    def _test_filter(self, folder, postprocessors=()):
        path = os.path.join(helper.INPUT_PATH, 'filters')
        for filename in sorted(os.listdir(path)):
            variation = Variation(
                size=(0, 0),
                postprocessors=postprocessors
            )
            with open(os.path.join(path, filename), 'rb') as fp:
                img = Image.open(fp)
                img = prepare_image(img)
                new_img = variation.process(img)

                output_path = os.path.join(helper.OUTPUT_PATH, 'filters', folder)
                if not os.path.isdir(output_path):
                    os.makedirs(output_path)

                variation.save(new_img, os.path.join(output_path, filename))

            # check output
            with self.subTest(filename):
                result_path = os.path.join(helper.OUTPUT_PATH, 'filters', folder, filename)
                target_path = os.path.join(helper.TARGET_PATH, 'filters', folder, filename)
                self.assertIsNone(helper.image_diff(result_path, target_path))

    def test_grayscale(self):
        self._test_filter('grayscale', [
            processors.Grayscale()
        ])

    def test_posterize(self):
        self._test_filter('posterize', [
            processors.MakeOpaque(),
            processors.Posterize(4),
        ])

    def test_solarize(self):
        self._test_filter('solarize', [
            processors.MakeOpaque(),
            processors.Solarize(),
        ])

    def test_blur(self):
        self._test_filter('blur', [
            processors.Blur(),
        ])

    def test_sharpen(self):
        self._test_filter('sharpen', [
            processors.Sharpen(),
        ])

    def test_smooth(self):
        self._test_filter('smooth', [
            processors.Smooth(),
        ])

    def test_edge_enchance(self):
        self._test_filter('edge_enchance', [
            processors.EdgeEnhance(),
        ])

    def test_unsharp_mask(self):
        self._test_filter('unsharp_mask', [
            processors.UnsharpMask(),
        ])

    def test_box_blur(self):
        self._test_filter('box_blur', [
            processors.BoxBlur(10),
        ])

    def test_gaussian_blur(self):
        self._test_filter('gaussian_blur', [
            processors.GaussianBlur(10),
        ])

    def test_stack_blur(self):
        if processors.STACK_BLUR_SUPPORT:
            self._test_filter('stack_blur', [
                processors.StackBlur(10),
            ])

    def test_custom(self):
        if not processors.STACK_BLUR_SUPPORT:
            return

        path = os.path.join(helper.INPUT_PATH, 'filters')
        for filename in sorted(os.listdir(path)):
            variation = Variation(
                size=(120, 80),
                face_detection=True,
                format='webp',
                webp=dict(
                    quality=0,
                ),
                preprocessors=[
                    processors.MakeOpaque(),
                ],
                postprocessors=[
                    processors.StackBlur(8),
                ]
            )
            with open(os.path.join(path, filename), 'rb') as fp:
                img = Image.open(fp)
                img = prepare_image(img)
                new_img = variation.process(img)

                output_path = os.path.join(helper.OUTPUT_PATH, 'filters/custom')
                if not os.path.isdir(output_path):
                    os.makedirs(output_path)

                output_filename = variation.replace_extension(os.path.join(output_path, filename))
                variation.save(new_img, output_filename)

            # check output
            with self.subTest(filename):
                result_path = replace_extension(os.path.join(helper.OUTPUT_PATH, 'filters/custom', filename), 'webp')
                target_path = replace_extension(os.path.join(helper.TARGET_PATH, 'filters/custom', filename), 'webp')
                self.assertIsNone(helper.image_diff(result_path, target_path))
