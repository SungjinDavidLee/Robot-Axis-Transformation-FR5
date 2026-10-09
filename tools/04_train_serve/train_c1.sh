#!/usr/bin/env bash
# 학습 서버: B0 학습 설정 그대로, 데이터셋·출력·스텝만 바꿔 C1 을 학습한다 (GPU1 고정, 백그라운드)
cd ~/lerobot
CUDA_VISIBLE_DEVICES=1 nohup ./.venv/bin/lerobot-train \
  --config_path=outputs/fr5_task6_abs/checkpoints/006000/pretrained_model/train_config.json \
  --dataset.repo_id=local/fr5_fr3_task6_v1 \
  --output_dir=outputs/fr5_fr3_task6_v1 \
  --job_name=fr5_fr3_task6_v1 \
  --steps=12000 --save_freq=6000 \
  > outputs/fr5_fr3_task6_v1.log 2>&1 &
echo "started pid $!"
