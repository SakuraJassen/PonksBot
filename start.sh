#!/bin/bash
if pgrep -f main.py 
then
  git --git-dir=/home/pi/PonksBot/.git pull --force
  nohup python /home/pi/PonksBot/main.py > /home/pi/PonksBot/botlog.out
fi
