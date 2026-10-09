#!/usr/bin/env python3
# FR3 v5 vs FR5 1차 정합 확인 — 데이터는 읽기만 한다. 결과: 텍스트 + phase1_xy.png
# 주의: FR5 데이터는 base 가 아니라 작업 프레임(base 를 z축 -77.2° 회전) 기준이다. 그림 제목의 "own base frame" 은 FR3 에만 맞다.
import glob, sys
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy.spatial.transform import Rotation as Rot
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
SETS = {'FR3': f'{ROOT}/data/task6_franka_v5', 'FR5': f'{ROOT}/data/fr5_task6_abs'}
np.set_printoptions(precision=3, suppress=True)

def load(d):
    files = sorted(glob.glob(f'{d}/data/**/*.parquet', recursive=True))
    df = pd.concat([pq.read_table(f).to_pandas() for f in files], ignore_index=True).sort_values('index')
    S = np.stack(df['observation.state'].to_numpy()).astype(float)
    A = np.stack(df['action'].to_numpy()).astype(float)
    return S, A, df['episode_index'].to_numpy()

def rng(P):
    return 'n/a' if len(P) == 0 else f'min {P.min(0)}  max {P.max(0)}  mean {P.mean(0)}'

res = {}
fig, axes = plt.subplots(1, 2, figsize=(11, 5))
for ax, (name, d) in zip(axes, SETS.items()):
    S, A, ep = load(d)
    starts = np.r_[0, np.flatnonzero(np.diff(ep)) + 1]
    ends = np.r_[starts[1:], len(ep)]
    R = Rot.from_rotvec(S[:, 3:6])                  # 비정규 axis-angle도 회전으로 복원됨
    M = R.as_matrix()
    tilt = np.degrees(np.arccos(np.clip(-M[:, 2, 2], -1, 1)))   # 툴 z축과 연직 하향 사이 각
    yaw = np.degrees(np.arctan2(M[:, 1, 0], M[:, 0, 0]))       # 툴 x축의 평면 방위각
    step = np.linalg.norm(np.diff(S[:, :3], axis=0), axis=1)[np.diff(ep) == 0]
    g = A[:, 6]; thr = (g.min() + g.max()) / 2
    grasp, place = [], []
    for s, e in zip(starts, ends):
        c = np.flatnonzero(g[s:e] < thr)
        if len(c) == 0:
            continue
        grasp.append(S[s + c[0], :3])
        o = np.flatnonzero(g[s + c[0]:e] > thr)
        if len(o):
            place.append(S[s + c[0] + o[0], :3])
    grasp, place = np.array(grasp), np.array(place)
    L = ends - starts
    print(f'\n##### {name}  episodes={len(starts)}  len mean/min/max={L.mean():.1f}/{L.min()}/{L.max()}')
    print(f'start xyz   {rng(S[starts, :3])}')
    print(f'grasp xyz   n={len(grasp)}  {rng(grasp)}')
    print(f'place xyz   n={len(place)}  {rng(place)}')
    print(f'tilt deg    median {np.median(tilt):.1f}  p95 {np.percentile(tilt, 95):.1f}  max {tilt.max():.1f}')
    print(f'yaw deg     start mean {yaw[starts].mean():.1f} std {yaw[starts].std():.1f} | all p5/p50/p95 {np.percentile(yaw, [5, 50, 95])}')
    print(f'step m/frame median {np.median(step):.4f}  p95 {np.percentile(step, 95):.4f}  max {step.max():.4f}')
    print(f'gripper     unique={len(np.unique(np.round(g, 5)))}  min {g.min():.4f}  max {g.max():.4f}  hist {np.histogram(g, 10)[0]}')
    res[name] = R[starts].mean()
    ax.plot(S[::3, 1], S[::3, 0], ',', alpha=0.3, color='gray')
    if len(grasp): ax.scatter(grasp[:, 1], grasp[:, 0], s=8, label='grasp')
    if len(place): ax.scatter(place[:, 1], place[:, 0], s=8, label='place')
    ax.set_title(f'{name} (own base frame)'); ax.set_xlabel('y [m]'); ax.set_ylabel('x [m]')
    ax.set_aspect('equal'); ax.legend()
fig.tight_layout(); fig.savefig(f'{ROOT}/phase1_xy.png', dpi=120)

off = res['FR3'].inv() * res['FR5']     # R_FR5 = R_FR3 · R_off (툴 좌표계, 시작 자세 평균)
print(f'\n##### 시작 자세 회전 차 (FR3→FR5, tool frame)  angle {np.degrees(off.magnitude()):.1f} deg  euler xyz {off.as_euler("xyz", degrees=True)}')

print('\n##### fr5_cell.urdf')
try:
    root = ET.parse(f'{ROOT}/assets/fr5/fr5_cell.urdf').getroot()
    keep = ('world_to_table', 'table_to_plate', 'plate_to_arm_base', 'world_to_sensor_mount_vertical',
            'world_to_sensor_mount_horizontal', 'grasp_joint')
    for j in root.findall('joint'):
        if j.get('name') in keep:
            o = j.find('origin')
            print(j.get('name'), dict(o.attrib) if o is not None else None)
    for l in root.findall('link'):
        if l.get('name') == 'table_link':
            print('table_link box:', [b.get('size') for b in l.iter('box')])
except Exception as e:
    print('URDF 읽기 실패:', e)
