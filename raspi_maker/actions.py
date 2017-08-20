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


@PromptOnError
def copy_boot_partition(source, target):
    """Copy the boot partition, including flags and file type.

    SideEffects
    -----------
    Creates a partition on target device, with:
        label: boot
        size: equivalent to source device's partition 1
        
    """
    boot_source = source.partition_specs(1)

    mkfs_command = [
        'sudo',
        'parted',
        target.path,
        'mkpart',
        'primary',
        'fat16',
        boot_souce['Start'],
        boot_souce['End']
    ]

    # Create a placeholder partition
    interactive_console(mkfs_command)

    partition = target.partitions[0]

    e2label_command = [
        'sudo',
        'e2label',
        'boot'
    ]

    print 'Labelling filesystem.'
    interactive_console(e2label_command)
    copy_command = 'sudo dd if={source} | pv | sudo dd of={target}'

    populated_cmd = cmd.format(
        source=source.path,
        target=target.path)

    output = check_output(populated_cmd, shell=True)    
    print output