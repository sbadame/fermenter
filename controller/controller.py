
import json
import subprocess
import sys
import time
import fcntl

from collections import namedtuple

State = namedtuple('State', 'state, timestamp')
_UNINITIALIZED = 'uninitialized'
_COOLING = 'cooling'
_OFF = 'off'

class Gpio(object):
  _PIN = 'GPIO. 0'

  def __init__(self, gpio_path):
    self._gpio_path = gpio_path

  def _gpio(self, args):
    subprocess.check_call([self._gpio_path] + args)

  def init(self):
    self._gpio(['mode', self._PIN, 'out'])

  def high(self):
    self._gpio(['write', self._PIN, '1'])

  def low(self):
    self._gpio(['write', self._PIN, '0'])

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
      kwargs = json.loads(f.read())
      if 'timestamp' not in kwargs:
        kwargs['timestamp'] = int(time.time())
      return State(**kwargs)
  except FileNotFoundError:
      return State(_UNINITIALIZED, int(time.time()))

class Controller(object):

  def __init__(self, gpio, state_file, log_file):
    self._gpio = gpio
    self._state_file = state_file
    self._log_file = log_file

  def _write(self, state):
    with open(self._state_file, 'w') as f:
      f.write(json.dumps(state._asdict()))
    with open(self._log_file, 'a') as f:
      f.write('%d,%s\n' % (state.timestamp, state.state))


  def cool(self):
    self._gpio.high()
    self._write(State(_COOLING, int(time.time())))

  def off(self):
    self._gpio.low()
    self._write(State(_OFF, int(time.time())))


def decide(gpio, realtime_log, monitor_thermometer, controller_state, controller_log, desired, threshold):
  controller = Controller(gpio, controller_state, controller_log)
  temp = read_temp(realtime_log, monitor_thermometer)

  s = read_state(controller_state)

  if s.state == _UNINITIALIZED:
    if temp < desired:
      controller.off()
    else:
      controller.cool()
  elif s.state == _OFF:
    if temp > desired + threshold:
      controller.cool()
  elif s.state == _COOLING:
    if temp < desired - threshold:
      controller.off()
  else:
    raise Exception('Unhandled state: %s' % s)

def _main(poll_seconds, *args):
  if poll_seconds < 0:
    decide(*args)
    sys.exit(0)
  else:
    while True:
      decide(*args)
      time.sleep(poll_seconds)

if __name__ == "__main__":
  with open(sys.argv[1], 'r') as fd:
    config = json.loads(fd.read())

  gpio = Gpio(config['gpio_path'])
  args = [
    config['control_every_n_seconds'],
    gpio,
    config['realtime_log'],
    config['monitor_thermometer'],
    config['controller_state'],
    config['controller_state_log'],
    config['desired_temp_celsius'],
    config['threshold_degrees_celsius'],
  ]
  gpio.init()
  _main(*args)
