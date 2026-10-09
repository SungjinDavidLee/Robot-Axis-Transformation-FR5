# 학습 서버에서 ~/lerobot 의 venv 로 실행: cd ~/lerobot && ./.venv/bin/python merge_fr5_fr3.py
from pathlib import Path
from lerobot.datasets.aggregate import aggregate_datasets
from lerobot.datasets.lerobot_dataset import LeRobotDataset

B = Path.home() / '.cache/huggingface/lerobot/local'
SRC = ['fr5_task6_abs', 'fr3_task6_aligned_v1']   # FR5 먼저: 0~204 FR5, 205~404 FR3
OUT = 'fr5_fr3_task6_v1'
if (B / OUT).exists():
    raise SystemExit(f'{B / OUT} 이미 있음')
aggregate_datasets(repo_ids=[f'local/{s}' for s in SRC], aggr_repo_id=f'local/{OUT}',
                   roots=[B / s for s in SRC], aggr_root=B / OUT)

ds = LeRobotDataset(f'local/{OUT}', root=B / OUT)
m = ds.meta
print('episodes', m.total_episodes, 'frames', m.total_frames, 'robot_type', m.robot_type, 'fps', m.fps)
print('tasks', m.tasks)
for i in (0, len(ds) - 1):
    s = ds[i]
    print(i, 'ep', int(s['episode_index']), 'state', [round(float(v), 4) for v in s['observation.state']],
          'img', tuple(s['observation.images.image'].shape), tuple(s['observation.images.wrist_image'].shape))
st = m.stats['observation.state']
print('stats state min', [round(float(v), 4) for v in st['min']])
print('stats state max', [round(float(v), 4) for v in st['max']])
# 주의: aggregate 는 norm_stats.json 을 복사하지 않는다. 정책 서버가 ref_axis_angle 을 그 파일에서 읽으므로
#       FR5 의 파일을 합친 데이터셋 폴더에 복사해야 한다 (04_train_serve/restart_c1.sh).
