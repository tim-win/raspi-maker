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

    def partitions(self, full=False):
        lsblk_output = _get_lsblk_output()
        return _get_partitions(lsblk_output, self.blk_id, full)

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
        for partition in self.partitions():
            mounts += _get_partition_mounts(partition)
        return mounts


    def __str__(self):
        return '{vendor} {model} {hr_size}'.format(
            vendor=self.vendor,
            model=self.model,
            hr_size=self.hr_size)

    def __repr__(self):
        return self.__str__()

    def partition_specs(self, number):
        """Get the specs of the boot partition you need to copy.
        Parameters
        ----------
        number : int
            number of partition you want data for

        Returns
        -------
        dict : column titles vs parameters for partition

        Raises
        ------
        IndexError : if you choose a partition that isn't there.
        """

        device_unit_info = _device_partitions(self.path)
        return _partition_details(device_unit_info, number)


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



def _get_lsblk_output():
    """This is what we use to get our partitions."""
    p = Popen(['lsblk'], stdout=PIPE)
    return p.stdout.read()

    
def _get_partitions(lsblk_output, blk_id, full_paths=False):
    """Get partitions for a given block id.

    Parameters
    ----------
    lsblk_output : str
        Output of lsblk. This gives us all the info we need,
        so we just need to pull it apart. Example:
            '''NAME                    MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINT
            sda                       8:0    0 931.5G  0 disk  
            ├─sda1                    8:1    0   512M  0 part  /boot/efi
            ├─sda2                    8:2    0   488M  0 part  /boot
            └─sda3                    8:3    0 930.5G  0 part  
              └─sda3_crypt          252:0    0 930.5G  0 crypt 
                ├─ubuntu--vg-root   252:1    0 898.7G  0 lvm   /
                └─ubuntu--vg-swap_1 252:2    0  31.9G  0 lvm   [SWAP]
            sdc                       8:32   1  14.9G  0 disk  
            ├─sdc1                    8:33   1    63M  0 part  
            └─sdc2                    8:34   1     4G  0 part  
            sr0                      11:0    1  1024M  0 rom   
            mmcblk0                 179:0    0    29G  0 disk  
            └─mmcblk0p1             179:1    0    63M  0 part  
            '''

    blk_id : str
        root block id that we're getting partitions for

    full_paths : bool
        Whether to return the id of each partition, or its
        full path.

    Returns
    -------
    list : list of strings of partitions. Can be empty.
    """

    partitions = []


    flagged = False
    for line in lsblk_output.splitlines():

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

    if full_paths:
        partitions = ['/dev/{0}'.format(partition) for partition in partitions]

    return partitions

def _get_partition_mounts(partition_name):
    """Return all mounts for this partition."""
    mounts = []
    with open('/etc/mtab') as f:
        for line in f:
            if partition_name in line:
                mounts.append(line.split()[1])
    return mounts


def _device_partitions(device_path):
    """Print out the deets for this device.

    Example:
    """
    cmd = ['sudo', 'parted', device_path, 'unit', 's', 'print']

    p = Popen(
        cmd,
        stdout=PIPE)

    return p.stdout.read()


def _partition_details(device_unit_info, number):
    """Pull details of a numbered partition out, put into dict.
    Parameters
    ----------
    device_unit_info : str
        Output of _device_partitions. Example:

            '''Model: SanDisk Cruzer Fit (scsi)
            Disk /dev/sdc: 31266816s
            Sector size (logical/physical): 512B/512B
            Partition Table: msdos
            Disk Flags: 

            Number  Start    End       Size      Type     File system  Flags
             1      8192s    137215s   129024s   primary  fat16        lba
             2      137216s  8538111s  8400896s  primary  ext4
            '''

    Returns
    -------
    dict : label: value mappings for partition.
    """

    for line in device_unit_info.splitlines():
        split_line = line.split()
        try:
            if split_line and int(split_line[0]) == number:
                values = split_line
                break
        except ValueError:
            # Not our line, that's for sure!
            continue
    deets = {
        'Number': split_line.pop(0),
        'Start': split_line.pop(0),
        'End': split_line.pop(0),
        'Size': split_line.pop(0),
        'Type': split_line.pop(0),
        'File system': split_line.pop(0),
        'Flags': split_line.pop(0) if split_line else None
    }

    return deets
