import logging
from pilkit.lib import Image, ImageColor, ImageDraw
from pilkit.processors import ResizeToFill


class ColorOverlay(object):
    """
    Аналогичен pilkit-процессору ColorOverlay, но корректно работает с RGBA.
    """
    def __init__(self, color, overlay_opacity=0.5):
        self.color = color
        self.overlay_opacity = overlay_opacity

    def process(self, img):
        if isinstance(self.color, str):
            color = ImageColor.getrgb(self.color)
        else:
            color = self.color
        if len(color) == 3:
            color += (int(self.overlay_opacity * 255),)

        original = img
        overlay = Image.new('RGBA', original.size, color)
        img = Image.alpha_composite(original, overlay)
        return img


class ROIDetectionResizeToFill(ResizeToFill):
    """
    Добавление функции определения лиц
    """
    def __init__(self, *args, face_detection=False, **kwargs):
        self.face_detection = face_detection
        super().__init__(*args, **kwargs)

    def _detect_faces(self, img):
        try:
            import numpy
            import face_recognition
        except ImportError:
            logging.warning('Cannot use face detection because face_recognizer is not installed.')
            return

        if img.mode not in ('RGB', 'L'):
            clone = img.convert('RGB')
            image_data = numpy.array(clone)
        else:
            image_data = numpy.array(img)

        faces = face_recognition.face_locations(image_data, number_of_times_to_upsample=0)
        if not faces:
            return

        rect = list(faces[0])
        for face in faces[1:]:
            top, right, bottom, left = face
            rect[0] = min(rect[0], top)
            rect[1] = max(rect[1], right)
            rect[2] = max(rect[2], bottom)
            rect[3] = min(rect[3], left)
        return rect[3], rect[0], rect[1], rect[2]   # left, top, right, bottom

    def _get_new_anchor(self, img, roi_rect):
        original_width, original_height = img.size
        ratio = max(float(self.width) / original_width,
                    float(self.height) / original_height)
        new_width, new_height = (int(round(original_width * ratio)),
                                 int(round(original_height * ratio)))

        left, top, right, bottom = roi_rect
        x = (left + right) / 2 * ratio
        y = (top + bottom) / 2 * ratio
        anchor_x = 0
        if new_width != self.width:
            anchor_x = max(0, min((x - self.width / 2) / (new_width - self.width), 1))
        anchor_y = 0
        if new_height != self.height:
            anchor_y = max(0, min((y - self.height / 2) / (new_height - self.height), 1))
        return anchor_x, anchor_y

    def process(self, img):
        rect = None
        if self.face_detection:
            rect = self._detect_faces(img)

        if rect is None:
            return super().process(img)

        # draw = ImageDraw.Draw(img)
        # draw.rectangle(rect, outline='#FFFF00')

        # overwrite anchor
        original_anchor = self.anchor
        self.anchor = self._get_new_anchor(img, rect)
        result = super().process(img)
        self.anchor = original_anchor
        return result
