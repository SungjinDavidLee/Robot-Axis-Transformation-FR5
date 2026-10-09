#!/usr/bin/env bash
# 학습 종료 후 실행. GPU1에 B0 / C1-6k / C1-12k 정책 서버를 띄운다.
O=$HOME/lerobot/outputs
[ -d $O/fr5_fr3_task6_v1/checkpoints/012000 ] || { echo "12000 체크포인트 없음 — 학습 종료 후 실행"; exit 1; }
cd ~/lerobot
start() {  # 이름 포트 체크포인트 데이터셋
  CUDA_VISIBLE_DEVICES=1 PORT=$2 CKPT=$3 REPO=$4 nohup ./.venv/bin/python $HOME/fr5_policy_server.py > ~/policy_server_$1.log 2>&1 &
  echo "$1  port $2  pid $!"
}
start b0     8200 $O/fr5_task6_abs/checkpoints/006000/pretrained_model     local/fr5_task6_abs
start c1_6k  8201 $O/fr5_fr3_task6_v1/checkpoints/006000/pretrained_model  local/fr5_fr3_task6_v1
start c1_12k 8202 $O/fr5_fr3_task6_v1/checkpoints/012000/pretrained_model  local/fr5_fr3_task6_v1
# 확인: for p in 8200 8201 8202; do curl -s http://127.0.0.1:$p/info; echo; done
