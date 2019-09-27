# variations
A simple interface that allows to process images.

## Compatibility
* `python` >= 3.4

## Installation
1. Install [Pillow](http://pypi.python.org/pypi/Pillow)

    ``pip install Pillow``
2. Install [pilkit](https://github.com/matthewwithanm/pilkit)

    ``pip install pilkit``
3. Run `pip install variations`

4. (**optional**) If you want to use [StackBlur](https://github.com/dldevinc/pillow-stackblur)
    
    ``pip install pillow-stackblur``

5. (**optional**) If you want to use [Face Detection](https://github.com/ageitgey/face_recognition)

    ``pip install face_recognition``

## Usage
```python
    from PIL import Image
    from variations import processors
    from variations.variation import Variation
    from variations.utils import prepare_image

    variation = Variation(
        size=(400, 0),
        max_height=800,
        clip=False,
        upscale=False,
        anchor=processors.Anchor.TOP_LEFT,
        jpeg=dict(
            quality=92,
        ),
        webp=dict(
            lossless=True,
            quality=90,
        ),
        postprocessors=[
            processors.ColorOverlay('#FF0000', overlay_opacity=0.25),
        ],
    )
    
    img = Image.open('source.jpg')
    img = prepare_image(img, draft_size=variation.get_output_size(img.size))
    new_img = variation.process(img)
    dest_path = variation.replace_extension('dest.jpg')
    variation.save(new_img, dest_path)
```

## Options
|                    | Type                 | Examples                                                  | Description                                                                                                                                              |
|--------------------|----------------------|-----------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **size**           | tuple<br>list        | `(640, 480)`<br>`(640, 0)`<br>`(0, 0)`                          | The **canvas** size of image. If you set the width or height to zero,  the corresponding value will be automatically adjusted based on  the aspect ratio |
| **max_width**      | int                  | `640`                                                     | It specifies the maximim width in pixels.This option have meaning only when corresponding value in `size` is zero                                        |
| **max_height**     | int                  | `480`                                                     | It specifies the maximim height in pixels.This option have meaning only when corresponding value in `size` is zero                                       |
| **clip**           | bool                 |                                                           | When set to `True`, the image can be cropped when filling the canvas.                                                                                    |
| **upscale**        | bool                 |                                                           | When set to `True`, the image can be upscaled when filling the canvas.                                                                                   |
| **anchor**         | str<br>tuple<br>list | `'tr'` (top right)<br>`'c'` (center)<br>`(1, 1)` (bottom right) | Defines the anchor point.                                                                                                                                |
| **face_detection** | bool                 |                                                           | Use a face detection system to find anchor point. You must install [facial recognition api](https://github.com/ageitgey/face_recognition) to use this.   |
| **format**         | str                  | `'JPEG'` `'png'` `'WebM'`                                 | Enforce output image format. Defaults to `'AUTO'`, which means keep input format.                                                                        |
| **preprocessors**  | list                 | `[processors.Crop(width=200, height=120, x=50, y=50)]`      | [PilKit](https://github.com/matthewwithanm/pilkit) processors are invoked before the main processing stage                                               |
| **postprocessors** | list                 | `[processors.ColorOverlay('#0000FF', 0.10)]`                | [PilKit](https://github.com/matthewwithanm/pilkit) processors are invoked after the main processing stage                                                |

## Additional options

It is possible to pass additional [options](https://pillow.readthedocs.io/en/latest/handbook/image-file-formats.html)
to `save()` method.

```python
# Defaults
Variation(
    # ...
    jpeg=dict(
        quality=85,
        progressive=True,
    ),
    webp=dict(
        autoconvert=False,
        quality=85,
    ),
    tiff=dict(
        compression='jpeg',
    )
)
```
