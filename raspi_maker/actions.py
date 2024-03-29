import os
from tempfile import mkdtemp
from subprocess import check_output

from .debugging import PromptOnError
from .console import console
from .console import interactive_console


def _delete_partition(device, number):
    print('Deleting {0} partition #{1}'.format(device.path, number))
    console(['sudo', 'parted', device.path, 'rm', str(number)])


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

    partitions = device.partitions()

    for partition in range(1, 1+len(partitions)):
        _delete_partition(device, partition)

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
    print(output)


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
        boot_source['Start'],
        boot_source['End']
    ]

    # Create a placeholder partition
    interactive_console(mkfs_command)

    partition = target.partitions()[0]

    copy_command = 'sudo dd if={source} | pv | sudo dd of={target}'

    populated_cmd = copy_command.format(
        source=source.partitions(full_paths=True)[0],
        target=target.partitions(full_paths=True)[0])

    print('Copying the boot fs over.')
    output = check_output(populated_cmd, shell=True)
    print(output)

    e2label_command = [
        'sudo',
        'e2label',
        target.partitions(full_paths=True)[0],
        'boot'
    ]

    print('Labeling filesystem.')
    interactive_console(e2label_command)


@PromptOnError
def update_sdcard_boot_commands(device):
    """Make the SD Card point to the thumb drive on boot."""
    mount_dir = mkdtemp()

    boot_partition = device.partitions(full_paths=True)[0]

    mount_command = ['sudo', 'mount', boot_partition, mount_dir]

    print(f'Mounting SD Card partition {boot_partition} to temp directory {mount_dir}')
    interactive_console(mount_command)

    # Note- this sed command is what the target mounts will look like
    # I'm not messing with the blk_ids of our devices as we know them
    # here.

    sed_command = [
        'sudo',
        'sed',
        '-i',
        '-E',
        's#root=[^ ]+#root=/dev/sda2#',
        os.path.join(mount_dir, 'cmdline.txt')]
    console(sed_command)
    sed_command = [
        'sudo',
        'sed',
        '-i',
        's# init=/usr/lib/raspi-config/init_resize.sh##',
        os.path.join(mount_dir, 'cmdline.txt')]

    print('Modifying init command line')
    console(sed_command)

    print('Successfully modified! Unmounting.')
    umount_command = ['sudo', 'umount', mount_dir]
    interactive_console(umount_command)

    print('Cleaning up mounted dir')
    os.rmdir(mount_dir)


def expand_second_partition(device):
    """Take the second partition from the thumb drive and expand it."""

    print('Deleting the original boot partition from the thumb drive')
    _delete_partition(device, 1)

    print('Expanding the partition. Resizing isn\'t worth it. Or obvious to do.')
    resize_command = ['sudo', 'parted', device.path, 'resizepart', '2', '"-1s"']
    interactive_console(resize_command)

    print('Fixing the nibbly bits for the partition itself')
    target_partition = device.partitions(full_paths=True)[0]
    interactive_console(['sudo', 'e2fsck', '-f', target_partition])

    print('Fixing ext4 so it goes all the way to the end')
    target_end = device.partition_specs(2)['End']
    interactive_console(['sudo', 'resize2fs', target_partition, target_end])

    print('Success!')


