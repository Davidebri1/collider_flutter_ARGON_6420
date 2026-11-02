@echo off
rem Made by Claude (2026-10-21). Every pane on a phone screen, one after another. Usage: phone_tour.cmd <port> [prefix]
set P=%1
set X=%2
if "%X%"=="" set X=p
node drive_app.mjs %P% "[[\"click\",277,833],[\"wait\",1000],[\"click\",81,365],[\"wait\",3000],[\"shot\",\"%X%_smartgen\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",277,833],[\"wait\",1000],[\"click\",161,365],[\"wait\",3500],[\"shot\",\"%X%_market\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",277,833],[\"wait\",1000],[\"click\",241,365],[\"wait\",4500],[\"shot\",\"%X%_documents\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",277,833],[\"wait\",1000],[\"click\",321,365],[\"wait\",3000],[\"shot\",\"%X%_files\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",277,833],[\"wait\",1000],[\"click\",81,474],[\"wait\",3000],[\"shot\",\"%X%_gallery\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",277,833],[\"wait\",1000],[\"click\",161,474],[\"wait\",3500],[\"shot\",\"%X%_premium\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",277,833],[\"wait\",1000],[\"click\",241,474],[\"wait\",3000],[\"shot\",\"%X%_music\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",277,833],[\"wait\",1000],[\"click\",321,474],[\"wait\",6000],[\"shot\",\"%X%_browser\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",62,665],[\"wait\",2500],[\"shot\",\"%X%_newchat\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",62,718],[\"wait\",2500],[\"shot\",\"%X%_history\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",62,764],[\"wait\",2500],[\"shot\",\"%X%_models\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",125,833],[\"wait\",2000],[\"shot\",\"%X%_composer\"]]" >> tour_log.txt 2>&1
echo TOUR DONE >> tour_log.txt
