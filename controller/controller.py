
import json
import subprocess
import sys
import time
import fcntl
import fsm as fsm_lib

fsm = fsm_lib.FSM("""
  uninitialized -> off     | temp < desired
  uninitialized -> cooling | temp > desired
  cooling -> off           | temp < desired - threshold
  off -> cooling           | temp > desired + threshold
""")


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


class Controller(object):

  def __init__(self, gpio, log_file):
    self._gpio = gpio
    self._log_file = log_file

  def _write(self, state):
    with open(self._log_file, 'a') as f:
      f.write('%d,%s\n' % (int(time.time()), state))

  def cool(self):
    self._gpio.high()
    self._write('cooling')

  def off(self):
    self._gpio.low()
    self._write('off')


def decide(gpio, realtime_log, monitor_thermometer, controller_log, desired, threshold):
  controller = Controller(gpio, controller_log)
  temp = read_temp(realtime_log, monitor_thermometer)
  fsm.evaluate({'temp': temp, 'desired': desired, 'threshold': threshold})
  {'off': controller.off, 'cooling': controller.cool}[fsm.current.name]()

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
    config['controller_state_log'],
    config['desired_temp_celsius'],
    config['threshold_degrees_celsius'],
  ]
  gpio.init()
  _main(*args)
