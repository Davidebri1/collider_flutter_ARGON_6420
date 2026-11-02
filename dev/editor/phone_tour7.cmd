@echo off
rem Made by Claude (2026-10-21). Round 19c: words typed in Discover, made into pictures in the media chat. Usage: phone_tour7.cmd <port>
set P=%1
echo TOUR7 > tour7_log.txt
node drive_app.mjs %P% "[[\"click\",276,832],[\"wait\",1000],[\"click\",161,365],[\"wait\",5000],[\"click\",200,750],[\"wait\",500],[\"type\",\"a lighthouse at dusk\"],[\"wait\",300],[\"click\",358,750],[\"wait\",3000],[\"shot\",\"r19c_sent\"],[\"wait\",80000],[\"shot\",\"r19c_made\"],[\"click\",92,668],[\"wait\",2500],[\"shot\",\"r19c_viewer\"]]" >> tour7_log.txt 2>&1
echo TOUR7 DONE >> tour7_log.txt
