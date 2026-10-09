# FR5 시연에서 파지 순간 손목이 시작 자세 대비 어떻게 돌아 있었는지 (yaw: 접근축 둘레, tilt: 접근축 기울기)
import glob, numpy as np, pandas as pd, pyarrow.parquet as pq
from scipy.spatial.transform import Rotation as Rot
D = '/home/data/fr_transfer/data/fr5_task6_abs'
df = pd.concat([pq.read_table(f).to_pandas() for f in sorted(glob.glob(f'{D}/data/**/*.parquet', recursive=True))]).sort_values('index')
S = np.stack(df['observation.state'].to_numpy()).astype(float); A = np.stack(df['action'].to_numpy()).astype(float)
ep = df['episode_index'].to_numpy(); thr = (A[:, 6].min() + A[:, 6].max()) / 2
yaw, tilt = [], []
for e in np.unique(ep):
    i = np.flatnonzero(ep == e); c = np.flatnonzero(A[i, 6] < thr)
    if not len(c): continue
    R = (Rot.from_rotvec(S[i[0], 3:6]).inv() * Rot.from_rotvec(S[i[c[0]], 3:6])).as_matrix()
    yaw.append(np.degrees(np.arctan2(R[1, 0], R[0, 0]))); tilt.append(np.degrees(np.arccos(np.clip(R[2, 2], -1, 1))))
for n, v in (('yaw', yaw), ('tilt', tilt)):
    print(f'{n:4s}  n={len(v)}  p10/p50/p90 = {np.round(np.percentile(v, [10, 50, 90]), 1)}')
