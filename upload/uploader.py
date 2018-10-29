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
_THERM_NAME = {
  'blue': 'In water',
  'yellow': 'In fridge',
  'white': 'Garage',
}

# Use a service account
cred = credentials.Certificate(cert_file)
firebase_admin.initialize_app(cred)

db = firestore.client()
logentries = db.collection(u'logentries')

latest_entry_timestamp = next(logentries.order_by(u'timestamp', direction=firestore.Query.DESCENDING).limit(1).get()).to_dict()[u'timestamp']

print('Latest entry: %s' % latest_entry_timestamp)

with open(log_file, 'r') as log:
  first_line = log.readline()

  batch = db.batch()
  batch_count = 0
  commit_count = 0
  line_count = 0
  while True:
    log_line = log.readline()
    line_count = line_count + 1
    if not log_line:
      break
    try:
      timestamp_str, therm_name, status, celsius = log_line.split(',')
      timestamp = datetime.fromtimestamp(int(timestamp_str), tz=pytz.UTC)
      if timestamp <= latest_entry_timestamp:
        continue
      new_logentry_ref = logentries.document()
      batch.set(new_logentry_ref, {
          'timestamp': timestamp,
          'thermometer_name': _THERM_NAME[therm_name],
          'status': status,
          'temperature_celsius': float(celsius),
      })
      batch_count = batch_count + 1
      if batch_count == _BATCH_SIZE:
        batch_count = 0
        batch.commit()
        batch = db.batch()
        commit_count = commit_count + 1
    except:
      print('Error on line: %d' % line_count, file=sys.stderr)
      raise

batch.commit()
print('New latest entry: %s' % timestamp)
print('Added %d entries.' % ((commit_count * _BATCH_SIZE) + batch_count))

# There is a firebase function that is trigged on writes to /ui/upload.last_upload
db.document(u'ui/upload').set({u'last_upload': datetime.now()})
