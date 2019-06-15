from pilkit.processors.base import *

__all__ = ['ProcessorPipeline', 'Adjust', 'Reflection', 'Transpose', 'Anchor', 'MakeOpaque']


class MakeOpaque(object):
    """
    Подобен pilkit-процессору MakeOpaque, но работает с изображениями в любых
    режимах, включая RGB, LA и P. Возвращает RGB-изображение, а не RGBA.
    NOTE: полностью игнорирует alpha-канал фонового цвета.
    """
    def __init__(self, background_color=(255, 255, 255)):
        if isinstance(background_color, str):
            background_color = ImageColor.getrgb(background_color)
        self.background_color = background_color[:3]

    def process(self, img):
        new_img = Image.new('RGB', img.size, self.background_color)
        if img.mode in ('P', 'LA'):
            img = img.convert('RGBA')
        if img.mode in ('1', 'L', 'RGBA'):
            new_img.paste(img, img)
        else:
            new_img.paste(img)
        return new_img
