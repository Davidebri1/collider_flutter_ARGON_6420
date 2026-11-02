@echo off
rem Made by Claude (2026-10-21). Round 19e: Discover's head over the pictures; the pictures' toolbar whole on a phone. Usage: phone_tour9.cmd <port>
set P=%1
echo TOUR9 > tour9_log.txt
node drive_app.mjs %P% "[[\"click\",276,832],[\"wait\",1000],[\"click\",161,365],[\"wait\",6000],[\"shot\",\"r19e_discover\"]]" >> tour9_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",276,832],[\"wait\",1000],[\"click\",161,365],[\"wait\",5000],[\"click\",230,750],[\"wait\",500],[\"type\",\"a paper boat on a pond\"],[\"wait\",300],[\"click\",358,750],[\"wait\",100000],[\"shot\",\"r19e_made\"]]" >> tour9_log.txt 2>&1
echo TOUR9 DONE >> tour9_log.txt
