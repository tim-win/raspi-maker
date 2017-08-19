# -*- coding: utf-8 -*-
"""Tests for the old block devices."""

import os
from pytest import mark


from raspi_maker.device import get_devices
from raspi_maker.device import _get_blk_size_bytes
from raspi_maker.device import _get_hr_size
from raspi_maker.device import _get_vendor
from raspi_maker.device import _get_model
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
def test__get_partitions():
    assert _get_partitions('sda')

@mark.functional
def test_device_init():
    assert Device('sda')

@mark.functional
def test_device_partitions_property():
    assert Device('sda').partitions