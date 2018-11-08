#!/bin/bash
set -e # quit after the first error

cd $(dirname $0)/..
source env/bin/activate
exec python upload/uploader.py data/certs/uploader.json data/log.csv
