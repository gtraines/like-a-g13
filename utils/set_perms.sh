#!/usr/bin/env bash

# It's still not the "muggle's tweak" that I'm really looking for, but at least this works:

# Apparently there are two directories for udev (I have no idea why):

# /etc/udev/rules.d
# /lib/udev/rules.d
# I'd been messing with the /lib one and getting nowhere. I found the /etc one here, and it does work:

# Put SUBSYSTEM=="usb", ATTRS{idVendor}=="VID", ATTRS{idProduct}=="PID", MODE="0666"

# VID is the USB-IF-assigned Vendor ID of the device in question *
# PID is the Vendor-assigned Product ID of the device in question *
# 0666 gives universal read/write access to whatever matches this line

# * $ lsusb to see all attached USB devices and their ID's.

# In /etc/udev/rules.d/xx-my-rule.rules (may need root/sudo permissions)

# xx is any number > 50 (the defaults are in 50, and higher numbers take priority)
# my-rule is whatever you want to call it
# must end in .rules
# Then udevadm control --reload-rules (may also need root/sudo permissions), and it should "just work" for that specific VID/PID pair.

G13_VENDOR_ID="046d"
G13_PRODUCT_ID="c21c"

cd /etc/udev/rules.d
sudo touch 999-g13-access.rules
sudo echo "SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"${G13_VENDOR_ID}\", ATTRS{idProduct}==\"${G13_PRODUCT_ID}\", MODE=\"0666\"" > 999-g13-access.rules
sudo touch 998-usb-access.rules
sudo echo "SUBSYSTEM==\"usb\", GROUP=\"users\", MODE=\"0666\"" > 998-usb-access.rules


sudo udevadm control --reload-rules
echo "Reloaded rules"
cd ${OLDPWD}
