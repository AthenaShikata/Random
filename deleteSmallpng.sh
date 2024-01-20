#!/bin/bash

#Created by AthenaShikata under CC-BY-SA

#required args
sizes=("8 x 8" "16 x 16" "32 x 32" "48 x 48" "64 x 64" "128 x 128" "256 x 256" "512 x 512" "64 x 32" "128 x 64" "64 x 128" "24 x 48" "128 x 256" "512 x 256" "256 x 128" "192 x 256" "192 x 128" "64 x 512" "64 x 1024" "128 x 1024" "128 x 2048" "64 x 4096" "512 x 256" "1024 x 1024" "1024 x 512")
countDel=0

for directory in *; do
  if [[ -d "$directory" ]]; then
    cd "$directory" 
    echo "directory" "$directory" 
    for t in ${!sizes[@]}; do
      search=" "${sizes[$t]}","
      for filename in *; do
        if [[ -f "$filename" ]]; then
          if file $filename | grep -q "$search" ; then
            file $filename
            echo $directory ${sizes[$t]}
            sudo rm -v $filename
            countDel=$((countDel+1))
            echo $countDel
          fi
        fi
      done
    done
  fi
  cd ..
done
echo ""
echo $countDel
echo "complete"