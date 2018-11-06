#/bin/bash

systemctl --user status fermenter-logging
grep "" /dev/null data/config.json
./list_therms.sh --all
tail ~/logs/upload.sh.log
