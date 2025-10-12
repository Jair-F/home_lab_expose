#!/bin/bash
URL=$1
wget -O /dev/null $URL 2> /dev/null
STATUS_CODE=$?

if [[ $STATUS_CODE -eq 0 ]]
then
    echo "site is up"
    exit 0
else
    echo "site is down"
    exit $STATUS_CODE
fi
