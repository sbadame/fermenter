#!/usr/bin/python

import sys
import time

_USAGE='''./print_temperature $(./list_therms)'''

to_fahrenheit = lambda c: (c * 9.0/5) + 32

def read_therm(therm):
  try:
    content = open(therm, 'r').read()
  except KeyboardInterrupt:
    sys.exit(0)
  lines = content.splitlines()
  status = 'YES' in lines[0]
  _, temp = lines[1].split('t=')
  celsius = int(temp)/1000.0
  return status, celsius, to_fahrenheit(celsius)


def main(thermostat):
  while True:
    temp = read_therm(thermostat)
    print temp
    try:
      time.sleep(1)
    except KeyboardInterrupt:
      sys.exit(0)

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print _USAGE
    sys.exit(1)
  file_name = sys.argv[1]
  main(file_name)
