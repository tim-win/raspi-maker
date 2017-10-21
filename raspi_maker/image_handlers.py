"""Got to keep your image up!"""
import os

IMAGE_NAME = '2016-11-25-raspbian-jessie.img'
IMAGE_NAME = '2017-08-16-raspbian-stretch.img'
PATH = '~/Documents/'


def check_image():
    full_path = os.path.expanduser(os.path.join(PATH, IMAGE_NAME))
    if os.path.exists(full_path):
        return full_path
    return False
