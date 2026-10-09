#!/usr/bin/env bash
# C1 서버의 ref_axis_angle 이 null 로 나온 문제 수정: 서버는 REPO 폴더의 norm_stats.json 에서 이 값만 읽는다.
# aggregate 가 이 파일을 복사하지 않으므로 FR5 의 파일을 복사하고 C1 서버 두 개를 다시 띄운다.
# (pid 3854760 3854761 은 당시 값 — 다시 쓸 때는 바꿀 것)
L=~/.cache/huggingface/lerobot/local
cp -n $L/fr5_task6_abs/norm_stats.json $L/fr5_fr3_task6_v1/norm_stats.json && echo "norm_stats.json 복사 완료"
kill 3854760 3854761; sleep 5
O=$HOME/lerobot/outputs
cd ~/lerobot
for a in "c1_6k 8201 006000" "c1_12k 8202 012000"; do
  set -- $a
  CUDA_VISIBLE_DEVICES=1 PORT=$2 CKPT=$O/fr5_fr3_task6_v1/checkpoints/$3/pretrained_model REPO=local/fr5_fr3_task6_v1 \
    nohup ./.venv/bin/python $HOME/fr5_policy_server.py > ~/policy_server_$1.log 2>&1 &
  echo "$1  port $2  pid $!"
done
