#!/bin/bash

cd $(dirname $0)/..
source env/bin/activate
python upload/uploader.py data/certs/uploader.json data/log.csv
python upload/controller_uploader.py data/certs/uploader.json data/controller_state.log
