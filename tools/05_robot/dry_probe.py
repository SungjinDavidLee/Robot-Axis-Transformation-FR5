#!/usr/bin/env python3
# --dry 추종 확인용 탐침. 로봇에는 아무것도 보내지 않는다 (제어판 읽기 + 카메라 + 추론 요청만).
#   같은 관측을 세 서버에 보내 체크포인트끼리 짝지어 비교한다.
#   전제: 롤아웃·수집기 꺼짐(카메라 독점), 로봇은 초기 자세, 서버 3개 실행 중
#   실행 환경: conda activate openvla_py310  (pyrealsense2·PIL 이 함께 있는 환경)
import base64, csv, json, math, os, sys, time, urllib.request
import numpy as np
import pyrealsense2 as rs
from PIL import Image
sys.path.insert(0, os.path.expanduser("~/fr5cap/collect"))
import fr5cfg as C

HOST = os.environ.get("HOST", "http://TRAIN_SERVER_IP")
SERVERS = [("B0", 8200), ("C1-6k", 8201), ("C1-12k", 8202)]
PANEL = "http://127.0.0.1:8088"
REPEAT = int(os.environ.get("REPEAT", "3"))
GRIP_CLOSE = 0.3 * C.GRIP_MAX_M                      # 롤아웃 GRIP_TH 0.3 과 같은 기준
OUT = os.path.expanduser("~/fr5cap/dry_probe.csv")
EXP_T, EXP_W = int(os.environ.get("EXP_THIRD", "25600")), int(os.environ.get("EXP_WRIST", "17300"))
WB_T, WB_W = int(os.environ.get("WB_THIRD", "3600")), int(os.environ.get("WB_WRIST", "3800"))


def http_get(url, timeout=10):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read())


def http_post(url, obj, timeout=30):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def canon(aa, ref):                                  # fr5_rollout.py 와 동일
    aa = np.asarray(aa, float); n = float(np.linalg.norm(aa))
    if n < 1e-9 or ref is None:
        return aa
    alt = aa * (n - 2.0 * math.pi) / n
    return aa if np.linalg.norm(aa - np.asarray(ref)) <= np.linalg.norm(alt - np.asarray(ref)) else alt


class Cam:                                           # fr5_rollout.py 와 동일한 설정
    def __init__(self, sn, exp, wb, name):
        self.pipe = rs.pipeline(); cfg = rs.config(); cfg.enable_device(sn)
        cfg.enable_stream(rs.stream.color, C.IMG_W, C.IMG_H, rs.format.rgb8, C.CAM_FPS)
        s = self.pipe.start(cfg).get_device().query_sensors()[0]
        s.set_option(rs.option.enable_auto_exposure, 0); s.set_option(rs.option.exposure, exp)
        s.set_option(rs.option.enable_auto_white_balance, 0); s.set_option(rs.option.white_balance, wb)
        print(f"  {name}: exp={exp} wb={wb}")

    def grab(self):
        f = self.pipe.wait_for_frames().get_color_frame()
        im = np.asanyarray(f.get_data())
        return np.asarray(Image.fromarray(im).resize((256, 256), Image.BILINEAR), dtype=np.uint8)


def summarize(chunk):                                # 처음 닫으라는 지점, 없으면 가장 낮은 지점
    c = np.asarray(chunk, float)
    idx = np.flatnonzero(c[:, 6] < GRIP_CLOSE)
    k = int(idx[0]) if len(idx) else int(np.argmin(c[:, 2]))
    return c[k, :3], ("close" if len(idx) else "minz"), c[-1, :3]


refs = {}
for name, port in SERVERS:
    info = http_get(f"{HOST}:{port}/info")
    print(f"{name:7s} {port}  {info['ckpt']}")
    refs[name] = info["ref_axis_angle"]
if None in refs.values() or len({json.dumps(v) for v in refs.values()}) != 1:
    sys.exit("ref_axis_angle 이 비었거나 서버마다 다름 — 중단")
REF = refs["B0"]
third, wrist = Cam(C.CAM_THIRD, EXP_T, WB_T, "third"), Cam(C.CAM_WRIST, EXP_W, WB_W, "wrist")
for _ in range(10):                                  # 노출 안정화
    third.grab(); wrist.grab()

new = not os.path.exists(OUT)
f = open(OUT, "a", newline=""); w = csv.writer(f)
if new:
    w.writerow(["time", "layout", "bowl_x", "bowl_y", "ckpt", "rep", "kind",
                "tx", "ty", "tz", "end_x", "end_y", "end_z", "ms"])
print("\n그릇을 놓고 로봇을 초기 자세에 둔 뒤 '배치이름 x y' 입력 (예: L1 0.620 0.280). 빈 입력이면 종료.")
while True:
    line = input("배치> ").strip()
    if not line:
        break
    try:
        lab, bx, by = line.split(); bx, by = float(bx), float(by)
    except ValueError:
        print("  형식: 이름 x y"); continue
    st = http_get(PANEL + "/api/state", 2)
    p, aa, _ = C.tcp_to_task(st["tcp"])
    g = C.grip_to_m(st["gripper"]["pos"])
    state = [float(v) for v in p] + [float(v) for v in canon(aa, REF)] + [g, -g]
    im, wr = third.grab(), wrist.grab()
    body = {"state": state, "image": base64.b64encode(im.tobytes()).decode(),
            "wrist": base64.b64encode(wr.tobytes()).decode()}
    row = []
    for name, port in SERVERS:
        T, kinds = [], []
        for r in range(REPEAT):
            t0 = time.time()
            res = http_post(f"{HOST}:{port}/act", body)
            ms = (time.time() - t0) * 1000
            tp, kind, ep = summarize(res["chunk"])
            T.append(tp[:2]); kinds.append(kind)
            w.writerow([time.strftime("%F %T"), lab, bx, by, name, r, kind,
                        *np.round(tp, 4), *np.round(ep, 4), round(ms)])
        T = np.array(T)
        print(f"  {name:7s} 목표 xy {np.round(T.mean(0), 3)}  반복 편차 {np.round(T.std(0) * 1000, 1)} mm  {kinds}")
        row += [round(float(v), 3) for v in T.mean(0)]
    f.flush()
    print("  스프레드시트 행:", lab, bx, by, *row)
f.close()
print("saved", OUT)
