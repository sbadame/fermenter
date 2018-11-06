#/bin/bash

systemctl --user status fermenter-logging
grep "" /dev/null data/config.json
./list_therms.sh --all
tail ~/logs/upload.sh.log
echo "Latest time in data/log.csv: $(date -d @$(tail -n1 data/log.csv | cut -d',' -f1) '+%F %X')" 
