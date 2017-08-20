"""Configure it just, just right."""
from ConfigParser import ConfigParser
from ConfigParser import NoSectionError
import os


CONFIG_FILE='./config.ini'

def file_config_exists():
    if os.path.exists(CONFIG_FILE):
        return True
    return False

def parse_config():
    parser = ConfigParser()
    parser.readfp(CONFIG_FILE)

    sd_card = parser.get('devices', 'sd_card')
    thumb_drive = parser.get('devices', 'thumb_drive')

    try:
        ssid = parser.get('wireless', 'ssid')
        psk = parser.get('wireless', 'psk')

    except NoSectionError:
        ssid = None
        psk = None

    return sd_card, thumb_drive, ssid, psk
