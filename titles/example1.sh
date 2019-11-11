convert -background none -pointsize 50 -strokewidth 6 \
   -stroke \#00000040 -fill black label:"THIS IS A TEST" \
   -stroke none -fill white label:"THIS IS A TEST" -compose dstout -composite \
   -fill \#FF000080 label:"THIS IS A TEST" -compose over -composite output.png