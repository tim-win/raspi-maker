# -*- coding: utf-8 -*-
"""Helper Functions for the file system."""
import os
from subprocess import Popen, PIPE, STDOUT
from console import console


class Device(object):
    """Abstraction around a given block device."""
    def __init__(self, blk_id):
        assert os.path.exists('/dev/')
        self.blk_id = blk_id
        
        size = _get_blk_size_bytes(blk_id)
        self.hr_size = _get_hr_size(size)

        self.vendor = _get_vendor(blk_id)
        self.model = _get_model(blk_id)

        self.path = '/dev/{0}'.format(blk_id)

    @property
    def partitions(self):
        return _get_partitions(self.blk_id)

    def unmount_all(self):
        """Runs umount on all partitions. Regardless.

        Returns
        -------
        bool : True if successful.
        `"""
        for mount in self.mount_points:
            print 'Unmounting {0}'.format(mount)
            p = Popen(
                ['sudo', 'umount', mount],
                stdout=PIPE,
                stderr=STDOUT)  # stdout=PIPE makes this line blocking.
        print True

    @property
    def mount_points(self):
        mounts = []
        for partition in self.partitions:
            mounts += _get_partition_mounts(partition)
        return mounts


    def __str__(self):
        return '{vendor} {model} {hr_size}'.format(
            vendor=self.vendor,
            model=self.model,
            hr_size=self.hr_size)

    def __repr__(self):
        return self.__str__()


def get_devices():
    """Get all devices.

    Returns
    -------
    list : list of strings related to each device.
    """

    devices = []

    cmd = ['lsblk']
    for line in console(cmd).split('\n'):
        if 'disk' in line:
            devices.append(line.split()[0])
    devices.sort()

    return devices


def _get_blk_size_bytes(blk_id, test=None):
    """Return a block device total size in bytes.

    Parameters
    ----------
    blk_id : str
        id of the block (sda, sdb, etc)

    test : str
        pass a string instead of reading from disk

    Returns
    -------
    int : Block device total size in bytes
    """

    size_format = '/sys/block/{blk_id}/size'
    if test is None:
        with open(size_format.format(blk_id=blk_id)) as f:
            size = f.read()
    else:
        size = test
    return int(size.strip()) * 512  # /sys/block/{blk_id}/size is in 512B blocks.


def _get_hr_size(bytes):
    """Returns a human readable description of the bytes.
    
    Parameters
    ----------
    bytes : int
        Number of bytes. Accepts anything that can coerce to a float.

    Returns
    -------
    str : a human readable string, in the format '%d%t' where %d is
        digits and %t is the byte size (MB, TB, PB, etc).

    """
    mapping = {
        0: 'B',
        1: 'KB',
        2: 'MB',
        3: 'GB',
        4: 'TB',
        5: 'PB'
    }

    size = abs(float(bytes))

    counter = 0
    while size >= 1024:
        counter +=1
        size /= 1024.0

    index = str(size).index('.')

    return str(size)[:index] + mapping[counter]


def _get_vendor(blk_id):
    """Get the name of the vendor for a given block."""
    vendor_format = '/sys/block/{blk_id}/device/vendor'
    path = vendor_format.format(blk_id=blk_id)
    if os.path.exists(path):
        with open(path) as f:
            raw = f.read().strip()
        return raw
    return blk_id


def _get_model(blk_id):
    model_format = '/sys/block/{blk_id}/device/model'
    model_path = model_format.format(blk_id=blk_id)
    if os.path.exists(model_path):
        with open(model_path) as f:
            raw = f.read().strip()
        return raw
    return blk_id


def _get_partitions(blk_id):
    """Get partitions for a given block id."""

    partitions = []

    p = Popen(['lsblk'], stdout=PIPE)

    gen = iter(p.stdout.readline, b'')

    flagged = False
    for line in gen:

        # exhaust lines we don't care about
        if blk_id in line and not flagged:
            flagged = True
            continue

        # Only start caring once the flag is set
        if '─' in line and flagged:
            stripped_line = line.lstrip('─└├ ')
            components = stripped_line.split()
            partitions.append(components[0])

        # if the flag is set and we're out of subdivisions
        # break out of the generator
        elif flagged:
            break

    return partitions

def _get_partition_mounts(partition_name):
    """Return all mounts for this partition."""
    mounts = []
    with open('/etc/mtab') as f:
        for line in f:
            if partition_name in line:
                mounts.append(line.split()[1])
    return mounts

