import os

from . import helper


def pytest_generate_tests(metafunc):
    if "exif_image_filename" in metafunc.fixturenames:
        input_folder = os.path.join(helper.INPUT_PATH, 'exif')
        files = sorted(os.listdir(input_folder))
        metafunc.parametrize("exif_image_filename", files)
    elif "face_image_filename" in metafunc.fixturenames:
        input_folder = os.path.join(helper.INPUT_PATH, 'faces')
        files = sorted(os.listdir(input_folder))
        metafunc.parametrize("face_image_filename", files)
    elif "filter_image_filename" in metafunc.fixturenames:
        input_folder = os.path.join(helper.INPUT_PATH, 'filters')
        files = sorted(os.listdir(input_folder))
        metafunc.parametrize("filter_image_filename", files)
    elif "jpeg_image_filename" in metafunc.fixturenames:
        input_folder = os.path.join(helper.INPUT_PATH, 'jpg')
        files = sorted(os.listdir(input_folder))
        metafunc.parametrize("jpeg_image_filename", files)
    elif "png_image_filename" in metafunc.fixturenames:
        input_folder = os.path.join(helper.INPUT_PATH, 'png')
        files = sorted(os.listdir(input_folder))
        metafunc.parametrize("png_image_filename", files)
    elif "gif_image_filename" in metafunc.fixturenames:
        input_folder = os.path.join(helper.INPUT_PATH, 'gif')
        files = sorted(os.listdir(input_folder))
        metafunc.parametrize("gif_image_filename", files)
    elif "webp_image_filename" in metafunc.fixturenames:
        input_folder = os.path.join(helper.INPUT_PATH, 'webp')
        files = sorted(os.listdir(input_folder))
        metafunc.parametrize("webp_image_filename", files)
