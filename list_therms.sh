#!/bin/bash

# PROTIP-- Use this with $watch ./list_therms.sh <args>

# These should be loaded on bootup. Checkout /etc/modules-load.d/modules.conf
# sudo modprobe w1-gpio
# sudo modprobe w1-therm

# If you have more than one Sensor connected, you'll see multiple 28-xxx files.
# Each one will have the unique serial number so you may want to plug one in at
# a time, look at what file is created, and label the sensor!

ls /sys/bus/w1/devices/28-*/w1_slave
 
for i in "$@"
do
case $i in
 -a|--all)
 PRINT_TEMPS='YES'
 shift
 break;;
esac
done

if [[ -n "$PRINT_TEMPS" ]]; then
  # Linux is too weird, this is the best approach that I see to print file
  # names with content.
  # Oh, and you always need 1 file, sooo lets pre-pend /dev/null
  grep "" /dev/null /sys/bus/w1/devices/28-*/w1_slave
fi
