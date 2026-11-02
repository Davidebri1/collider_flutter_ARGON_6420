@echo off
rem Made by Claude (2026-10-21). The panes changed for the phone, on an iPhone 16 Pro screen. Usage: phone_tour3.cmd <port>
set P=%1
node drive_app.mjs %P% "[[\"click\",277,833],[\"wait\",1000],[\"click\",321,365],[\"wait\",3000],[\"shot\",\"q_files\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",277,833],[\"wait\",1000],[\"click\",241,474],[\"wait\",3000],[\"shot\",\"q_music\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",277,833],[\"wait\",1000],[\"click\",241,365],[\"wait\",4500],[\"shot\",\"q_documents\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",277,833],[\"wait\",1000],[\"click\",321,474],[\"wait\",7000],[\"shot\",\"q_browser\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",31,718],[\"wait\",2500],[\"shot\",\"q_history\"]]" >> tour_log.txt 2>&1
echo TOUR3 DONE >> tour_log.txt
