
import json
import subprocess
import sys
import time
import fcntl

from collections import namedtuple

State = namedtuple(
  'State', 'current_temp_c, desired_temp_c, fridge')

_PIN = 'GPIO. 0'

_gpio = lambda args: subprocess.call(['/usr/bin/gpio'] + args)
_INIT = lambda: _gpio('mode', _PIN, 'out')
_HIGH = lambda: _gpio('write', _PIN, '1')
_LOW = lambda: _gpio('write', _PIN, '0')


def read_with_lock(file_path):
  with open(file_path, 'r') as fd:
    fcntl.lockf(fd, fcntl.LOCK_SH)
    return fd.read()

def read(file_path):
  with open(file_path, 'r') as f:
    return State(**json.loads(f.read()))

def write(file_path, state):
  with open(file_path, 'w') as f:
    f.write(json.dumps(state._asdict()))

def log(log_file, msg):
  with open(log_file, 'a') as f:
    f.write('%.0f,%s\n' % (time.time(), msg))

def _cool(state, state_file, log_file):
  _HIGH()
  write(state_file, s._replace(fridge='COOLING'))
  log(log_file, 'COOLING')

def _heat(state, state_file, log_file):
  _LOW()
  write(state_file, s._replace(fridge='HEATING'))
  log(log_file, 'HEATING')


def decide(state_file, log_file):
  s = read(state_file)
  if abs(s.current_temp_c - s.desired_temp_c) < 3:
    # If we're within 3 degrees of desired, just pass
  elif s.current_temp_c > s.desired_temp_c:
    _cool(s, log_file)
  elif s.current_temp_c < s.desired_temp_c:
    _heat(s, log_file)
  else:
    raise Exception('Unhandled state: %s' % s)

def _main(state_file):
  while True:
    decide()
    time.sleep(30)  

if __name__ == "__main__":
  with open(sys.argv[1], 'r') as fd:
    config = json.loads(fd.read())
  _INIT()
  _main(config.controller_state)
