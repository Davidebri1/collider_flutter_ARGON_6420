@echo off
rem Made by Claude (2026-10-21). Smallest phone again after the fixes, then the largest phone's apps. Usage: phone_tour4.cmd <port>
set P=%1
set PHONE=375x667
node drive_app.mjs %P% "[[\"click\",263,625],[\"wait\",1000],[\"click\",307,262],[\"wait\",3000],[\"shot\",\"se2_files\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",263,625],[\"wait\",1000],[\"click\",67,262],[\"wait\",3000],[\"shot\",\"se2_smartgen\"]]" >> tour_log.txt 2>&1
set PHONE=440x956
node drive_app.mjs %P% "[[\"click\",296,914],[\"wait\",1200],[\"shot\",\"max_apps\"]]" >> tour_log.txt 2>&1
echo TOUR4 DONE >> tour_log.txt
