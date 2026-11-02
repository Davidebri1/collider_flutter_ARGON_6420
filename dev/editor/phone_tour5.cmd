@echo off
rem Made by Claude (2026-10-21). Round 19: the new Discover, its picture view, Premium's dim, the browser's sidebar, Files. Usage: phone_tour5.cmd <port>
set P=%1
echo TOUR5 > tour5_log.txt
node drive_app.mjs %P% "[[\"click\",276,832],[\"wait\",1000],[\"click\",161,365],[\"wait\",5000],[\"shot\",\"r19_discover\"],[\"click\",150,200],[\"wait\",2500],[\"shot\",\"r19_viewer\"]]" >> tour5_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",276,832],[\"wait\",1000],[\"click\",161,474],[\"wait\",6000],[\"shot\",\"r19_premium\"]]" >> tour5_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",276,832],[\"wait\",1000],[\"click\",321,474],[\"wait\",5000],[\"shot\",\"r19_browser\"]]" >> tour5_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",276,832],[\"wait\",1000],[\"click\",321,365],[\"wait\",4000],[\"shot\",\"r19_files\"]]" >> tour5_log.txt 2>&1
echo TOUR5 DONE >> tour5_log.txt
