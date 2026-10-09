#!/usr/bin/env bash
# 학습 서버: 합치기 도구 시그니처·검증 규칙과 GPU 상태
AG=~/lerobot/src/lerobot/datasets/aggregate.py
echo "== aggregate_datasets 시그니처"; sed -n '352,375p' "$AG"
echo "== 메타데이터 검증 규칙"; grep -n "def validate_all_metadata" -A 25 "$AG" | head -35
echo "== GPU"; nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv
echo "== GPU uuid ↔ index"; nvidia-smi --query-gpu=index,uuid --format=csv,noheader
echo "== GPU 사용 프로세스 (pid | 메모리 | 사용자 | 명령)"
nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader | while IFS=, read -r g p m; do
  p=${p// /}; echo "$g | $p |$m | $(ps -o user= -p "$p") | $(ps -o args= -p "$p" | cut -c1-120)"; done
echo "== 서버 IP"; hostname -I
echo "== lerobot-train 위치"; ls ~/lerobot/.venv/bin/lerobot-train 2>/dev/null || which lerobot-train
