#!/usr/bin/env python

import sys
import pytz

from datetime import datetime

def read(file_path):
  """Yields a tuple of (datetime, [values]) for each entry."""

  with open(file_path, 'r') as log:
    first_line = log.readline()
  
    line_count = 0
    while True:
      log_line = log.readline()
      line_count = line_count + 1
      if not log_line: # Could be a blank line, could be EOF... friggen python.
        break
      try:
        if log_line.strip().startswith('#'):
          continue
        entries =  [s.strip() for s in log_line.split(',')]
        timestamp = datetime.fromtimestamp(int(entries[0]), tz=pytz.UTC)
        yield (timestamp,  entries[1:])
      except:
        print('Error on line number %d: "%s"' % (line_count, log_line), file=sys.stderr)
        raise

if __name__ == '__main__':
  import sys
  for line in read(sys.argv[1]):
    print(line)
