#!/bin/bash

cd /root/empirical/engines/TopSeed || exit

# -------- DIFF --------
for i in {5..5}; do
    SESSION="DI$i"
    echo "Starting DIFF screen session: $SESSION"
    screen -dmS "$SESSION" bash -c "python3 topseed.py program_configs/diff.json 86400 $i --eta_time=120"
done

# -------- FIND --------
for i in {5..5}; do
    SESSION="FI$i"
    echo "Starting FIND screen session: $SESSION"
    screen -dmS "$SESSION" bash -c "python3 topseed.py program_configs/find.json 86400 $i --eta_time=120"
done

# -------- GAWK --------
for i in {5..5}; do
    SESSION="GA$i"
    echo "Starting GAWK screen session: $SESSION"
    screen -dmS "$SESSION" bash -c "python3 topseed.py program_configs/gawk.json 86400 $i --eta_time=120"
done

# -------- GCAL --------
for i in {5..5}; do
    SESSION="GL$i"
    echo "Starting GCAL screen session: $SESSION"
    screen -dmS "$SESSION" bash -c "python3 topseed.py program_configs/gcal.json 86400 $i --eta_time=120"
done

# -------- GREP --------
for i in {5..5}; do
    SESSION="GR$i"
    echo "Starting GREP screen session: $SESSION"
    screen -dmS "$SESSION" bash -c "python3 topseed.py program_configs/grep.json 86400 $i --eta_time=120"
done

# -------- M4 --------
for i in {5..5}; do
    SESSION="MF$i"
    echo "Starting M4 screen session: $SESSION"
    screen -dmS "$SESSION" bash -c "python3 topseed.py program_configs/m4.json 86400 $i --eta_time=120"
done

# -------- SED --------
for i in {5..5}; do
    SESSION="SE$i"
    echo "Starting SED screen session: $SESSION"
    screen -dmS "$SESSION" bash -c "python3 topseed.py program_configs/sed.json 86400 $i --eta_time=120"
done

# -------- SQLITE3 --------
for i in {5..5}; do
    SESSION="SQ$i"
    echo "Starting FIND screen session: $SESSION"
    screen -dmS "$SESSION" bash -c "python3 topseed.py program_configs/sqlite.json 86400 $i --eta_time=120"
done

echo "All increase screen sessions for running TopSeed started and detached."
