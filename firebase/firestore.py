#!/usr/bin/env python

import gzip
import json
import pytz
import sys

import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

# First element is the script
args = sys.argv[1:]
cert_file = args.pop(0)

# Use a service account
cred = credentials.Certificate(cert_file)
firebase_admin.initialize_app(cred)

db = firestore.client()

# I would call this 'set', but that's reserved...
def fire_set(fire_path, file_path, gzip_flag=''):
  file_content = open(file_path, 'r').read()
  content = ''
  if gzip_flag == '--gzip':
    compressed = gzip.compress(file_content.encode())
    content = {'gzipped': compressed}
  else:
    content = json.loads(file_content)
  db.document(fire_path).set(content)

def fire_get(fire_path, file_path):
  data = db.document(fire_path).get().to_dict()
  print(len(data['gzipped']))
  with open(file_path, 'w') as f:
    f.write(json.dumps(data))


OPTIONS = {
  'set': fire_set,
  'get': fire_get,
}
OPTIONS[args[0]](*args[1:])
