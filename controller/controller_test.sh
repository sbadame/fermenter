#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
die() { echo -e "${RED}${test_dir}: $*${NC}" 1>&2 ; exit 1; }

cd $(dirname $0)/..

echo "Test cooling"
test_dir=$(mktemp -d)
cat << EOF > "${test_dir}/config.json"
{
  "realtime_log": "${test_dir}/realtime_log.csv",
 
  "monitor_thermometer": "blue",
  "controller_state": "${test_dir}/controller_state.json",
  "desired_temp_celsius": 10,
  "threshold_degrees_celsius": 3,

  "gpio_path": "/bin/echo",
  "control_every_n_seconds": -1
}
EOF
cat << EOF > "${test_dir}/realtime_log.csv"
1541945869,blue,OK,16.5
1541945869,yellow,OK,17.3
1541945869,white,OK,16.9
EOF

output=$(python3.5 controller/controller.py "${test_dir}/config.json")
(echo "${output}" | grep -q 'mode GPIO. 0 out') || die 'FAIL'
rm -r "${test_dir}"

echo "Test heating"
test_dir=$(mktemp -d)
cat << EOF > "${test_dir}/config.json"
{
  "realtime_log": "${test_dir}/realtime_log.csv",
  "monitor_thermometer": "blue",
  "controller_state": "${test_dir}/controller_state.json",
  "desired_temp_celsius": 10,
  "threshold_degrees_celsius": 3,
  "gpio_path": "/bin/echo",
  "control_every_n_seconds": -1
}
EOF
cat << EOF > "${test_dir}/realtime_log.csv"
1541945869,blue,OK,1
1541945869,yellow,OK,17.3
1541945869,white,OK,16.9
EOF

output=$(python3.5 controller/controller.py "${test_dir}/config.json")
(echo "${output}" | grep -q 'mode GPIO. 0 out') || die 'FAIL'
(cat "${test_dir}/controller_state.json" | jq -r '.state' | grep -q 'off') || die 'Bad state file'
rm -r "${test_dir}"

echo -e "${GREEN}PASS${NC}"
