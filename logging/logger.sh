#!/bin/bash

cd $(dirname $0)/..
source env/bin/activate
python logging/logger.py data/log.csv
