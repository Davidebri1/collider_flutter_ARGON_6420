@echo off
rem Made by Claude (2026-10-21). Round 19b: Discover after the memory fix, its picture view, and the box at its foot. Usage: phone_tour6.cmd <port>
set P=%1
echo TOUR6 > tour6_log.txt
node drive_app.mjs %P% "[[\"click\",276,832],[\"wait\",1000],[\"click\",161,365],[\"wait\",6000],[\"shot\",\"r19b_discover\"],[\"swipe\",250,600,250,150],[\"wait\",1500],[\"shot\",\"r19b_discover_scrolled\"],[\"click\",150,300],[\"wait\",2500],[\"shot\",\"r19b_viewer\"]]" >> tour6_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",276,832],[\"wait\",1000],[\"click\",161,365],[\"wait\",5000],[\"click\",200,750],[\"wait\",500],[\"type\",\"a lighthouse at dusk\"],[\"wait\",300],[\"click\",358,750],[\"wait\",4000],[\"shot\",\"r19b_sent\"],[\"wait\",20000],[\"shot\",\"r19b_sent_later\"]]" >> tour6_log.txt 2>&1
echo TOUR6 DONE >> tour6_log.txt
