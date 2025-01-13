#!/bin/bash
echo "The current HTTP response for " $1 " is..."
response=$(curl --write-out "%{http_code}\n" --silent --output /dev/null "$1")
echo "${response}"
