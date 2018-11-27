#!/usr/bin/env python

import sys
import pytz

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

cert_file = sys.argv[1]
log_file = sys.argv[2]
_BATCH_SIZE = 500

# Use a service account
cred = credentials.Certificate(cert_file)
firebase_admin.initialize_app(cred)

db = firestore.client()
logentries = db.collection(u'controller_logentries')

try:
  latest_entry_timestamp = next(logentries.order_by(u'timestamp', direction=firestore.Query.DESCENDING).limit(1).get()).to_dict()[u'timestamp']
  print('Latest entry: %s' % latest_entry_timestamp)
except StopIteration:
  latest_entry_timestamp = None
  print('No entries found.')


with open(log_file, 'r') as log:
  batch = db.batch()
  batch_count = 0
  commit_count = 0
  line_count = 0
  while True:
    log_line = log.readline()
    line_count = line_count + 1
    if not log_line: # Could be a blank line, could be EOF... friggen python.
      break
    try:
      if log_line.strip().startswith('#'):
        continue
      timestamp_str, state = log_line.split(',')
      timestamp = datetime.fromtimestamp(int(timestamp_str), tz=pytz.UTC)
      if latest_entry_timestamp and timestamp <= latest_entry_timestamp:
        continue
      new_logentry_ref = logentries.document()
      batch.set(new_logentry_ref, {
          'timestamp': timestamp,
          'state': state.strip(),
      })
      batch_count = batch_count + 1
      if batch_count == _BATCH_SIZE:
        batch_count = 0
        batch.commit()
        batch = db.batch()
        commit_count = commit_count + 1
    except:
      print('Error on line number %d: "%s"' % (line_count, log_line), file=sys.stderr)
      raise

batch.commit()
print('New latest entry: %s' % timestamp)
print('Added %d entries.' % ((commit_count * _BATCH_SIZE) + batch_count))
print('Parsed %d lines.' % line_count)
