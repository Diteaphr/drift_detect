#!/bin/bash
# D3 launcher (docs/ECPF_D3_主方法與參照過時_開發檢查.md): 8 cells.
# The launching PowerShell sets this shell to Idle during the sleep; every cell inherits Idle. No affinity changes.
cd /c/Users/chenp/Desktop/project/drift_detect || exit 1
sleep 5
LOG="/c/Users/chenp/AppData/Local/Temp/claude/C--Users-chenp-Desktop-project-drift-detect/2acc16a5-ce47-488d-9856-20a09761d8c9/scratchpad/d3_run.log"
date '+D3 start %F %T' > "$LOG"
xargs -P 8 -L 1 sh -c '"$0" -W ignore scripts/run_e1_e2.py --family "$1" --arm "$2" > "outputs/e1_e2/logs/$1-$2.log" 2>&1; rc=$?; echo "$(date +%T) $1 $2 exit=$rc" >> "'"$LOG"'"' /c/Users/chenp/anaconda3/python.exe < "/c/Users/chenp/AppData/Local/Temp/claude/C--Users-chenp-Desktop-project-drift-detect/2acc16a5-ce47-488d-9856-20a09761d8c9/scratchpad/d3_jobs.txt"
date '+D3 end %F %T' >> "$LOG"
