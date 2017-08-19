from pytest import mark
from raspi_maker.errors import check_for_root_device
from raspi_maker.errors import NotGunnaDoItException


@mark.unit
def test_check_for_root_device_success():
    assert check_for_root_device('sdb', 'mmcblk0')

    assert check_for_root_device('sdb1', 'sda3', 'dd101202')


@mark.unit
def test_check_for_root_device_failure():
    try:
        assert not check_for_root_device('sdb', 'sda')
    except NotGunnaDoItException:
        assert True