# Raspi-maker
Scripts for setting up the base sd card and thumb drive for
a raspberry pi. This is something I've needed to do a lot
manually, so I wrote up scripts to automate the process and
hopefully others can use it.

## Thinking
Currently, the most stable RPIs that I own are the ones where
I use the SD card as a read-only boot drive, and have my root
file system on a nice thumb drive that I provide to my RPI.

The benefits here are that as the SD card never gets mounted
for read-write, power outages no longer can corrupt the disk.

For some reason thumb drives seem more resilient to this.

This script provisions Raspbian on a thumb drive, and then
copies the boot system to the SD card and modifies it ever
so slightly to point at the thumb drive on the final RPI
system.

In addition, because we have access to the eventual root fs,
we can update `/etc/ssh/sshd_config` to be more secure, and
insert a trusted key into `.ssh/authorized_keys` of the pi
user. This is just good practice- if you can resolve host
names on your network, this means you can plug in an RPI and
immediately get secure shell access to it.

## Installation / Requirements
Needs python 2.7 and to be run from a linux system, in my
case Ubuntu 16.04. Needs passwordless sudo.

## Usage
Run the `./run.py` command and then follow the interactive
prompts. It takes some guesses about your system (that I
use to protect my own), like it won't let you mess with the
`sda` device by accident.
