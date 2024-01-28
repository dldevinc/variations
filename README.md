# variations

`variations` is a Python library for image processing that provides a Variation class 
to handle various image transformation operations. It is built on top of the popular 
Python Imaging Library (PIL) and aims to simplify the process of applying variations 
to images.

A simple interface that allows processing of images.

[![PyPI](https://img.shields.io/pypi/v/variations.svg)](https://pypi.org/project/variations/)
[![Build Status](https://github.com/dldevinc/variations/actions/workflows/tests.yml/badge.svg)](https://github.com/dldevinc/variations)
[![Software license](https://img.shields.io/pypi/l/variations.svg)](https://pypi.org/project/variations/)

## Compatibility

-   `python` >= 3.9

## Installation

1. Run `pip install variations`

2. (**optional**) If you want to use [StackBlur](https://github.com/dldevinc/pillow-stackblur):

    `pip install pillow-stackblur`

3. (**optional**) If you want to use [Face Detection](https://github.com/ageitgey/face_recognition):

    `pip install face_recognition`

## Getting Started

### Basic Usage

To get started with variations, follow these simple steps:

1. Import the necessary modules:

   ```python
   from PIL import Image
   from variations import Variation, processors
   ```

1. Create a `Variation` instance with your desired parameters:

   ```python
   # Example Variation with specified parameters
   variation = Variation(
       size=(800, 600),
       mode=Variation.Mode.FIT,
       background="#FFFFFF",
       preprocessors=[
           processors.Grayscale()
       ],
   )
   ```

1. Open an image using PIL:

   ```python
   img = Image.open("path/to/your/image.jpg")
   ```

1. Process the image using the created variation:

   ```python
   processed_image = variation.process(img)
   ```

1. Save the processed image:

   ```python
   variation.save(processed_image, "path/to/your/destination/image.jpg")
   ```

### Example

Here's a complete example:

```python
from PIL import Image
from variations import Variation, processors

# Create a variation with specific parameters
variation = Variation(
    size=(800, 600),
    mode=Variation.Mode.FIT,
    background="#FFFFFF",
    preprocessors=[
        processors.Grayscale()
    ],
    jpeg=dict(
       quality=80,
       progressive=True,
    )
)

img = Image.open("source.jpg")

# Process an image using the variation
processed_image = variation.process(img)

# Save the processed image to a destination file
variation.save(processed_image, "dest.jpg")
```

## Parameters

### `size` (required)
* Type: tuple of two non-negative integers
* Description: Specifies the target size of the processed image in the format `(width, height)`.

### `mode`
* Type: `Variation.Mode`
* Default: `Variation.Mode.FILL`
* Description: Specifies the processing mode. Available modes are `FILL`, `FIT`, `CROP`, and `NONE`.

### `gravity`
* Type: `Variation.Gravity`
* Default: `Variation.Gravity.CENTER`
* Description: Specifies the gravity or anchor point for cropping or fitting operations.

### `upscale`
* Type: `bool`
* Default: `False`
* Description: Enables or disables upscaling of images.

### `background`
* Type: `str` or `Collection[int]`
* Default: `None`
* Description: Specifies the background color. Used when the mode is set to `FIT`.

### `format`
* Type: `str` or `None`
* Default: `None`
* Description: Specifies the output format of the processed image.

### `preprocessors`
* Type: `Iterable[ProcessorProtocol]` or `None`
* Default: `None`
* Description: A list of PILKit processors to apply before the main processing step.

### `postprocessors`
* Type: `Iterable[ProcessorProtocol]` or `None`
* Default: `None`
* Description: A list of PILKit processors to apply after the main processing step.

### Other Parameters
Additional parameters specific to particular image formats (e.g., `jpeg`, `webp`) can 
be provided as nested dictionaries. These parameters will be passed to the corresponding 
image processing backend and ultimately to the `Image.save()` method. For a list 
of available options for each format, refer to the 
[Pillow documentation](https://pillow.readthedocs.io/en/latest/handbook/image-file-formats.html).


## Migration Guide

The `variations` library has gone through some changes to make it easier to understand 
and use. This guide will help you update your code to the latest version.

### Handling Images with Both Dimensions Defined and Clipping Enabled

In the old code, if both dimensions were defined and `clip=True`, the library assumed 
`FILL` mode, whether `upscale` was `True` or `False`. In the new version, you should 
explicitly set the mode parameter.

Old code:
```python
Variation(
   size=(800, 600),
   clip=True    # can be omitted as it is the default value
)
```

New code:
```python
Variation(
   size=(800, 600),
   mode=Variation.Mode.FILL,    # can be omitted as it is the default value
)
```

### Handling Single-Dimension Images with Clipping and No Upscaling

In the old code, if only one dimension was set, `clip=True`, and `upscale` was `False`, 
the library assumed `FILL` mode. In the new version, you should explicitly set the mode 
parameter.

Old code:
```python
Variation(
   size=(800, 0),
   clip=True,       # can be omitted as it is the default value
   upscale=False    # can be omitted as it is the default value
)
```

New code:
```python
Variation(
   size=(800, 0),
   mode=Variation.Mode.FILL,    # can be omitted as it is the default value
   upscale=False                # can be omitted as it is the default value
)
```

### Handling Single-Dimension Images with Clipping, Upscaling, and Width Comparison

In the previous implementation, when dealing with a single-dimension image, `clip=True`, 
and `upscale=True`, the mode was determined based on a comparison between the specified 
variation dimension and the actual image dimension. If the variation dimension was greater, 
the `mode` should be `FILL`; otherwise, it should be `CROP`.

Old code:
```python
Variation(
   size=(800, 0),
   clip=True,       # can be omitted as it is the default value
   upscale=True
)
```

New code:
```python
Variation(
   size=(800, 0),
   mode=Variation.Mode.FILL,    # can be omitted as it is the default value
   upscale=True
)
```

If the specified variation dimension was smaller:

Old code:
```python
Variation(
   size=(200, 0),
   clip=True,       # can be omitted as it is the default value
   upscale=True
)
```

New code:
```python
Variation(
   size=(200, 0),
   mode=Variation.Mode.CROP
)
```

### Handling Images with Clipping Disabled

In the old code, if `clip` was set to `False`, the `mode` should be `FIT` with a background 
for any `upscale` value.

Old code:
```python
Variation(
   size=(800, 600),
   clip=False
)
```

New code:
```python
Variation(
   size=(800, 600),
   mode=Variation.Mode.FIT,
   background=(255, 255, 255, 0),
)
```

### Handling Images with Clipping Disabled and Max Width or Max Height Set

In the old code, if `clip` was `False`, and `max_width` or `max_height` was set, 
the `mode` should be `FIT` without a background.

Old code:
```python
Variation(
   size=(0, 0),
   clip=False,
   max_width=800,
   max_height=600
)
```

New code:
```python
Variation(
   size=(200, 0),
   mode=Variation.Mode.FIT
)
```

Additionally, instead of using `anchor`, the parameter `gravity` should be employed. 
For cases previously using `face_detection`, use `gravity=Variation.Gravity.AUTO` 
for the same effect. These changes enhance clarity and explicitly define the behavior, 
making it easier to understand and use.
