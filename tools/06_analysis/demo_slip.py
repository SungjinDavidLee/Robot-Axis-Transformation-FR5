# FR5 시연의 파지 후 밀림(닫은 뒤 폭 - 이송 중 최소 폭)과 파지 높이·손목 yaw
# 그리퍼 값은 수집기(fr5_collect.py)가 제어판 gripper.pos(실측)를 읽어 남긴 것이다.
import glob, numpy as np, pandas as pd, pyarrow.parquet as pq
from scipy.spatial.transform import Rotation as Rot
D = '/home/data/fr_transfer/data/fr5_task6_abs'
df = pd.concat([pq.read_table(f).to_pandas() for f in sorted(glob.glob(f'{D}/data/**/*.parquet', recursive=True))]).sort_values('index')
S = np.stack(df['observation.state'].to_numpy()).astype(float); ep = df['episode_index'].to_numpy()
w = S[:, 6]; thr = (w.min() + w.max()) / 2
out = []
for e in np.unique(ep):
    i = np.flatnonzero(ep == e); c = np.flatnonzero(w[i] < thr)
    if not len(c):
        continue
    k = int(c[0]); o = np.flatnonzero(w[i][k:] > thr); r = k + int(o[0]) if len(o) else len(i)
    seg = w[i][k + 1:r]
    if len(seg) < 3:
        continue
    a = 2                                    # 닫기 시작 후 약 0.9 s (3.4 Hz 기준 2프레임) 지점의 폭을 기준으로
    R = (Rot.from_rotvec(S[i[0], 3:6]).inv() * Rot.from_rotvec(S[i[k], 3:6])).as_matrix()
    out.append([(seg[a] - seg[a:].min()) * 1000, seg[a:].min() * 1000, seg[a] * 1000,
                S[i[k], 2] * 1000, np.degrees(np.arctan2(R[1, 0], R[0, 0]))])
O = np.array(out)
for n, j in (('밀림 mm', 0), ('최소 폭 mm', 1), ('문 폭 mm', 2), ('파지 z mm', 3), ('yaw deg', 4)):
    print(f'{n:10s} p10/p50/p90 = {np.round(np.percentile(O[:, j], [10, 50, 90]), 1)}')
print(f'판 수 {len(O)}   밀림 4 mm 이상 {int(np.sum(O[:, 0] >= 4))}   최소 폭 1.5 mm 미만(놓침) {int(np.sum(O[:, 1] < 1.5))}')
print(f'상관  밀림~z {np.corrcoef(O[:, 0], O[:, 3])[0, 1]:+.2f}   밀림~yaw {np.corrcoef(O[:, 0], O[:, 4])[0, 1]:+.2f}')
