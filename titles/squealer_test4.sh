convert -size 960x90 xc:transparent \
    -font "font/squealer/squealer.ttf" -pointsize 65 \
    \( -stroke black -strokewidth 3 -fill black -gravity center -draw "text 4,4 'CIBBL Standings • Year 5 Summer'" \) \
    -channel a -evaluate multiply 0.85 +channel \
    -compose over -fill "#F9A51E" \
    -stroke "#63110f" -gravity center -strokewidth 3 -draw "text 0,0 'CIBBL Standings • Year 5 Summer'" \
    -compose over -fill "#F9A51E" \
    -stroke "#63110f" -gravity center -strokewidth 3 -draw "text 0,0 'CIBBL Standings • Year 5 Summer'" \
    +repage \
    -filter lanczos -distort SRT "0,0 1 0 -0.5,-0.7" \
    \( -compose over -stroke none -gravity center -draw "text 0,0 'CIBBL Standings • Year 5 Summer'" \) \
    output.png