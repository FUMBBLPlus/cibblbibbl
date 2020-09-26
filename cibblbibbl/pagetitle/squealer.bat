@echo off
setlocal

rem https://ss64.com/nt/syntax-dequote.html

rem https://stackoverflow.com/a/54731058/2334951
set batdir=%~dp0

set filename="output.png"

IF NOT "%2"=="" goto have_2_args
:back_from_have_2_args

magick convert -size 960x90 xc:transparent^
    -font "%batdir%\font\squealer\squealer.ttf" -pointsize 65^
    -stroke black -strokewidth 3 -fill black -gravity center^
    -draw "text 3,3 '%~1'"^
    -channel a -evaluate multiply 0.85 +channel^
    -compose over -fill "#F9A51E"^
    -stroke "#63110f" -gravity center -strokewidth 3^
    -draw "text 0,0 '%~1'"^
    -compose over -stroke none -gravity center^
    -draw "text 0.5,0.7 '%~1'"^
    -depth 8 %filename%

goto end

:have_2_args
set filename="%~2"
goto back_from_have_2_args

:end
endlocal
