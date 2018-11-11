#!/bin/bash

while read -r line; do
  epoch=$(echo $line | cut -f1 -d',');
  d=$(date -d @"$epoch");
  echo $line | sed "s/${epoch}/${d}/";
done
