#!/usr/bin/python3

import glob
import sys
import time
import json


def parse_therm(name, content, seconds_since_epoch):
  str_time = '%.0f' % seconds_since_epoch

  lines = content.splitlines()

  if 'YES' not in lines[0]:
    return ','.join([str_time, 'ERROR', 0, 0])

  _, temp = lines[1].split('t=')
  celsius = int(temp)/1000.0
  to_f = lambda c: (c * 9.0/5) + 32
  return ','.join([str_time, name, 'OK', '%2.3f' % celsius, '%2.3f' % to_f(celsius)])


def main(thermostat_files, poll_every_n_seconds, thermostat_names):
  while True:
    try:
      contents = [
        (f, open(f, 'r').read()) for f in thermostat_files]
    except KeyboardInterrupt:
      sys.exit(0)
    for fname, fcontents in contents:
      name = fname
      if fname in thermostat_names:
        name = thermostat_names[fname]
      print(parse_therm(name, fcontents, time.time()))
    try:
      time.sleep(poll_every_n_seconds)
    except KeyboardInterrupt:
      sys.exit(0)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    files = glob.glob('/sys/bus/w1/devices/28-*/w1_slave')
  else:
    files = sys.argv[1:]

  try:
    config = json.loads(open('data/config.json', 'r').read())
  except FileNotFoundError:
    config = {}

  if 'poll_every_n_seconds' not in config:
    config['poll_every_n_seconds'] = 30

  print(files, config)
  main(files, **config)
