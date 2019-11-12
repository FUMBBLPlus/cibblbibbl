#!/bin/bash

# https://stackoverflow.com/a/246128/2334951
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

filename="output.png"

if [ "$2" != "" ]; then
    filename=$2
fi

convert -size 960x90 xc:transparent \
    -font "$DIR/font/squealer/squealer.ttf" -pointsize 65 \
    -stroke black -strokewidth 3 -fill black -gravity center \
    -draw "text 3,3 '$1'" \
    -channel a -evaluate multiply 0.85 +channel \
    -compose over -fill "#F9A51E" \
    -stroke "#63110f" -gravity center -strokewidth 3 \
    -draw "text 0,0 '$1'" \
    -compose over -stroke none -gravity center \
    -draw "text 0.5,0.7 '$1'" \
    $filename