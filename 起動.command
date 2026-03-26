#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate

# サーバーをバックグラウンドで起動
python3 run_server.py &
SERVER_PID=$!

# サーバーが起動するまで待つ（最大10秒）
for i in $(seq 1 20); do
  sleep 0.5
  if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    break
  fi
done

# ブラウザを開く
open http://localhost:8000

# サーバーが終了するまで待つ
wait $SERVER_PID
