import unittest
from pilkit import processors
from variations import processors
from variations.variation import Variation


class TestVariationInit(unittest.TestCase):
    def test_variation_size(self):
        type_error_sizes = [
            None,
            '65',
            {100, 200},
            {100: 10, 200: 20},
        ]

        value_error_sizes = [
            (),
            [],
            (100, ),
            [10, -1.6],
            (-100, -200),
            ('-100', '200'),
            [100, 200, 300],
        ]

        pass_values = [
            (0, 0),
            (100, 200),
            ('100', '200'),
            [100, 200],
            ['100', '200'],
            (100.6, 200.7),
            (x for x in [100, 200]),
            [x for x in [100, 200]],
        ]

        for size in type_error_sizes:
            with self.assertRaises(TypeError):
                Variation(size)

        for size in value_error_sizes:
            with self.assertRaises(ValueError):
                Variation(size)

        for size in pass_values:
            Variation(size)

        v = Variation(['123', 456.6])
        self.assertEqual(v.width, 123)
        self.assertEqual(v.height, 456)

    def test_variation_limits(self):
        type_error_limits = [
            {'max_width': 'a'},
            {'max_width': [0, 200]},
            {'max_height': 'b'},
            {'max_height': [10, 50]},
        ]

        value_error_limits = [
            {'max_width': '-100'},
            {'max_height': '-100'},
        ]

        pass_values = [
            {'max_width': 100},
            {'max_height': 200},
            {'max_width': '0', 'max_height': 0},
            {'max_width': '100', 'max_height': 200},
        ]

        for limits in type_error_limits:
            with self.assertRaises(TypeError):
                Variation([100, 100], **limits)

        for limits in value_error_limits:
            with self.assertRaises(ValueError):
                Variation([100, 100], **limits)

        for limits in pass_values:
            Variation([0, 0], clip=False, **limits)

        v = Variation([0, 0], clip=False, max_width=350, max_height=450.75)
        self.assertEqual(v.max_width, 350)
        self.assertEqual(v.max_height, 450)

    def test_variation_copy(self):
        v = Variation(
            size=[0, 0],
            clip=False,
            max_width=350,
            max_height=450.75,
            preprocessors=[
                processors.Crop(
                    width=200,
                    height=120,
                    x=50,
                    y=50
                )
            ],
            postprocessors=[
                processors.ColorOverlay('#0000FF', 0.10)
            ],
            extra=dict(
                key='SomeWhat',
                inner_list=[1, 2, 3]
            )
        )

        clone = v.copy()
        self.assertIsNot(clone, v)
        self.assertIsNot(clone.preprocessors, v.preprocessors)
        self.assertIsNot(clone.postprocessors, v.postprocessors)
        self.assertIsNot(clone.extra_context, v.extra_context)
        self.assertIsNot(
            clone.extra_context['extra']['inner_list'],
            v.extra_context['extra']['inner_list']
        )

    def test_variation_anchor(self):
        type_error_anchor = [
            1,
            {0.10, 0.14},
            'xxx',
            '0, 0',
        ]

        value_error_anchor = [
            (),
            [0, 0, 0],
            (0, 0, 0),
        ]

        pass_values = [
            'c',
            'tl',
            [0.12, '0.8'],
            (0, 0.15),
            ('1', '0.75'),
        ]

        for anchor in type_error_anchor:
            with self.assertRaises(TypeError):
                Variation([100, 100], anchor=anchor)

        for anchor in value_error_anchor:
            with self.assertRaises(ValueError):
                Variation([100, 100], anchor=anchor)

        for anchor in pass_values:
            Variation([100, 100], anchor=anchor)

        v = Variation([100, 200])
        self.assertEqual(v.anchor, (0.5, 0.5))

        v = Variation([100, 200], anchor='TL')
        self.assertEqual(v.anchor, (0, 0))

        v = Variation([100, 200], anchor=[0.1, 0.75])
        self.assertEqual(v.anchor, (0.1, 0.75))
