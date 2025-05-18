#!/bin/bash

# 启动 main.py 并记录 PID
nohup /home/koril/project/python/badminton/.venv/bin/python main.py > /dev/null 2>&1 &
echo $! > pid.txt

echo "服务已启动，进程ID: $(cat pid.txt)"
