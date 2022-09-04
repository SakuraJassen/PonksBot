#!/bin/bash
cd "${0%/*}"
if ! pgrep -f main.py ;
then
  git reset --hard origin/master
  git pull
#git --git-dir=/home/pi/PonksBot/.git pull --force
  nohup python main.py > botlog.out
fi
