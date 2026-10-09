#!/usr/bin/env python3
# FR3/FR5 3인칭 시작 프레임 합성 — 그릇 배치 커버리지 판정용. 데이터는 읽기만 한다.
import glob, sys
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import av
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
SETS = {'FR3': f'{ROOT}/data/task6_franka_v5', 'FR5': f'{ROOT}/data/fr5_task6_abs'}
KEY = 'observation.images.image'

def start_times(d):
    files = sorted(glob.glob(f'{d}/meta/episodes/**/*.parquet', recursive=True))
    ep = pd.concat([pq.read_table(f).to_pandas() for f in files]).sort_values('episode_index')
    tc = [c for c in ep.columns if KEY in c and c.endswith('from_timestamp')]
    fc = [c for c in ep.columns if KEY in c and c.endswith('file_index')]
    if not tc:
        print('from_timestamp 열 없음:', ep.columns.tolist()); sys.exit(1)
    if fc and ep[fc[0]].nunique() > 1:
        print('경고: 영상 파일이 여러 개 — 첫 파일만 사용')
    return ep[tc[0]].to_numpy(float)

def frames_at(path, times):
    out, order, k = [None] * len(times), np.argsort(times), 0
    with av.open(path) as c:
        s = c.streams.video[0]
        print(f'  codec {s.codec_context.name}  frames {s.frames}')
        for f in c.decode(s):
            t = float(f.pts * s.time_base)
            while k < len(order) and t >= times[order[k]] - 1e-3:
                out[order[k]] = f.to_ndarray(format='rgb24'); k += 1
            if k == len(order):
                break
    return [o for o in out if o is not None]

fig, axes = plt.subplots(2, 3, figsize=(12, 8.4))
for row, (name, d) in zip(axes, SETS.items()):
    vid = sorted(glob.glob(f'{d}/videos/{KEY}/**/*.mp4', recursive=True))[0]
    print(name, vid)
    F = np.stack(frames_at(vid, start_times(d)))
    print(f'  decoded start frames: {len(F)}')
    med = np.median(F, axis=0).astype(np.uint8)
    dark = (F.mean(-1) < med.mean(-1)[None] - 40).mean(0)   # 중앙값보다 크게 어두운 판의 비율
    row[0].imshow(med); row[0].set_title(f'{name} median (scene)')
    row[1].imshow(F.min(axis=0)); row[1].set_title(f'{name} min (all placements)')
    row[2].imshow(med); row[2].imshow(dark, cmap='hot', alpha=0.6, vmin=0, vmax=0.3)
    row[2].set_title(f'{name} dark-object frequency')
    for a in row:
        a.set_xticks(range(0, 256, 32)); a.set_yticks(range(0, 256, 32)); a.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(f'{ROOT}/coverage_start.png', dpi=110)
print('saved', f'{ROOT}/coverage_start.png')
