"""Raspi maker - make nice sd and thumb drive for raspi provisioning."""
from .actions import clear_device
from .actions import copy_boot_partition
from .actions import expand_second_partition
from .actions import flash_image
from .actions import polish_drive
from .actions import update_sdcard_boot_commands
from .cli_helpers import devices_prompt
from .cli_helpers import print_devices
from .device import Device
from .device import get_devices
from .errors import check_for_root_device
from .image_handlers import check_image


def main(args):
    devices = dict((dev, Device(dev)) for dev in get_devices())

    print_devices(devices)
    
    sd_card, thumb_drive = devices_prompt(devices)

    check_for_root_device(sd_card.blk_id, thumb_drive.blk_id)

    print 'Checking for local image'
    disk_image = check_image()
    if disk_image:
        print 'Image found: {0}'.format(disk_image)
    else:
        print 'Fetching Image Remotely'
        raise NotImplemented('I didnt write this yet...')

    print 'Clearing SD Card: {0}'.format(str(sd_card))
    clear_device(sd_card)

    print 'Clearing Thumb Drive: {0}'.format(str(thumb_drive))
    clear_device(thumb_drive)

    print 'Flashing the Image to the thumb_drive.'
    flash_image(disk_image, thumb_drive)

    print 'Creating a boot partition on the sd card'
    copy_boot_partition(source=thumb_drive, target=sd_card)

    print 'Modifying target boot dir on SD Card'
    update_sdcard_boot_commands(sd_card)

    print 'Expanding thumb drive to full thumb size.'
    expand_second_partition(thumb_drive)

    print 'Polishing thumb drive for final ready to go status.'
    polish_drive(thumb_drive)

    print 'Your shit is done!'
    print 'Plug it into a pi and you\'re ready to rock.'
    return 0