def polish_drive(device, ssid, psk, user, hostname):
    mount_dir = mkdtemp()
    mount_command = [
        'sudo',
        'mount',
        device.partitions(full_paths=True)[0],
        mount_dir]

    print('Mounting device locally')
    interactive_console(mount_command)

    print('Changing password acceptance on ssh policy to "no thanks"')
    sed_ssh_command = [
        'sudo',
        'sed',
        '-i',
        's/#PasswordAuthentication yes/PasswordAuthentication no/',
        os.path.join(mount_dir, 'etc', 'ssh', 'sshd_config')
    ]
    interactive_console(sed_ssh_command)

    print('Creating a .ssh directory for pi user.')
    mkdir_command = [
        'sudo',
        'mkdir',
        os.path.join(mount_dir, 'home', 'pi', '.ssh')
    ]
    interactive_console(mkdir_command)

    print('adding ~/.ssh/id_rsa.pub to ~/.ssh/authorized_keys')
    authorized_keys_command = [
        'sudo',
        'cp',
        os.path.join(os.path.expanduser('~/'), '.ssh', 'id_rsa.pub'),
        os.path.join(mount_dir, 'home', 'pi', '.ssh', 'authorized_keys')
    ]
    interactive_console(authorized_keys_command)

    print('Chowning the whole thing as UID=pID')
    chown_command = [
        'sudo',
        'chown',
        '-R',
        '1000:1000',
        os.path.join(mount_dir, 'home', 'pi', '.ssh')
    ]
    interactive_console(chown_command)

    print('Stricting up perms on .ssh dir as well')
    chown_command = [
        'sudo',
        'chmod',
        '700',
        os.path.join(mount_dir, 'home', 'pi', '.ssh')
    ]
    interactive_console(chown_command)

    if ssid and psk:
        print('Throwing the wireless info into the wpa_supplicant.conf')
        supplicant = os.path.join(mount_dir, 'etc', 'wpa_supplicant', 'wpa_supplicant.conf')
        me = os.getlogin()

        interactive_console(['sudo', 'chown', me, supplicant])
        with open(supplicant, 'a') as f:
            f.write('\n')
            f.write('network={\n')
            f.write('    ssid="{ssid}"\n'.format(ssid=ssid))
            f.write('    psk="{psk}"\n'.format(psk=psk))
            f.write('}\n')
            f.write('\n')
        interactive_console(['sudo', 'chown', '0:0', supplicant])

    print('Killing the pi user. Time to die!')
    print('...')
    print('Removing pi name from etc/passwd')
    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/pi/{0}/'.format(user),
        os.path.join(mount_dir, 'etc', 'passwd')
    ])
    print('Steal pis password for user')
    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/pi/{0}/'.format(user),
        os.path.join(mount_dir, 'etc', 'shadow')
    ])
    print('Removing pi group from etc/passwd')
    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/pi/{0}/'.format(user),
        os.path.join(mount_dir, 'etc', 'passwd')
    ])
    print('Removing pi group from etc/sudoers.d/010_pi-nopasswd')
    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/pi/{0}/'.format(user),
        os.path.join(mount_dir, 'etc', 'sudoers.d', '010_pi-nopasswd')
    ])
    print('Removing pi group from etc/group')
    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/:pi/:{0}/'.format(user),
        os.path.join(mount_dir, 'etc', 'group')
    ])
    print('Removing pi group from etc/group, again')
    interactive_console([
        'sudo',
        'sed',
        '-E',
        '-i',
        's#^pi\:x\:1000#{0}:x:1000:#'.format(user),
        os.path.join(mount_dir, 'etc', 'group')
    ])
    print('Removing pi group from etc/gshadow')
    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/:pi/:{0}/'.format(user),
        os.path.join(mount_dir, 'etc', 'gshadow')
    ])
    print('Removing pi group from etc/gshadow, again')
    interactive_console([
        'sudo',
        'sed',
        '-E',
        '-i',
        's#^pi\:!\:\:#{0}:!::#'.format(user),
        os.path.join(mount_dir, 'etc', 'gshadow')
    ])
    print('Moving pi directory')
    interactive_console([
        'sudo',
        'mv',
        os.path.join(mount_dir, 'home', 'pi'),
        os.path.join(mount_dir, 'home', user)
    ])

    print('Autologging in new user')
    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/pi/{0}/'.format(user),
        os.path.join(
            mount_dir,
            'etc',
            'systemd',
            'system',
            'autologin@.service')
    ])

    print('Changing hostname',)
    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/raspberrypi/{0}/'.format(hostname),
        os.path.join(mount_dir, 'etc', 'hostname')
    ])

    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/raspberrypi/{0}/'.format(hostname),
        os.path.join(mount_dir, 'etc', 'hosts')
    ])
    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/raspberrypi/{0}/'.format(hostname),
        os.path.join(mount_dir, 'etc', 'hosts')
    ])
    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/raspberrypi/{0}/'.format(hostname),
        os.path.join(mount_dir, 'etc', 'hosts')
    ])
    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/raspberrypi/{0}/'.format(hostname),
        os.path.join(mount_dir, 'etc', 'ssh', 'ssh_host_rsa_key.pub')
    ])
    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/raspberrypi/{0}/'.format(hostname),
        os.path.join(mount_dir, 'etc', 'ssh', 'ssh_host_ecdsa_key.pub')
    ])
    interactive_console([
        'sudo',
        'sed',
        '-i',
        's/raspberrypi/{0}/'.format(hostname),
        os.path.join(mount_dir, 'etc', 'ssh', 'ssh_host_dsa_key.pub')
    ])

    print('Fix the /boot fstab partition')
    interactive_console([
        'sudo',
        'sed',
        '-i',
        '-E',
        's#PARTUUID=.*-01#/dev/mmcblk0p1#',
        os.path.join(mount_dir, 'etc', 'fstab')
    ])
    print('Fix the root fstab partition')
    interactive_console([
        'sudo',
        'sed',
        '-i',
        '-E',
        's#PARTUUID=.*-02#/dev/sda2#',
        os.path.join(mount_dir, 'etc', 'fstab')
    ])

    print('Enabling SSH service on boot')
    ssh_service_path = os.path.join(mount_dir, 'lib', 'systemd', 'system', 'ssh.service')
    symlink_path = os.path.join(mount_dir, 'etc', 'systemd', 'system', 'multi-user.target.wants', 'ssh.service')
    enable_command = ['sudo', 'ln', '-s', ssh_service_path, symlink_path]
    interactive_console(enable_command)

    print('Good to go! Unmounting')
    umount_command = ['sudo', 'umount', mount_dir]
    interactive_console(umount_command)

    print('Removing temp dir')
    os.rmdir(mount_dir)

    print('All done!')
