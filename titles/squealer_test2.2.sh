convert -size 960x90 xc:transparent \
    -font "font/squealer/squealer.ttf" -pointsize 60 \
    \( \
    -fill black -strokewidth 3 -stroke black \
    -gravity center -annotate +3+3 'CIBBL Standings • Year 5 Summer' \
    \) \
    -channel a -evaluate multiply 0.8 +channel \
    -fill "#63110f" -strokewidth 3 -stroke "#63110f" \
    -gravity center -annotate +0+0 'CIBBL Standings • Year 5 Summer' \
    -fill "#F9A51E" -stroke none \
    -gravity center -annotate +1+1 'CIBBL Standings • Year 5 Summer' \
    output.png