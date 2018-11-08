#!/bin/bash

set -e # quit after the first error

cd $(dirname $0)/..
exec python3.5 logging/logger.py data/config.json data/log.csv
