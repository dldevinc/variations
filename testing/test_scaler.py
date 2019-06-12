import unittest
from variations.scaler import Scaler


class TestScaler(unittest.TestCase):
    def test_scaler_noupscale(self):
        s = Scaler(300, 600, upscale=False)
        s.set_width(200)
        self.assertEqual(s.width, 200)
        self.assertEqual(s.height, 400)

        s.set_width(400)
        self.assertEqual(s.width, 300)
        self.assertEqual(s.height, 600)

        s.set_height(300)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 300)

        s.set_height(800)
        self.assertEqual(s.width, 300)
        self.assertEqual(s.height, 600)

        s = Scaler(300, 600, upscale=False)
        s.set_height(500)
        self.assertEqual(s.width, 250)
        self.assertEqual(s.height, 500)

        s = Scaler(300, 600, upscale=False)
        s.set_height(800)
        self.assertEqual(s.width, 300)
        self.assertEqual(s.height, 600)

    def test_scaler_upscale(self):
        s = Scaler(300, 600, upscale=True)
        s.set_width(200)
        self.assertEqual(s.width, 200)
        self.assertEqual(s.height, 400)

        s.set_width(400)
        self.assertEqual(s.width, 400)
        self.assertEqual(s.height, 800)

        s.set_height(300)
        self.assertEqual(s.width, 150)
        self.assertEqual(s.height, 300)

        s.set_height(800)
        self.assertEqual(s.width, 400)
        self.assertEqual(s.height, 800)

        s = Scaler(300, 600, upscale=True)
        s.set_height(500)
        self.assertEqual(s.width, 250)
        self.assertEqual(s.height, 500)

        s = Scaler(300, 600, upscale=True)
        s.set_height(800)
        self.assertEqual(s.width, 400)
        self.assertEqual(s.height, 800)
