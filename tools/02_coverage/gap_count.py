#!/usr/bin/env python3
# 판별 시작 프레임에서 목표 그릇 위치를 찾아 인덕션 오른쪽 끝(EDGE 열) 기준 왼쪽 배치를 센다. 읽기 전용.
# 기록용으로 남긴다: 이 검출기는 실패했다 (docs/04_coverage.md 3절). 90백분위 배경이 흰 접시를 배경으로
# 잡아 FR5 에서 접시 자리를 "검은 물체"로 오검출했고, FR3 에서는 캐비닛 가장자리를 잡았다.
import glob, sys
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import av
from scipy import ndimage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
SETS = {'FR3': (f'{ROOT}/data/task6_franka_v5', 123), 'FR5': (f'{ROOT}/data/fr5_task6_abs', 125)}
KEY = 'observation.images.image'
ROW0 = 100   # 이 행 아래(작업대)만 탐색

def episodes(d):
    files = sorted(glob.glob(f'{d}/meta/episodes/**/*.parquet', recursive=True))
    ep = pd.concat([pq.read_table(f).to_pandas() for f in files]).sort_values('episode_index')
    tc = [c for c in ep.columns if KEY in c and c.endswith('from_timestamp')][0]
    return ep['episode_index'].to_numpy(), ep[tc].to_numpy(float)

def frames_at(path, times):
    out, order, k = [None] * len(times), np.argsort(times), 0
    with av.open(path) as c:
        s = c.streams.video[0]
        for f in c.decode(s):
            t = float(f.pts * s.time_base)
            while k < len(order) and t >= times[order[k]] - 1e-3:
                out[order[k]] = f.to_ndarray(format='rgb24'); k += 1
            if k == len(order):
                break
    return out

def grasps(d):
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
        if len(c):
            out[e] = S[idx[c[0]], :2]
    return out

fig, axes = plt.subplots(2, 2, figsize=(11, 10))
for row, (name, (d, edge)) in zip(axes, SETS.items()):
    eps, ts = episodes(d)
    vid = sorted(glob.glob(f'{d}/videos/{KEY}/**/*.mp4', recursive=True))[0]
    fr = frames_at(vid, ts)
    keep = [i for i, f in enumerate(fr) if f is not None]
    eps, F = eps[keep], np.stack([fr[i] for i in keep])
    G = F.mean(-1)
    bg = np.percentile(G, 90, axis=0)            # 그릇이 없는 배경 근사 (이 가정이 틀렸다)
    C = np.full((len(F), 2), np.nan)
    for k in range(len(F)):
        m = G[k] < bg - 70
        m[:ROW0] = False
        lab, n = ndimage.label(m)
        if n == 0:
            continue
        sz = ndimage.sum(m, lab, range(1, n + 1)); j = int(np.argmax(sz))
        if sz[j] >= 80:
            C[k] = ndimage.center_of_mass(m, lab, j + 1)
    gr = grasps(d)
    P = np.array([gr.get(e, [np.nan, np.nan]) for e in eps])
    ok = ~np.isnan(C[:, 0]) & ~np.isnan(P[:, 0])
    gap = ok & (C[:, 1] < edge)
    cc = lambda a, b: np.corrcoef(a[ok], b[ok])[0, 1]
    print(f'\n##### {name}  detected {ok.sum()}/{len(F)}  gap(col<{edge}) {gap.sum()}')
    print(f'corr  col~grasp_y {cc(C[:,1], P[:,1]):+.2f}  col~grasp_x {cc(C[:,1], P[:,0]):+.2f}  '
          f'row~grasp_x {cc(C[:,0], P[:,0]):+.2f}  row~grasp_y {cc(C[:,0], P[:,1]):+.2f}')
    if gap.any():
        print(f'gap grasp x {P[gap,0].min():.3f}~{P[gap,0].max():.3f}  y {P[gap,1].min():.3f}~{P[gap,1].max():.3f}')
        print('gap episodes', eps[gap].tolist())
    a = row[0]
    a.imshow(np.median(F, axis=0).astype(np.uint8))
    a.axvline(edge, color='yellow', lw=1)
    a.scatter(C[ok & ~gap, 1], C[ok & ~gap, 0], s=10, c='cyan', label='right of edge')
    a.scatter(C[gap, 1], C[gap, 0], s=14, c='red', label='left of edge (gap)')
    a.set_title(f'{name} bowl centroid at start'); a.legend(fontsize=8, loc='lower right')
    b = row[1]
    b.scatter(P[ok & ~gap, 1], P[ok & ~gap, 0], s=10, c='tab:blue', label='right of edge')
    b.scatter(P[gap, 1], P[gap, 0], s=14, c='red', label='gap')
    b.set_xlabel('grasp y [m]'); b.set_ylabel('grasp x [m]'); b.set_aspect('equal')
    b.set_title(f'{name} grasp point (data frame)'); b.legend(fontsize=8)
fig.tight_layout(); fig.savefig(f'{ROOT}/coverage_gap.png', dpi=110)
print('\nsaved', f'{ROOT}/coverage_gap.png')
