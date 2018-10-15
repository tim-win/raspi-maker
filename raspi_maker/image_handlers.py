"""Got to keep your image up!"""
import os

IMAGE_NAME = '2016-11-25-raspbian-jessie.img'
IMAGE_NAME = '2017-08-16-raspbian-stretch.img'
IMAGE_NAME = '2017-09-07-raspbian-stretch.img'
IMAGE_NAME = '2018-10-09-raspbian-stretch-lite.img'
# IMAGE_NAME = '2017-06-21-octopi-jessie-lite-0.14.0.img'
# IMAGE_NAME = 'retropie-4.3-rpi2_rpi3.img'
PATH = '~/Documents/'


def check_image():
    full_path = os.path.expanduser(os.path.join(PATH, IMAGE_NAME))
    if os.path.exists(full_path):
        return full_path
    return False
