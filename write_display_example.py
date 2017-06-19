#!/usr/bin/python3
# #####################################
# info: This script writes to VFD
#
# date: 2017-06-13
# version: 0.1.1
#
# Dependencies:
# $ sudo apt-get install python3-dev libusb-1.0-0-dev libudev-dev python3-pip
# $ sudo pip3 install --upgrade setuptools
# $ sudo pip3 install hidapi

# place a file 99-hidraw-vfd-permissions.rules with this line to /etc/udev/rules.d:
# SUBSYSTEM=="usb", ATTR{idVendor}=="19c2", ATTR{idProduct}=="6a11", MODE="0666"
#
# history:
#
# #####################################
# Import solution :-)
import VFD_MDM166
import time


#generate new device:
myVFD=VFD_MDM166.usbVFD()

#blank:
myVFD.clear_display()

#set audio iconds:
myVFD.set_rec()
myVFD.set_vol_logo()
for i in range(1,15):
    myVFD.set_vol_bar(segment=i)


# show clock:
#myVFD.set_clock_data(14,27)
#myVFD.set_clock_format(clock_format='24',row='upper')

#set brightness:
myVFD.dimming(50)

#write testtext:
myVFD.write_str('SOLAR POWER')
