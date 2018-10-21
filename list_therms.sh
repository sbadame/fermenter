#!/bin/bash

# These should be loaded on bootup. Checkout /etc/modules-load.d/modules.conf
# sudo modprobe w1-gpio
# sudo modprobe w1-therm

# If you have more than one Sensor connected, you'll see multiple 28-xxx files.
# Each one will have the unique serial number so you may want to plug one in at
# a time, look at what file is created, and label the sensor!

ls -l /sys/bus/w1/devices/28-*/w1_slave
