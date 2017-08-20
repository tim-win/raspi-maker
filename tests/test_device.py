# -*- coding: utf-8 -*-
"""Tests for the old block devices."""

import os
from pytest import mark


from raspi_maker.device import get_devices
from raspi_maker.device import _get_blk_size_bytes
from raspi_maker.device import _get_hr_size
from raspi_maker.device import _get_lsblk_output
from raspi_maker.device import _get_model
from raspi_maker.device import _get_vendor
from raspi_maker.device import _partition_details
from raspi_maker.device import _device_partitions
from raspi_maker.device import _get_partitions
from raspi_maker.device import Device


@mark.unit
def test__get_blk_size_bytes_test_inputs():
    assert 16008609792 == _get_blk_size_bytes('sdb', '31266816\n'), (
        'Block size is off on test string.')


@mark.unit
def test__get_hr_size():
    test_cases = [
        ('0', '0B'),
        ('1', '1B'),
        ('-1', '1B'),
        ('1000', '1000B'),
        ('100000', '97KB'),
        ('-10000', '9KB'),
        ('100000000', '95MB'),
        ('1000000000000', '931GB'),
        ('100000000000000000', '88PB'),
        ('900000000000000000', '799PB'),
    ]
    for x in test_cases:
        size = _get_hr_size(x[0])
        assert type(size) == str, 'Got wrong type back :('
        assert size == x[1], 'Got bad answer back. Learn to math!'
        assert len(size) < 6, 'Didnt trim enough :('


@mark.unit
def test__partition_details():
    sample_input = '''Model: SanDisk Cruzer Fit (scsi)
Disk /dev/sdc: 31266816s
Sector size (logical/physical): 512B/512B
Partition Table: msdos
Disk Flags: 

Number  Start    End       Size      Type     File system  Flags
 1      8192s    137215s   129024s   primary  fat16        lba
 2      137216s  8538111s  8400896s  primary  ext4
'''
    test1 = {
        'Number'
        'Start'
        'End'
        'Size'
        'Type'
        'File system'
        'Flags'
    }
    assert '1' == _partition_details(sample_input, 1)['Number']
    assert '8192s' == _partition_details(sample_input, 1)['Start']
    assert '137215s' == _partition_details(sample_input, 1)['End']
    assert '129024s' == _partition_details(sample_input, 1)['Size']
    assert 'primary' == _partition_details(sample_input, 1)['Type']
    assert 'fat16' == _partition_details(sample_input, 1)['File system']
    assert 'lba' == _partition_details(sample_input, 1)['Flags']

    assert '2' == _partition_details(sample_input, 2)['Number']
    assert '137216s' == _partition_details(sample_input, 2)['Start']
    assert '8538111s' == _partition_details(sample_input, 2)['End']
    assert '8400896s' == _partition_details(sample_input, 2)['Size']
    assert 'primary' == _partition_details(sample_input, 2)['Type']
    assert 'ext4' == _partition_details(sample_input, 2)['File system']
    assert None == _partition_details(sample_input, 2)['Flags']


lsblk_example = '''NAME                    MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINT
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


@mark.unit
def test__get_partitions_simple():
    assert _get_partitions(lsblk_example, 'sdc') == ['sdc1', 'sdc2']


@mark.unit
def test__get_partitions_full():
    assert _get_partitions(lsblk_example, 'sdc', full_paths=True) == ['/dev/sdc1', '/dev/sdc2']


@mark.unit
def test__get_partitions_fancy():
    assert _get_partitions(lsblk_example, 'mmcblk0', full_paths=True) == ['/dev/mmcblk0p1']


@mark.functional
def test_get_devices():
    assert get_devices(), 'Cant find any devices, maybe this is broke.'


@mark.functional
def test_get_blk_size_path_makes_sense():
    assert os.path.exists('/sys/block/sda/size'), (
        'I have made a terrible mistake about the filesystem, size file does not exist.')


@mark.functional
def test__get_blk_size_bytes_test_functions():
    assert 100 < _get_blk_size_bytes('sda'), 'SDA should really be bigger than 100 bytes.'


@mark.functional
def test__get_vendor_functional(): 
    assert _get_vendor('sda')


@mark.functional
def test__get_vendor_missing_functional():
    fake_device = 'natoheunstahoeunsth'
    assert fake_device == _get_vendor(fake_device)


@mark.functional
def test__get_model_functional():
    assert _get_model('sda')


@mark.functional
def test__get_model_missing_functional():
    fake_device = 'natoheunstahoeunsth'
    assert fake_device == _get_model(fake_device)


@mark.functional
def test_device_init():
    assert Device('sda')


@mark.functional
def test_device_partitions_property():
    assert Device('sda').partitions


@mark.functional
def test__device_partitions():
    assert _device_partitions('sda')

@mark.functional
def test__get_lsblk_output():
    assert _get_lsblk_output()