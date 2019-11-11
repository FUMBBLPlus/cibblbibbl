#!/bin/bash

filename="output.png"

if [ "$2" != "" ]; then
    filename=$2
fi

convert -size 960x90 xc:transparent \
    -font "font/squealer/squealer.ttf" -pointsize 65 \
    -stroke black -strokewidth 3 -fill black -gravity center \
    -draw "text 3,3 '$1'" \
    -channel a -evaluate multiply 0.85 +channel \
    -compose over -fill "#F9A51E" \
    -stroke "#63110f" -gravity center -strokewidth 3 \
    -draw "text 0,0 '$1'" \
    -compose over -stroke none -gravity center \
    -draw "text 0.5,0.7 '$1'" \
    $filename