#!/bin/bash

set -e # quit after the first error

cd $(dirname $0)/..
exec python3.5 controller/controller.py data/config.json
