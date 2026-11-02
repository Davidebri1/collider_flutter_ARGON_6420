@echo off
rem Made by Claude (2026-10-21). The chat side of the app on a phone screen. Usage: phone_tour2.cmd <port> [prefix]
set P=%1
set X=%2
if "%X%"=="" set X=p
node drive_app.mjs %P% "[[\"click\",31,672],[\"wait\",2500],[\"shot\",\"%X%_newchat\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",31,718],[\"wait\",2500],[\"shot\",\"%X%_history\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",31,764],[\"wait\",2500],[\"shot\",\"%X%_models\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",125,833],[\"wait\",1500],[\"click\",200,787],[\"type\",\"What is the tallest lighthouse in Florida?\"],[\"key\",\"Enter\"],[\"wait\",20000],[\"shot\",\"%X%_answer\"]]" >> tour_log.txt 2>&1
echo TOUR2 DONE >> tour_log.txt
