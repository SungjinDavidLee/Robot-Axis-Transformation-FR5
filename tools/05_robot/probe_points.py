#!/usr/bin/env python3
# 제어판에서 현재 TCP를 읽어 작업 프레임 좌표(m)로 기록한다. 로봇에 명령은 보내지 않는다.
# 고정물(인덕션·캐비닛·작업대 모서리) 좌표 측정용 — 아직 측정하지 않았다.
import csv, json, os, sys, time, urllib.request
sys.path.insert(0, os.path.expanduser("~/fr5cap/collect"))
import fr5cfg as C
PANEL = "http://127.0.0.1:8088"
OUT = os.path.expanduser("~/fr5cap/fixture_points.csv")

def state():
    with urllib.request.urlopen(PANEL + "/api/state", timeout=2) as r:
        return json.loads(r.read())

print("손끝을 지점에 대고 이름 입력 후 Enter. 빈 입력이면 종료.")
with open(OUT, "a", newline="") as f:
    w = csv.writer(f)
    while True:
        name = input("지점 이름> ").strip()
        if not name:
            break
        p, _, _ = C.tcp_to_task(state()["tcp"])
        row = [time.strftime("%F %T"), name] + [round(float(v), 4) for v in p]
        w.writerow(row); f.flush()
        print("  ", row)
print("saved", OUT)
