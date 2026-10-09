#!/usr/bin/env python3
# FR3 task6_franka_v5 -> FR5 규약 사본. 원본은 읽기만 하고 DST에 새로 쓴다.
#   z     : FR3 파지 높이를 FR5에 맞춤 (DZ)
#   회전  : 시작 자세 평균 기준 툴 좌표계 오프셋을 곱함, 축각은 판 안에서 연속 표현
#   action: action[t] = state[t+1][:7], 마지막 프레임은 자기 자신
import glob, json, os, shutil, sys
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy.spatial.transform import Rotation as Rot

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
SRC, REF = f'{ROOT}/data/task6_franka_v5', f'{ROOT}/data/fr5_task6_abs'
DST = f'{ROOT}/data/fr3_task6_aligned_v1'
DZ = -0.0192
REF_AA = np.array([-2.4425330290871115, 1.968073832566227, 0.0019828086840627443])  # FR5 축각 기준

def tables(d):
    fs = sorted(glob.glob(f'{d}/data/**/*.parquet', recursive=True))
    return fs, [pq.read_table(f) for f in fs]

def arrays(tabs):
    df = pd.concat([t.to_pandas() for t in tabs]).sort_values('index')
    S = np.stack(df['observation.state'].to_numpy()).astype(float)
    return S, df['episode_index'].to_numpy()

def starts(ep):
    return np.r_[0, np.flatnonzero(np.diff(ep)) + 1]

def pick(v, ref):                      # 같은 회전의 두 축각 표현 중 ref에 가까운 쪽
    th = np.linalg.norm(v)
    if th < 1e-9:
        return v
    a = v - 2 * np.pi * v / th
    return a if np.linalg.norm(a - ref) < np.linalg.norm(v - ref) else v

def stat(M, k):
    if k == 'min': return M.min(0)
    if k == 'max': return M.max(0)
    if k == 'mean': return M.mean(0)
    if k == 'std': return M.std(0)
    if k == 'count': return np.array([len(M)])
    if k.startswith('q') and k[1:].isdigit(): return np.percentile(M, int(k[1:]), axis=0)
    return None

if os.path.exists(DST):
    sys.exit(f'{DST} 이미 있음 — 확인 후 지우고 다시 실행')
src_files, src_tabs = tables(SRC)
S5, ep5 = arrays(tables(REF)[1])
S3, _ = arrays(src_tabs)
_, ep3 = arrays(src_tabs)
OFF = Rot.from_rotvec(S3[starts(ep3), 3:6]).mean().inv() * Rot.from_rotvec(S5[starts(ep5), 3:6]).mean()
print(f'회전 오프셋 (tool frame) {np.degrees(OFF.magnitude()):.1f} deg  euler xyz {OFF.as_euler("xyz", degrees=True).round(2)}')

shutil.copytree(SRC, DST, ignore=lambda d, names: ['data'] if d == SRC else [])
if os.path.exists(f'{DST}/norm_stats.json'):
    os.rename(f'{DST}/norm_stats.json', f'{DST}/norm_stats.json.stale')

allS, allA, allE = [], [], []
for f, t in zip(src_files, src_tabs):
    df = t.to_pandas()
    order = np.argsort(df['index'].to_numpy(), kind='stable')
    S = np.stack(df['observation.state'].to_numpy()).astype(float)
    ep = df['episode_index'].to_numpy()
    S2 = S.copy(); S2[:, 2] += DZ
    R = (Rot.from_rotvec(S[:, 3:6]) * OFF).as_rotvec()
    A2 = np.zeros((len(S2), 7))
    for e in np.unique(ep):
        idx = order[ep[order] == e]
        prev = REF_AA
        for i in idx:
            R[i] = pick(R[i], prev); prev = R[i]
    S2[:, 3:6] = R
    for e in np.unique(ep):
        idx = order[ep[order] == e]
        A2[idx[:-1]] = S2[idx[1:], :7]; A2[idx[-1]] = S2[idx[-1], :7]
    tab = t
    for col, M in (('observation.state', S2), ('action', A2)):
        i = tab.schema.get_field_index(col)
        tab = tab.set_column(i, col, pa.array(M.astype(np.float32).tolist(), type=tab.schema.field(col).type))
    out = f.replace(SRC, DST); os.makedirs(os.path.dirname(out), exist_ok=True)
    pq.write_table(tab, out)
    allS.append(S2); allA.append(A2); allE.append(ep)
S2, A2, E2 = np.vstack(allS), np.vstack(allA), np.concatenate(allE)

sp = f'{DST}/meta/stats.json'
st = json.load(open(sp))
for col, M in (('observation.state', S2), ('action', A2)):
    for k in list(st.get(col, {})):
        v = stat(M, k)
        if v is None: print('stats 갱신 못함:', col, k); continue
        st[col][k] = v.tolist()
json.dump(st, open(sp, 'w'), indent=4)

for f in sorted(glob.glob(f'{DST}/meta/episodes/**/*.parquet', recursive=True)):
    et = pq.read_table(f); edf = et.to_pandas()
    for col, M in (('observation.state', S2), ('action', A2)):
        for c in [c for c in edf.columns if c.startswith(f'stats/{col}/')]:
            k = c.split('/')[-1]
            vals = [stat(M[E2 == e], k) for e in edf['episode_index']]
            if any(v is None for v in vals): print('episode stats 갱신 못함:', c); continue
            i = et.schema.get_field_index(c)
            et = et.set_column(i, c, pa.array([v.tolist() for v in vals], type=et.schema.field(c).type))
    pq.write_table(et, f)

# 검증
S2c, ep2 = arrays(tables(DST)[1])
Ac = np.stack(pd.concat([t.to_pandas() for t in tables(DST)[1]]).sort_values('index')['action'].to_numpy())
same = np.r_[ep2[1:] == ep2[:-1]]
print(f'action[t]==state[t+1] 최대 오차 {np.abs(Ac[:-1][same] - S2c[1:, :7][same]).max():.2e}')
print(f'판 안 축각 최대 점프 {np.linalg.norm(np.diff(S2c[:, 3:6], axis=0)[same], axis=1).max():.3f} rad')
d = Rot.from_rotvec(S2c[starts(ep2), 3:6]).mean().inv() * Rot.from_rotvec(S5[starts(ep5), 3:6]).mean()
print(f'시작 자세 차 (정합 후, FR5 대비) {np.degrees(d.magnitude()):.2f} deg')
print('saved', DST)
