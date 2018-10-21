#!/usr/bin/python3

import sys
import time


def parse_therm(content, seconds_since_epoch):
  str_time = '%.0f' % seconds_since_epoch

  lines = content.splitlines()

  if 'YES' not in lines[0]:
    return ','.join([str_time, 'ERROR', 0, 0])

  _, temp = lines[1].split('t=')
  celsius = int(temp)/1000.0
  to_f = lambda c: (c * 9.0/5) + 32
  return ','.join([str_time, 'OK', '%2.3f' % celsius, '%2.3f' % to_f(celsius)])


def main(thermostat_file, poll_every_n_seconds):
  while True:
    try:
      content = open(thermostat_file, 'r').read()
    except KeyboardInterrupt:
      sys.exit(0)
    print(parse_therm(content, time.time()))
    try:
      time.sleep(poll_every_n_seconds)
    except KeyboardInterrupt:
      sys.exit(0)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print('./print_temperature $(./list_therms)')
    sys.exit(1)
  file_name = sys.argv[1]
  config = {
    'thermostat_file': file_name,
    'poll_every_n_seconds': 30,
  }
  print(config)
  main(**config)
