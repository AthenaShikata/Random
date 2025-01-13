#!/bin/bash
# cd /phone-location
current_year=`date +"%Y"`
current_month=`date +"%m"`
echo ${current_year}
echo ${current_month}
month1=$((current_month-2))
month2=$((current_month-1))
echo $month1
echo $month2
folder1="$current_year$month1"
echo $folder1
folder2="$current_year$month2"
echo $folder2

#x=3; y=$((x+2)); echo $y
