#!/usr/bin/env bash
# 읽기 전용 — 메타·설정·샘플 값만 출력 (FR3 제어 PC에서 실행)
PY=$HOME/lerobot/.venv/bin/python; [ -x "$PY" ] || PY=python3
T6=$HOME/openvla_franka/task6

echo "=== [1] LeRobot 데이터셋 요약"
du -sh $HOME/.cache/huggingface/lerobot/local/* 2>/dev/null
"$PY" - <<'PY'
import json, glob, os
import numpy as np
import pyarrow.parquet as pq

def fmt(v):
    try:
        return np.round(np.asarray(v, dtype=float), 5).tolist()
    except Exception:
        return str(v)[:60]

root = os.path.expanduser('~/.cache/huggingface/lerobot/local')
for d in sorted(glob.glob(f'{root}/*')):
    print(f'\n##### {os.path.basename(d)}')
    try:
        info = json.load(open(f'{d}/meta/info.json'))
    except Exception as e:
        print('info.json 읽기 실패:', e); continue
    for k in ['codebase_version', 'robot_type', 'fps', 'total_episodes', 'total_frames', 'total_tasks']:
        print(f'{k}: {info.get(k)}')
    for name, ft in info.get('features', {}).items():
        print(f'  - {name}: {ft.get("dtype")} {ft.get("shape")} names={ft.get("names")}')
    tj, tp = f'{d}/meta/tasks.jsonl', f'{d}/meta/tasks.parquet'
    if os.path.exists(tj):
        print('tasks:', open(tj).read().strip()[:800])
    elif os.path.exists(tp):
        print('tasks:', pq.read_table(tp).to_pandas().to_string()[:800])
    sp = f'{d}/meta/stats.json'
    if os.path.exists(sp):
        st = json.load(open(sp))
        print('stats keys:', [k for k in st if not k.startswith('observation.images')])
        for key in ['observation.state', 'action']:
            if key in st:
                print(f'stats {key} min:', fmt(np.ravel(st[key]['min'])))
                print(f'stats {key} max:', fmt(np.ravel(st[key]['max'])))
    files = sorted(glob.glob(f'{d}/data/**/*.parquet', recursive=True))
    if files:
        df = pq.read_table(files[0]).to_pandas()
        print('sample file:', files[0])
        print('columns:', list(df.columns))
        cols = [c for c in df.columns if not isinstance(df[c].iloc[0], (dict, bytes))]
        for i in range(min(3, len(df))):
            print({c: fmt(df[c].iloc[i]) for c in cols})
PY

echo; echo "=== [2] task6 작업 폴더 구조"
find "$T6" -maxdepth 2 -not -path '*/rlds/data/*' 2>/dev/null | sort | head -80
echo; echo "=== [3] collect/calib.json"
head -60 "$T6/collect/calib.json" 2>/dev/null
echo; echo "=== [4] 수집 스크립트 주요 설정"
grep -rnEi --include='*.py' --include='*.yaml' --include='*.json' 'serial|fps|hz|rate|width|height|robotiq|gripper|tcp|ee_frame|action_type|delta' "$T6/collect" 2>/dev/null | cut -c1-200 | head -60
echo; echo "=== [5] space 폴더"
ls -la "$T6/space" 2>/dev/null
head -40 "$T6/space/space_calib.py" 2>/dev/null
echo; echo "=== [6] GELLO 캘리브레이션 (good)"
head -40 $HOME/gello_backup/20260915_142905_good/calib_final.json 2>/dev/null
echo; echo "=== [7] FR5 관련 파일"
find $HOME -maxdepth 8 \( -iname '*fr5*' -o -iname '*fairino*' \) -not -path '*/.cache/*' -not -path '*/anaconda3/*' 2>/dev/null | head -30
echo; echo "=== [8] 정책 학습 저장소"
git -C $HOME/groot-fr3-task6 log --oneline -5 2>/dev/null
ls $HOME/groot-fr3-task6 2>/dev/null | head -30
