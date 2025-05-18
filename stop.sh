#!/bin/bash

# 停止由 start.sh 启动的进程
if [ -f pid.txt ]; then
    PID=$(cat pid.txt)
    if kill -0 $PID > /dev/null 2>&1; then
        kill $PID
        echo "已停止进程 $PID"
    else
        echo "进程 $PID 不存在，可能已停止"
    fi
    rm pid.txt
else
    echo "pid.txt 不存在 - 服务可能未启动"
fi
