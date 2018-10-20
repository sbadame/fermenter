#!/bin/bash

sudo modprobe w1-gpio
sudo modprobe w1-therm

# If you have more than one Sensor connected, you'll see multiple 28-xxx files.
# Each one will have the unique serial number so you may want to plug one in at
# a time, look at what file is created, and label the sensor!

dev=$(ls /sys/bus/w1/devices | grep '^28-')
echo "/sys/bus/w1/devices/$dev/w1_slave"
