"""CLI Helpers."""

def ask(prompt, options):
    """Ask for a decision among options"""
    print prompt
    print 'Your options are:'
    print ' '.join(options)
    while True:
        user_input = raw_input('--> ')
        if user_input in options:
            print 'You chose:'
            print options[user_input]
            option = options[user_input]
            del options[user_input]
            return option
        else:
            print 'That\'s not a valid option, bucko'
            print 'try again.'

def print_devices(devices):
    print devices
    for device in devices:
        print device, '--', devices[device]
    print ''

def devices_prompt(devices):
    sd_card = ask(
        'Which device is your SD card (boot card for rpi):',
        devices
    )
    print ''
    thumb_drive = ask(
        'Which device is your USB Thumb Drive? (this will become the RPI root partition):',
        devices
    )
    print ''
    print 'OK, looks like your SD Card is'
    print sd_card
    print 'And your USB Thumb Drive is'
    print thumb_drive
    you_sure = ask('Are you sure?'.format(sd_card.blk_id), {'Y': 'y', 'n': 'n'})

    if you_sure == 'Y':
        print 'Great! Lets go.'
    elif you_sure == 'n':
        exit()
    return sd_card, thumb_drive