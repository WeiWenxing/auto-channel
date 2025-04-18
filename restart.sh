#!/bin/bash

# 查找并杀死现有进程
echo "查找正在运行的 rss_bot.py 进程..."
PID=$(ps aux | grep rss_bot.py | grep -v grep | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "没有找到正在运行的 rss_bot.py 进程"
else
    echo "找到进程 PID: $PID, 正在杀死..."
    kill -9 $PID
    echo "进程已终止"
fi

# 等待一段时间，确保进程已经完全终止（可根据实际情况调整等待时间）
sleep 2

# 重新启动 rss_bot.py 并将输出重定向到日志文件
nohup python3 rss_bot.py > /tmp/rss-bot.log 2>&1 &

# 输出提示信息
echo "rss_bot.py 已重新启动，日志记录在 /tmp/rss-bot.log"
