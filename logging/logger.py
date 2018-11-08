import glob
import sys
import time
import json
import fcntl


def update_file(realtime_log, content):
  with open(realtime_log, 'w') as fd:
    fcntl.lockf(fd, fcntl.LOCK_EX)
    fd.write(content)


def parse_therm(name, content, seconds_since_epoch):
  str_time = '%.0f' % seconds_since_epoch

  lines = content.splitlines()

  if 'YES' not in lines[0]:
    return ','.join([str_time, name, 'ERROR', '0', '0'])

  _, temp = lines[1].split('t=')
  celsius = int(temp)/1000.0
  return ','.join([str_time, name, 'OK', '%2.1f' % celsius])


def main(thermometer_files, temperature_log, realtime_log, read_temps_every_n_seconds, thermometers):
  while True:
    try:
      contents = [
        (f, open(f, 'r').read()) for f in thermometer_files]
    except KeyboardInterrupt:
      sys.exit(0)
    entries = []
    for fname, fcontents in contents:
      name = thermometers[fname]['name']
      entries.append(parse_therm(name, fcontents, time.time()))
    entry = '\n'.join(entries)
    print(entry, file=temperature_log, flush=True)
    update_file(realtime_log, entry)
    try:
      time.sleep(read_temps_every_n_seconds)
    except KeyboardInterrupt:
      sys.exit(0)


if __name__ == "__main__":
  files = glob.glob('/sys/bus/w1/devices/28-*/w1_slave')

  config = json.loads(open(sys.argv[1], 'r').read())

  if len(sys.argv) > 2:
    out = open(sys.argv[2], 'a')
    print('# %s, %s' % (files, config), file=out, flush=True)
  else:
    out = sys.stdout

  print(files, config, flush=True)

  main(files, out, **config)
