
import json
import subprocess
import sys
import time
import fcntl

from collections import namedtuple

State = namedtuple('State', 'state')
_UNINITIALIZED = 'uninitialized'
_COOLING = 'cooling'
_OFF = 'off'

_PIN = 'GPIO. 0'

_gpio = lambda args: subprocess.call(['/usr/bin/gpio'] + args)
_INIT = lambda: _gpio(['mode', _PIN, 'out'])
_HIGH = lambda: _gpio(['write', _PIN, '1'])
_LOW = lambda: _gpio(['write', _PIN, '0'])


def read_with_lock(file_path):
  with open(file_path, 'r') as fd:
    fcntl.lockf(fd, fcntl.LOCK_SH)
    return fd.read()

def read_temp(file_path, monitor_thermometer):
  content = read_with_lock(file_path)
  for line in content.split('\n'):
    timestamp, name, status, temp = line.split(',')
    if name == monitor_thermometer:
      if status != 'OK':
        raise Exception('Thermometer is not OK. Was: %s' % (status))
      return float(temp)
  raise Exception('%s was not in the list thermometers.' % (monitor_thermometer))


def read_state(file_path):
  try:
    with open(file_path, 'r') as f:
      return State(**json.loads(f.read()))
  except FileNotFoundError:
      return State(_UNINITIALIZED)

def write(file_path, state):
  with open(file_path, 'w') as f:
    f.write(json.dumps(state._asdict()))

def _cool(state_file):
  _HIGH()
  write(state_file, State(_COOLING))

def _off(state_file):
  _LOW()
  write(state_file, State(_OFF))

def decide(realtime_log, monitor_thermometer, controller_state, desired, threshold):
  temp = read_temp(realtime_log, monitor_thermometer)
  s = read_state(controller_state)

  if s.state == _UNINITIALIZED:
    if temp < desired:
      _off(controller_state)
    else:
      _cool(controller_state)
  elif s.state == _OFF:
    if temp > desired + threshold:
      _cool(controller_state)
  elif s.state == _COOLING:
    if temp < desired - threshold:
      _off(controller_state)
  else:
    raise Exception('Unhandled state: %s' % s)

def _main(poll_seconds, *args):
  while True:
    decide(*args)
    time.sleep(poll_seconds)

if __name__ == "__main__":
  with open(sys.argv[1], 'r') as fd:
    config = json.loads(fd.read())
  args = [
    config['control_every_n_seconds'],
    config['realtime_log'],
    config['monitor_thermometer'],
    config['controller_state'],
    config['desired_temp_celsius'],
    config['threshold_degrees_celsius'],
  ]
  _INIT()
  _main(*args)
