@echo off
rem Made by Claude (2026-10-21). Round 19d: Discover edge to edge, the grouped picture actions, the 2-by-2 results. Usage: phone_tour8.cmd <port>
set P=%1
echo TOUR8 > tour8_log.txt
node drive_app.mjs %P% "[[\"click\",276,832],[\"wait\",1000],[\"click\",161,365],[\"wait\",6000],[\"shot\",\"r19d_discover\"],[\"click\",150,300],[\"wait\",2500],[\"shot\",\"r19d_viewer\"]]" >> tour8_log.txt 2>&1
node drive_app.mjs %P% "[[\"click\",276,832],[\"wait\",1000],[\"click\",161,365],[\"wait\",5000],[\"click\",230,750],[\"wait\",500],[\"type\",\"a red bicycle by a canal\"],[\"wait\",300],[\"click\",358,750],[\"wait\",90000],[\"shot\",\"r19d_made\"],[\"click\",321,560],[\"wait\",1500],[\"shot\",\"r19d_expanded\"]]" >> tour8_log.txt 2>&1
echo TOUR8 DONE >> tour8_log.txt
