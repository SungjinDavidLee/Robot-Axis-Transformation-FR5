#!/usr/bin/env python3
# FR3 데이터 프레임과 FR5 작업 프레임의 축 방향이 같은지 확인한다. 읽기 전용.
# 그룹은 3인칭 시작 프레임 시트(fig13/14)를 보고 사람이 나눈 것이다.
import glob, sys
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
GROUPS = {'plate_right': [0, 7, 11, 25, 64, 65, 73],    # 시트에서 접시가 그릇 오른쪽
          'plate_left':  [10, 35, 66, 70, 76, 78, 85],  # 접시가 그릇 왼쪽(인덕션 앞)
          'plate_front': [1, 2, 3, 4]}                   # 접시가 그릇보다 카메라 쪽

def events(d):
    files = sorted(glob.glob(f'{d}/data/**/*.parquet', recursive=True))
    df = pd.concat([pq.read_table(f).to_pandas() for f in files]).sort_values('index')
    S = np.stack(df['observation.state'].to_numpy()).astype(float)
    A = np.stack(df['action'].to_numpy()).astype(float)
    ep = df['episode_index'].to_numpy()
    g = A[:, 6]; thr = (g.min() + g.max()) / 2
    out = {}
    for e in np.unique(ep):
        idx = np.flatnonzero(ep == e)
        c = np.flatnonzero(g[idx] < thr)
        if not len(c):
            continue
        o = np.flatnonzero(g[idx[c[0]:]] > thr)
        out[e] = (S[idx[c[0]], :3], S[idx[c[0] + o[0]], :3] if len(o) else None)
    return out

fr3 = events(f'{ROOT}/data/task6_franka_v5')
fr5 = events(f'{ROOT}/data/fr5_task6_abs')
print('FR3  place - grasp  [dx, dy]')
for name, ids in GROUPS.items():
    D = []
    for e in ids:
        gp, pp = fr3.get(e, (None, None))
        if pp is None:
            print(f'  {name:12s} ep{e:3d}  place 없음'); continue
        d = pp[:2] - gp[:2]; D.append(d)
        print(f'  {name:12s} ep{e:3d}  dx {d[0]:+.3f}  dy {d[1]:+.3f}')
    if D:
        m = np.mean(D, 0); print(f'  -> {name} mean dx {m[0]:+.3f}  dy {m[1]:+.3f}')
D5 = np.array([pp[:2] - gp[:2] for gp, pp in fr5.values() if pp is not None])
print(f'\nFR5 전 판 (n={len(D5)})  mean dx {D5[:,0].mean():+.3f}  dy {D5[:,1].mean():+.3f}  dy<0 비율 {np.mean(D5[:,1] < 0):.2f}')
gz3 = np.median([gp[2] for gp, _ in fr3.values()]); gz5 = np.median([gp[2] for gp, _ in fr5.values()])
print(f'grasp z median  FR3 {gz3:.4f}  FR5 {gz5:.4f}  diff {gz3 - gz5:+.4f}')
