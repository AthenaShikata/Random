#!/bin/bash

shopt -s nullglob
for file in *.mkv; do
    # Extract season number (optional)
    season=$(echo "$file" | grep -oP 'Season\s*\K[0-9]+')
    if [[ -z "$season" ]]; then
        season=1
    fi

    # Extract episode number
    episode=$(echo "$file" | grep -oP '_-\K[0-9]+(?=_)')

    if [[ -z "$episode" ]]; then
        echo "Skipping '$file': episode number not found"
        continue
    fi

    season_padded=$(printf "%02d" "$season")
    episode_padded=$(printf "%02d" "$episode")
    code="S${season_padded}E${episode_padded}"

    echo "Processing '$file' -> '${code}.mkv'"

    ffmpeg -i "$file" \
        -map 0:v:0 \
        -map 0:a:1 -map 0:a:0 -map 0:a:2 \
        -map 0:s:1 -map 0:s:0 -map 0:s:2 -map 0:s:3 \
        -c:s copy \
        -disposition:a:0 default \
        -disposition:a:1 0 \
        -disposition:a:2 0 \
        -disposition:s:0 default \
        -disposition:s:1 0 \
        -disposition:s:2 0 \
        -disposition:s:3 0 \
        "${code}.mkv"
done
