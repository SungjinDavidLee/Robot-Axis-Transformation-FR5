#!/usr/bin/env python3
# FR3 시작 프레임 전체를 작업대 영역만 잘라 접촉 시트로 만든다 (눈으로 판정용). 읽기 전용.
import glob, sys
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import av
from PIL import Image, ImageDraw

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
D = f'{ROOT}/data/task6_franka_v5'
KEY = 'observation.images.image'
R0, R1, C0, C1 = 90, 250, 60, 220   # 작업대 영역 (256x256 기준)
EDGE = 123                          # 인덕션 오른쪽 끝 열 (참고선 — 실제 경계는 약 113~118열)
COLS, PER, GAP = 10, 100, 3

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

eps, ts = episodes(D)
vid = sorted(glob.glob(f'{D}/videos/{KEY}/**/*.mp4', recursive=True))[0]
tiles = []
for e, f in zip(eps, frames_at(vid, ts)):
    if f is None:
        continue
    im = Image.fromarray(np.ascontiguousarray(f[R0:R1, C0:C1]))
    dr = ImageDraw.Draw(im)
    dr.line([(EDGE - C0, 0), (EDGE - C0, R1 - R0)], fill=(255, 255, 0), width=1)
    dr.rectangle([0, 0, 26, 11], fill=(0, 0, 0))
    dr.text((2, 0), str(e), fill=(255, 255, 255))
    tiles.append(im)
w, h = C1 - C0, R1 - R0
for s in range(0, len(tiles), PER):
    chunk = tiles[s:s + PER]
    rows = (len(chunk) + COLS - 1) // COLS
    sheet = Image.new('RGB', (COLS * (w + GAP), rows * (h + GAP)), 'white')
    for i, t in enumerate(chunk):
        sheet.paste(t, ((i % COLS) * (w + GAP), (i // COLS) * (h + GAP)))
    out = f'{ROOT}/fr3_start_sheet_{s // PER + 1}.png'
    sheet.save(out); print('saved', out, sheet.size)
