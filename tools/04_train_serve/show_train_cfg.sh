#!/usr/bin/env bash
# 학습 서버: B0 6000스텝 체크포인트의 학습 설정을 평탄하게 출력한다
CK=~/lerobot/outputs/fr5_task6_abs/checkpoints/006000/pretrained_model
echo "== 체크포인트 폴더"; ls "$CK"
echo "== 학습 설정 (wandb/eval/env 제외)"
python3 - "$CK/train_config.json" <<'PY' | grep -viE '^(wandb|eval|env)\.'
import json, sys
def walk(d, p=''):
    for k, v in d.items():
        if isinstance(v, dict): walk(v, f'{p}{k}.')
        else: print(f'{p}{k} = {v}')
walk(json.load(open(sys.argv[1])))
PY
echo "== 셸 기록의 학습 명령"; grep -nE 'lerobot-train|lerobot_train|train\.py|gr00t' ~/.bash_history | tail -15
echo "== 데이터셋 합치기 도구 유무"; grep -rn "def aggregate_datasets" ~/lerobot/src 2>/dev/null | head -3
echo "== norm_stats.json 생성 위치"; grep -rln "norm_stats" ~/lerobot/src ~/lerobot/*.py 2>/dev/null | head -5
