#!/bin/bash

#Created by AthenaShikata under CC-BY-SA

#required args
subext_lim=$(( "${1%/}"-1 ))
recup_dir="${2%/}"
dest_dir="${3%/}"

#optional args
xExt="${4%/}"

mkdir -vp "$dest_dir"
cd "$recup_dir"

sortFiles () {
  if [ "${ext}" == "$filename" ]; then
    ext=__noExtension
  fi
  mkdir -vp "$dest_dir"/"${ext}"
  subext=$(( $(ls -l "$dest_dir"/"${ext}" | wc -l)-1 ))
  if [ $subext -le 0 ]; then
    subext=1
  fi
  mkdir -vp "$dest_dir"/"${ext}"/"${subext}"
  filecount=$(( $(ls -l "$dest_dir"/"${ext}"/"$subext" | wc -l)-1 ))
  if [[ $filecount -gt $subext_lim ]]; then
    subext="$(( subext+1 ))"
    mkdir -vp "$dest_dir"/"${ext}"/"${subext}"
  fi
}

existTest () {
  dupenum=0
  while [ $exists = true ]
  do
    if [ -f "$dest_dir"/"${ext}"/"$subext"/"$filename2" ]; then
      exists=true
      dupenum=$((dupenum + 1))
      filename2="$base""(""$dupenum"").""$ext"
    else
      exists=false
    fi
  done
}

for directory in *; do
  if [[ -d "$directory" ]]; then
    cd "$directory" 
    echo "directory" "$directory" 
    for filename in *; do
      if [[ -f "$filename" ]]; then
        base="${filename%.*}"
        ext="${filename#$base.}"
        filename2=$filename
        exists=true
        if [ -z "$xExt" ]; then
          sortFiles
          existTest
          cp -vi "$filename" "$dest_dir"/"${ext}"/"$subext"/"$filename2"
        elif [ $xExt == $ext ]; then
          sortFiles
          existTest
          cp -vi "$filename" "$dest_dir"/"${ext}"/"$subext"/"$filename2"
        fi
      fi
    done
    echo ""
  fi
done
echo "complete"