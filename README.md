# Raspi-maker

Generate both a SD card and a thumb drive with customizations
before booting your RPi for the first time.

## Problem Space
Two primary concerns drove this work. First, getting an RPi
that is intended to be headless onto a network can be
terrible. Ideally, you'd have a space monitor, keyboard, and
plenty of desk space to quickly set up / manually configure
/ finally tear back down.

The second problem is that, god dammit, SD cards are terrible.
No matter what I do, my power is not reliable, and that means
my SD cards end up corrupt in awful places (e tu, `/bin/`?!')
so relying on the SD card as little as possible makes sense.

## Problems: Solved

### First Solution: Polish the Root Partition at Flash Time
We have access to the root partition when we flash it to a
device, and most of the polish I apply to RPis before calling
them done is a handful of changes to disk. So when flashing
the root partition, lets also polish it: add some security
and QoL support.

In fact, it makes the most sense to automate the whole process
in three steps: first clear the media, then flash it, then
polish. No need to remove or take user input, like any good
deployment system.

Here are the changes made to the stock Raspbian install:

* Change password auth policy for ssh connections to "no thanks"
** Friends dont let friends connect with insecure passwords.
* Create a .ssh directory with correct perms
* Populate pi's `authorized_keys` file with `~/.ssh/id_rsa.pub`
* Populate wpa_supplicant.conf with provided psk and ssid
** Allows the RPi to "just connect" on first boot to the Wifi.

Now the boot drive is provisioned such that the RPi will
connect on first boot to the wifi in a secured way, and
support SSH access using the private key auth. Perfect!

### Second Problem: 
Easiest way to limit the risks inherent in booting to an SD
card is to use it for the bare minimum- only for booting.

The script will set up a second media device, a thumb drive,
to store the mounted root partition. In practice, this is
significantly more stable than booting directly to the SD
card, and I've gone from one SD card failure every couple
of months to zero failures using this method (YMMV though).

This whole idea is taken from the great instructables
guide here: https://goo.gl/hzk6fk.

## Installation / Requirements
Needs python 2.7 and to be run from a linux system, in my
case Ubuntu 16.04. Needs passwordless sudo.

No other python dependencies, just stdlibs. Like a boss.

## Usage
Run the `./run.py` command and then follow the interactive
prompts. It takes some guesses about your system (that I
use to protect my own), like it won't let you mess with the
`sda` device by accident.
