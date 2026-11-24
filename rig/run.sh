#!/bin/sh
# Runs on the experiment server from /root/exp. One status field, one writer.
# SETTING_UP -> RUNNING -> DONE, or SETUP_FAILED / RUN_FAILED. Safe to start twice: a DONE run is not redone.
cd /root/exp
st() { echo "$1" > STATUS; }
[ "$(cat STATUS 2>/dev/null)" = "DONE" ] && exit 0
st SETTING_UP
{ lscpu | grep -E 'Model name|^CPU\(s\)'; free -m | sed -n 2p; . /etc/os-release; echo "$PRETTY_NAME"; uname -r; } > hardware.txt 2>&1
sh setup.sh > setup.log 2>&1 || { st SETUP_FAILED; exit 1; }
st RUNNING
sh bench.sh > run.log 2>&1 || { st RUN_FAILED; exit 1; }
st DONE
