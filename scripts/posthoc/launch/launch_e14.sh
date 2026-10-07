#!/bin/bash
# E14 launcher (docs/ECPF_E14_分類確認_預註冊.md): 48 cells, xargs -P 8, longest first.
# The launching PowerShell sets this shell to Idle during the sleep; every cell inherits Idle. No affinity changes.
cd /c/Users/chenp/Desktop/project/drift_detect || exit 1
sleep 5
LOG="/c/Users/chenp/AppData/Local/Temp/claude/C--Users-chenp-Desktop-project-drift-detect/2acc16a5-ce47-488d-9856-20a09761d8c9/scratchpad/e14_run.log"
date '+E14 start %F %T' > "$LOG"
xargs -P 8 -L 1 sh -c '"$0" -W ignore scripts/run_e1_e2.py --family "$1" --arm "$2" > "outputs/e1_e2/logs/$1-$2.log" 2>&1; rc=$?; echo "$(date +%T) $1 $2 exit=$rc" >> "'"$LOG"'"' /c/Users/chenp/anaconda3/python.exe < "/c/Users/chenp/AppData/Local/Temp/claude/C--Users-chenp-Desktop-project-drift-detect/2acc16a5-ce47-488d-9856-20a09761d8c9/scratchpad/e14_jobs.txt"
date '+E14 end %F %T' >> "$LOG"
