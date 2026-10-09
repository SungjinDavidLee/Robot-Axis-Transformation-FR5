#!/usr/bin/env bash
# aggregate_datasets 는 robot_type 이 같아야 합친다. 정합 사본만 fairino_fr5 로 바꾼다 (원본 FR3 데이터는 그대로).
D=/home/data/fr_transfer/data/fr3_task6_aligned_v1
sed -i 's/"robot_type": "franka_fr3"/"robot_type": "fairino_fr5"/' $D/meta/info.json && grep -n robot_type $D/meta/info.json
echo "source: task6_franka_v5 (FR3). z -0.0192 m, tool-frame rotation offset 80.4 deg, action recomputed. robot_type set to fairino_fr5 for aggregation only." > $D/ALIGNMENT_NOTE.txt
# 학습 서버로 전송
# rsync -av /home/data/fr_transfer/data/fr3_task6_aligned_v1 SERVER_USER@TRAIN_SERVER_IP:~/.cache/huggingface/lerobot/local/
