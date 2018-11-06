import glob
import sys
import time
import json


def parse_therm(name, content, seconds_since_epoch):
  str_time = '%.0f' % seconds_since_epoch

  lines = content.splitlines()

  if 'YES' not in lines[0]:
    return ','.join([str_time, name, 'ERROR', '0', '0'])

  _, temp = lines[1].split('t=')
  celsius = int(temp)/1000.0
  return ','.join([str_time, name, 'OK', '%2.1f' % celsius])


def main(thermostat_files, temperature_log, poll_every_n_seconds, thermostats):
  while True:
    try:
      contents = [
        (f, open(f, 'r').read()) for f in thermostat_files]
    except KeyboardInterrupt:
      sys.exit(0)
    for fname, fcontents in contents:
      name = thermostats[fname]['name']
      print(parse_therm(name, fcontents, time.time()), file=temperature_log, flush=True)
    try:
      time.sleep(poll_every_n_seconds)
    except KeyboardInterrupt:
      sys.exit(0)


if __name__ == "__main__":
  files = glob.glob('/sys/bus/w1/devices/28-*/w1_slave')

  config = json.loads(open('data/config.json', 'r').read())

  if len(sys.argv) > 1:
    out = open(sys.argv[1], 'a')
    print('# %s, %s' % (files, config), file=out, flush=True)
  else:
    out = sys.stdout

  print(files, config, flush=True)

  main(files, out, **config)
