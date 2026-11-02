@echo off
rem Made by Claude (2026-10-21). The smallest phone (iPhone SE, 375 x 667). Usage: phone_tour_se.cmd <port>
set P=%1
set PHONE=375x667
node drive_app.mjs %P% "[[\"click\",263,625],[\"wait\",1000],[\"click\",307,262],[\"wait\",3000],[\"shot\",\"se_files\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",263,625],[\"wait\",1000],[\"click\",307,370],[\"wait\",7000],[\"shot\",\"se_browser\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",263,625],[\"wait\",1000],[\"click\",147,262],[\"wait\",3500],[\"shot\",\"se_market\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",263,625],[\"wait\",1000],[\"click\",147,370],[\"wait\",3500],[\"shot\",\"se_premium\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",263,625],[\"wait\",1000],[\"click\",67,262],[\"wait\",3000],[\"shot\",\"se_smartgen\"]]" >> tour_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",263,625],[\"wait\",1000],[\"click\",227,262],[\"wait\",4500],[\"shot\",\"se_documents\"]]" >> tour_log.txt 2>&1
echo TOURSE DONE >> tour_log.txt
