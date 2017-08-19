from .debugging import PromptOnError
from .console import console

from subprocess import check_output


@PromptOnError
def clear_device(device):
    """Run rm commands on all partitions on the device.

    To do this, we count the partitions, and delete them one by one.
    This is done by running:
        
        $ sudo parted <path_to_device> rm <partition_number>

    Where path_to_device is something like /dev/mmcblk0 and partition_number
    is a 1 indexed id for partitions.

    To get a list of partitions, you can also run:

        $ sudo parted /dev/mmcblk0 unit s print

    This will make it more clear what you're working with.

    Parameters
    ----------
    device : raspi-maker.device.Device instance

    Returns
    -------
    bool : True if successful

    Side Effects
    ------------
    Delete all the partitions on the target device.

    Raises
    ------
    Prompt on Error will catch exceptions, so this will drop into a prompt
    if it fails.
    """
    device.unmount_all()
    
    partitions = device.partitions

    for partitions in reversed(xrange(1,1+len(partitions))):
        print 'Deleting {0} partition #{1}'.format(device.path, partitions)
        console(['sudo', 'parted', device.path, 'rm', str(partitions)])

    return True


@PromptOnError
def flash_image(disk_image, device):
    """DD an image onto a device."""
    cmd = 'dd if={disk_image} | pv | sudo dd of={device_path}'

    populated_cmd = cmd.format(
        disk_image=disk_image,
        device_path=device.path)

    # why check output? because then you can do the cool
    # dd | pv | dd trick. '|pv|'' is awesome stdout.
    output = check_output(populated_cmd, shell=True)
    print output
