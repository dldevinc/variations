import logging
from pilkit.lib import Image, ImageColor
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


class FaceDetectionResizeToFill(ResizeToFill):
    """
    Добавление функции определения лиц
    """
    def __init__(self, *args, face_detection=False, **kwargs):
        self.face_detection = face_detection
        super().__init__(*args, **kwargs)

    def _get_new_anchor(self, img, faces_box):
        original_width, original_height = img.size
        ratio = max(float(self.width) / original_width,
                    float(self.height) / original_height)
        new_width, new_height = (int(round(original_width * ratio)),
                                 int(round(original_height * ratio)))

        top, right, bottom, left = faces_box
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
        if self.face_detection is False:
            return super().process(img)

        try:
            import numpy
            import face_recognition
        except ImportError:
            logging.warning('face_recognition not installed')
            return super().process(img)

        original_anchor = self.anchor
        if img.mode not in ('RGB', 'L'):
            clone = img.convert('RGB')
            image_data = numpy.array(clone)
        else:
            image_data = numpy.array(img)

        face_locations = face_recognition.face_locations(image_data, number_of_times_to_upsample=0)
        if not face_locations:
            return super().process(img)

        faces_box = list(face_locations[0])
        for face_location in face_locations[1:]:
            top, right, bottom, left = face_location
            faces_box[0] = min(faces_box[0], top)
            faces_box[1] = max(faces_box[1], right)
            faces_box[2] = max(faces_box[2], bottom)
            faces_box[3] = min(faces_box[3], left)

        # overwrite anchor
        self.anchor = self._get_new_anchor(img, faces_box)
        result = super().process(img)
        self.anchor = original_anchor
        return result
