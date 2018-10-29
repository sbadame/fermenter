#!/usr/bin/env python

import json
import sys
import pytz

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
def fire_set(fire_path, file_path):
  content = open(file_path, 'r').read()
  json_content= json.loads(content)
  db.document(fire_path).set(json_content)


OPTIONS = {
  'set': fire_set
}
OPTIONS[args[0]](*args[1:])
