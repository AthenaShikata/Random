#!/bin/bash
recup_dir="${1%/}"
dest_dir="${2%/}"

cd "$recup_dir"

sortFiles () {
  mkdir -vp "$dest_dir"/"${ext}"
  cp -vi "$filename" "$dest_dir"/"${ext}"/"$filename2"
}


existTest () {
  dupenum=0
  while [ $exists = true ]
  do
    if [ -f "$dest_dir"/"${ext}"/"$filename2" ]; then
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
        existTest
        sortFiles
      fi
    done
    cd ..
    echo ""
  fi
done
echo "complete"