from fractions import Fraction

from variations.scaler import Scaler


class TestScaler:
    def test_scaler_str(self):
        s = Scaler(300, 600)
        assert str(s) == "300x600"

    def test_scaler_repr(self):
        s = Scaler(300, 600)
        assert repr(s) == "Scaler(300, 600)"

    def test_scaler_ratio(self):
        assert Scaler(300, 600).ratio == 0.5
        assert Scaler(300, 100).ratio == 3
        assert Scaler(100, 300).ratio == Fraction(1, 3)

        s = Scaler(300, 600, upscale=False)
        s.set_width(200)
        assert s.width == 200
        assert s.height == 400
        assert s.ratio == 0.5

    def test_scaler_noupscale(self):
        s = Scaler(300, 600, upscale=False)
        s.set_width(200)
        assert s.width == 200
        assert s.height == 400

        s.set_width(400)
        assert s.width == 300
        assert s.height == 600

        s.set_height(300)
        assert s.width == 150
        assert s.height == 300

        s.set_height(800)
        assert s.width == 300
        assert s.height == 600

        s = Scaler(300, 600, upscale=False)
        s.set_height(500)
        assert s.width == 250
        assert s.height == 500

        s = Scaler(300, 600, upscale=False)
        s.set_height(800)
        assert s.width == 300
        assert s.height == 600

    def test_scaler_upscale(self):
        s = Scaler(300, 600, upscale=True)
        s.set_width(200)
        assert s.width == 200
        assert s.height == 400

        s.set_width(400)
        assert s.width == 400
        assert s.height == 800

        s.set_height(300)
        assert s.width == 150
        assert s.height == 300

        s.set_height(800)
        assert s.width == 400
        assert s.height == 800

        s = Scaler(300, 600, upscale=True)
        s.set_height(500)
        assert s.width == 250
        assert s.height == 500

        s = Scaler(300, 600, upscale=True)
        s.set_height(800)
        assert s.width == 400
        assert s.height == 800
