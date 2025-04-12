#!/bin/bash

# 查找运行 /usr/bin/python3.11 -m main 的进程
pids=$(ps aux | grep '/usr/bin/python3.11 -m main' | grep -v grep | awk '{print $2}')

# 如果找到进程，则终止它们
if [ -n "$pids" ]; then
    echo "找到以下运行 /usr/bin/python3.11 -m main 的进程，将终止它们："
    echo "$pids"
    kill -9 $pids
    echo "进程已终止。"
else
    echo "未找到运行 /usr/bin/python3.11 -m main 的进程。"
fi