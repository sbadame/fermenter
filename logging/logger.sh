#!/bin/bash

set -e # quit after the first error

cd $(dirname $0)/..
source env/bin/activate
exec python logging/logger.py data/log.csv
