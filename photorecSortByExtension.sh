#!/bin/bash

subext_lim=$(( "${1%/}"-1 ))
recup_dir="${2%/}"
dest_dir="${3%/}"

mkdir -vp "$dest_dir"
cd "$recup_dir"

sortFiles () {
  if [ -z "${ext}" ]; then
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
        sortFiles
        existTest
        cp -vi "$filename" "$dest_dir"/"${ext}"/"$subext"/"$filename2"
      fi
    done
    cd "$directory"
    cd ..
    echo ""
  fi
done
echo "complete"