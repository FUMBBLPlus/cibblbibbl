convert -size 960x90 xc:transparent \
    -font "font/squealer/squealer.ttf" -pointsize 66 \
    \( \
    -fill black -strokewidth 2 -stroke black \
    -gravity center -annotate +4+4 'CIBBL Standings • Year 5 Summer' \
    \) \
    -channel a -evaluate multiply 0.8 +channel \
    +repage
    -fill "#63110f" -strokewidth 2 -stroke "#63110f" \
    -gravity center -annotate +0+0 'CIBBL Standings • Year 5 Summer' \
    -fill "#F9A51E" -stroke none\
    -gravity center -annotate +1+1 'CIBBL Standings • Year 5 Summer' \
    output.png