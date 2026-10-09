import csv, math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Arc

import matplotlib.font_manager as fm
for _p in ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"):
    fm.fontManager.addfont(_p)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIG, DAT = f"{R}/fig", f"{R}/data"
C_B0, C_C1 = "#4C72B0", "#DD8452"
COL = {"success": "#2E7D32", "slip": "#C62828", "drop_on_plate": "#EF9A9A",
       "empty": "#757575", "no_release": "#F9A825"}
LAB = {"success": "성공 (정상 해제)", "slip": "이송 중 놓침", "drop_on_plate": "놓쳤으나 접시 위로 떨어짐",
       "empty": "헛잡음", "no_release": "미해제"}

# ------------------------------------------------------------------ 배치 좌표 (롤아웃 로그에서 확인된 세트)
bowl = {1: (0.637, 0.328), 2: (0.62, 0.264), 3: (0.601, 0.293), 4: (0.63, 0.253), 5: (0.632, 0.296),
        6: (0.647, 0.293), 7: (0.599, 0.31), 8: (0.587, 0.243), 9: (0.578, 0.245), 10: (0.665, 0.283),
        15: (0.668, 0.32), 16: (0.593, 0.271), 17: (0.601, 0.289), 18: (0.62, 0.319), 19: (0.597, 0.275),
        20: (0.618, 0.285), 21: (0.578, 0.265), 22: (0.644, 0.322), 23: (0.603, 0.297), 24: (0.586, 0.258),
        25: (0.613, 0.242), 26: (0.657, 0.318), 27: (0.598, 0.305), 28: (0.615, 0.288), 29: (0.602, 0.288),
        30: (0.653, 0.303)}
plate = {1: (0.701, 0.061), 2: (0.767, 0.086), 3: (0.763, 0.152), 4: (0.709, 0.067), 5: (0.748, 0.089),
         6: (0.736, 0.079), 7: (0.721, 0.078), 8: (0.743, 0.088), 9: (0.753, 0.104), 10: (0.767, 0.07),
         15: (0.764, 0.129), 16: (0.755, 0.088), 17: (0.709, 0.061), 18: (0.736, 0.111), 19: (0.749, 0.105),
         20: (0.764, 0.08), 21: (0.701, 0.093), 22: (0.768, 0.109), 23: (0.715, 0.07), 24: (0.744, 0.112),
         25: (0.72, 0.073), 26: (0.729, 0.121), 27: (0.759, 0.094), 28: (0.764, 0.137), 29: (0.715, 0.087),
         30: (0.752, 0.069)}

# ------------------------------------------------------------------ B0 (2026-09-28, FR5-GR00T-Benchmark RESULTS 9절)
b0_rows = [
    (1, "success", "S9", 3.9, 1.7, 0.610, 0.162, 0.064, 0.099), (2, "success", "S9", 5.6, 3.1, 0.617, 0.171, 0.050, 0.088),
    (3, "success", "S9", 5.3, 3.3, 0.593, 0.195, 0.051, 0.134), (4, "success", "S9", 5.6, 3.2, 0.599, 0.153, 0.050, 0.081),
    (5, "success", "S9", 4.9, 2.5, 0.600, 0.168, 0.054, 0.117), (6, "empty", "S3", 0.0, None, 0.606, 0.152, 0.050, None),
    (7, "success", "S9", 5.5, 3.1, 0.571, 0.171, 0.050, 0.079), (8, "slip", "S7", 3.3, 3.3, 0.628, 0.173, 0.050, None),
    (9, "success", "S9", 5.5, 3.2, 0.595, 0.168, 0.050, 0.071), (10, "slip", "S7", 11.0, 9.2, 0.651, 0.163, 0.050, None),
    (11, "slip", "S7", 4.6, 4.6, 0.605, 0.171, 0.056, None), (12, "slip", "S7", 5.6, 5.6, 0.576, 0.188, 0.050, None),
    (13, "empty", "S3", 0.0, None, 0.640, 0.203, 0.051, None), (14, "success", "S9", 4.6, 2.4, 0.604, 0.138, 0.054, 0.090),
    (15, "slip", "S7", 5.6, 5.6, 0.612, 0.210, 0.050, None), (16, "slip", "S7", 4.2, 4.2, 0.589, 0.165, 0.060, None),
    (17, "success", "S9", 5.4, 3.0, 0.599, 0.176, 0.050, 0.102), (18, "empty", "S3", 0.0, None, 0.613, 0.171, 0.051, None),
    (19, "empty", "S3", 0.0, None, 0.594, 0.168, 0.050, None), (20, "empty", "S3", 0.0, None, 0.624, 0.204, 0.050, None),
    (21, "success", "S9", 4.4, 2.2, 0.606, 0.136, 0.056, 0.100), (22, "success", "S9", 5.1, 2.7, 0.640, 0.182, 0.053, 0.111),
    (23, "success", "S9", 5.6, 3.2, 0.632, 0.204, 0.050, 0.106), (24, "slip", "S7", 3.8, 3.8, 0.611, 0.141, 0.067, None),
    (25, "slip", "S7", 3.7, 3.7, 0.602, 0.150, 0.071, None), (26, "empty", "S3", 0.0, None, 0.615, 0.186, 0.055, None),
    (27, "empty", "S3", 0.0, None, 0.589, 0.163, 0.052, None), (28, "no_release", "S8", 5.5, 3.1, 0.602, 0.175, 0.050, None),
    (29, "slip", "S7", 4.7, 4.7, 0.602, 0.166, 0.055, None), (30, "success", "S9", 5.2, 2.7, 0.642, 0.188, 0.052, 0.114)]
B0 = {r[0]: dict(set=r[0], outcome=r[1], stage=r[2], width=r[3], slide=r[4], gx=r[5], gy=r[6], gz=r[7], rel_z=r[8]) for r in b0_rows}

# ------------------------------------------------------------------ C1 (2026-10-05, bench_runner.csv + 롤아웃 로그)
# (set, 기록 판정, 단계, 기록 원인, 폭 m, 밀림 mm, 파지 xyz, 해제 위치, end_why, 기록기)
c1_raw = [
    (1, "f", "S7", "off_target", 0.0056, None, (0.584, 0.189, 0.050), None, "lost", "v1"),
    (2, "f", "S7", "off_target", 0.0056, 5.6, (0.578, 0.194, 0.050), None, "lost", "v1"),
    (3, "f", "S7", "off_target", 0.0056, 5.6, (0.572, 0.184, 0.050), None, "lost", "v1"),
    (4, "s", "S9", "none", 0.0056, 3.1, (0.598, 0.166, 0.050), (0.706, 0.021, 0.111), "released", "v1"),
    (5, "s", "S9", "none", 0.0056, 3.1, (0.565, 0.174, 0.050), (0.739, 0.044, 0.102), "released", "v1"),
    (6, "s", "S9", "none", 0.0050, 2.6, (0.602, 0.190, 0.053), (0.734, 0.054, 0.103), "released", "v1"),
    (7, "f", "S7", "off_target", 0.0056, 5.6, (0.561, 0.177, 0.050), None, "lost", "v1"),
    (8, "s", "S9", "none", 0.0056, 3.1, (0.592, 0.172, 0.050), (0.749, 0.025, 0.106), "released", "v1"),
    (9, "f", "S8", "no_release", 0.0055, 5.5, (0.584, 0.178, 0.050), None, "lost", "v1"),
    (10, "f", "S7", "off_target", 0.0045, 4.5, (0.641, 0.209, 0.057), None, "lost", "v1"),
    (11, "s", "S9", "none", 0.0046, 3.0, (0.602, 0.193, 0.056), (0.710, 0.054, 0.109), "released", "v3"),
    (12, "s", "S9", "none", 0.0056, 3.1, (0.575, 0.175, 0.050), (0.743, 0.007, 0.093), "released", "v3"),
    (13, "f", "S7", "slip", 0.0053, 5.3, (0.628, 0.173, 0.052), None, "lost", "v3"),
    (14, "s", "S9", "none", 0.0053, 4.2, (0.584, 0.168, 0.051), None, "lost", "v3"),
    (15, "f", "S7", "slip", 0.0056, 5.6, (0.611, 0.224, 0.050), None, "lost", "v3"),
    (16, "s", "S9", "none", 0.0055, 3.3, (0.589, 0.180, 0.050), (0.726, 0.037, 0.102), "released", "v3"),
    (17, "f", "S7", "slip", 0.0055, 5.5, (0.597, 0.191, 0.050), None, "lost", "v3"),
    (18, "s", "S9", "none", 0.0043, 2.1, (0.611, 0.198, 0.059), (0.719, 0.026, 0.105), "released", "v3"),
    (19, "f", "S7", "slip", 0.0046, 4.6, (0.582, 0.161, 0.056), None, "lost", "v3"),
    (20, "s", "S9", "none", 0.0052, 5.2, (0.587, 0.186, 0.051), None, "lost", "v3"),
    (21, "s", "S9", "none", 0.0049, 4.9, (0.598, 0.185, 0.054), None, "lost", "v3"),
    (22, "s", "S9", "none", 0.0055, 5.5, (0.593, 0.192, 0.050), None, "lost", "v3"),
    (23, "s", "S9", "none", 0.0056, 5.6, (0.590, 0.166, 0.050), None, "lost", "v3"),
    (24, "f", "S7", "slip", 0.0056, 5.6, (0.585, 0.136, 0.050), None, "lost", "v3"),
    (25, "s", "S9", "none", 0.0052, 5.2, (0.594, 0.186, 0.051), None, "lost", "v3"),
    (26, "f", "S7", "slip", 0.0054, 5.4, (0.613, 0.184, 0.051), None, "lost", "v3"),
    (27, "f", "S3", "empty", 0.0000, None, (0.594, 0.176, 0.050), None, "operator", "v3"),
    (28, "s", "S9", "none", 0.0055, 3.4, (0.607, 0.172, 0.050), (0.739, 0.031, 0.112), "released", "v3"),
    (29, "f", "S7", "slip", 0.0060, 6.0, (0.589, 0.167, 0.050), None, "lost", "v3"),
    (30, "f", "S8", "slip", 0.0055, 5.5, (0.683, 0.155, 0.050), None, "lost", "v3")]


def c1_outcome(r):
    s, v, stg, fail, w, sl, g, pl, why, ver = r
    if why == "released":
        return "success"
    if fail == "empty":
        return "empty"
    if fail == "no_release":
        return "no_release"
    if v == "s":
        return "drop_on_plate"
    return "slip"


C1 = {}
for r in c1_raw:
    s, v, stg, fail, w, sl, g, pl, why, ver = r
    C1[s] = dict(set=s, rec_verdict=v, rec_stage=stg, rec_failure=fail, width=w * 1000, slide=sl,
                 gx=g[0], gy=g[1], gz=g[2], place=pl, end_why=why, runner=ver, outcome=c1_outcome(r))

# ------------------------------------------------------------------ CSV 저장
with open(f"{DAT}/b0_20260928.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["set", "outcome", "stage", "grip_width_mm", "slide_mm", "grasp_x", "grasp_y", "grasp_z", "release_z"])
    for s in range(1, 31):
        d = B0[s]
        w.writerow([s, d["outcome"], d["stage"], d["width"], "" if d["slide"] is None else d["slide"],
                    d["gx"], d["gy"], d["gz"], "" if d["rel_z"] is None else d["rel_z"]])
with open(f"{DAT}/c1_main_20261005.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["set", "outcome_strict", "recorded_verdict", "recorded_stage", "recorded_failure", "end_why",
                "grip_width_mm", "slide_mm", "grasp_x", "grasp_y", "grasp_z", "place_x", "place_y", "place_z",
                "runner", "bowl_x", "bowl_y", "plate_x", "plate_y"])
    for s in range(1, 31):
        d = C1[s]
        pl = d["place"] or ("", "", "")
        bx, by = bowl.get(s, ("", ""))
        px, py = plate.get(s, ("", ""))
        w.writerow([s, d["outcome"], d["rec_verdict"], d["rec_stage"], d["rec_failure"], d["end_why"],
                    round(d["width"], 1), "" if d["slide"] is None else d["slide"], d["gx"], d["gy"], d["gz"],
                    *pl, d["runner"], bx, by, px, py])
with open(f"{DAT}/yaw_test_20261005.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["tag", "set", "yaw_off_deg", "grasp_dz", "grasp_z", "grip_width_mm", "slide_mm", "result"])
    w.writerows([["yaw0", 4, 0, 0, 0.067, 3.7, 1.5, "released"],
                 ["yaw15", 1, -15, 0, 0.053, 5.1, 2.7, "released"],
                 ["yaw15", 2, -15, 0, 0.070, 3.9, 3.9, "lost"],
                 ["yaw15", 3, -15, 0, 0.064, 4.0, 4.0, "lost"]])


# ------------------------------------------------------------------ 통계
def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def binom_two_sided(b, c):              # McNemar 정확검정
    n, k = b + c, min(b, c)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def fisher_two_sided(a, b, c, d):
    n1, n2, k = a + b, c + d, a + c
    N = n1 + n2
    def hp(x):
        return math.comb(n1, x) * math.comb(n2, k - x) / math.comb(N, k)
    p0 = hp(a)
    return sum(hp(x) for x in range(max(0, k - n2), min(k, n1) + 1) if hp(x) <= p0 + 1e-12)


sets = range(1, 31)
b0_grasp = {s for s in sets if B0[s]["outcome"] != "empty"}
c1_grasp = {s for s in sets if C1[s]["outcome"] != "empty"}
b0_succ = {s for s in sets if B0[s]["outcome"] == "success"}
c1_succ = {s for s in sets if C1[s]["outcome"] == "success"}
stats = {
    "grasp": (len(b0_grasp), len(c1_grasp)),
    "success": (len(b0_succ), len(c1_succ)),
    "grasp_mcnemar": binom_two_sided(len(b0_grasp - c1_grasp), len(c1_grasp - b0_grasp)),
    "grasp_disc": (len(b0_grasp - c1_grasp), len(c1_grasp - b0_grasp)),
    "succ_mcnemar": binom_two_sided(len(b0_succ - c1_succ), len(c1_succ - b0_succ)),
    "succ_disc": (len(b0_succ - c1_succ), len(c1_succ - b0_succ)),
    "grasp_fisher": fisher_two_sided(len(c1_grasp), 30 - len(c1_grasp), len(b0_grasp), 30 - len(b0_grasp)),
    "succ_fisher": fisher_two_sided(len(c1_succ), 30 - len(c1_succ), len(b0_succ), 30 - len(b0_succ)),
}

# ------------------------------------------------------------------ 그림 1: 요약 비율
fig, ax = plt.subplots(figsize=(7.2, 3.8))
metrics = [("파지 성공\n(S5)", len(b0_grasp), 30, len(c1_grasp), 30),
           ("최종 성공\n(정상 해제)", len(b0_succ), 30, len(c1_succ), 30),
           ("문 뒤 유지\n(파지한 판 중)", len(b0_succ), len(b0_grasp), len(c1_succ), len(c1_grasp))]
x = np.arange(len(metrics)); wd = 0.36
for i, (name, kb, nb, kc, nc) in enumerate(metrics):
    for off, k, n, col, lab in ((-wd / 2, kb, nb, C_B0, "B0  FR5 205판 (09-28)"), (wd / 2, kc, nc, C_C1, "C1  FR5 205 + FR3 200판 (10-05)")):
        p = k / n; lo, hi = wilson(k, n)
        ax.bar(i + off, p, wd, color=col, label=lab if i == 0 else None)
        ax.errorbar(i + off, p, yerr=[[p - lo], [hi - p]], color="black", capsize=3, lw=1)
        ax.text(i + off, hi + 0.03, f"{k}/{n}", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels([m[0] for m in metrics])
ax.set_ylim(0, 1.15); ax.set_ylabel("비율")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="upper right", fontsize=8.5)
ax.set_title("같은 30세트 배치, 같은 실행 설정 (규칙 A 켬, 힘 70 %)", fontsize=10)
fig.tight_layout(); fig.savefig(f"{FIG}/fig01_summary.png", dpi=160); plt.close(fig)

# ------------------------------------------------------------------ 그림 2: 세트별 결과 격자
fig, ax = plt.subplots(figsize=(11, 2.3))
for row, (name, D) in enumerate((("B0", B0), ("C1", C1))):
    for s in sets:
        o = D[s]["outcome"]
        ax.add_patch(Rectangle((s - 0.45, 1 - row - 0.4), 0.9, 0.8, color=COL[o]))
    ax.text(0.2, 1 - row, name, ha="right", va="center", fontsize=11, fontweight="bold")
for s in sets:
    ax.text(s, -0.6, str(s), ha="center", va="center", fontsize=7.5, color="#444")
ax.set_xlim(-0.6, 30.6); ax.set_ylim(-0.9, 1.6); ax.axis("off")
handles = [Rectangle((0, 0), 1, 1, color=COL[k]) for k in ("success", "empty", "slip", "drop_on_plate", "no_release")]
ax.legend(handles, [LAB[k] for k in ("success", "empty", "slip", "drop_on_plate", "no_release")],
          ncol=5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.12), fontsize=8.5)
fig.tight_layout(); fig.savefig(f"{FIG}/fig02_paired_sets.png", dpi=160); plt.close(fig)

# ------------------------------------------------------------------ 그림 3: 실패 유형
fig, ax = plt.subplots(figsize=(6.4, 3.4))
order = ["success", "empty", "slip", "drop_on_plate", "no_release"]
for i, (name, D) in enumerate((("B0 (09-28)", B0), ("C1 (10-05)", C1))):
    left = 0
    for k in order:
        n = sum(1 for s in sets if D[s]["outcome"] == k)
        if n:
            ax.barh(i, n, left=left, color=COL[k], label=LAB[k] if i == 1 or k not in ("drop_on_plate",) else None)
            ax.text(left + n / 2, i, str(n), ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        left += n
ax.set_yticks([0, 1]); ax.set_yticklabels(["B0 (09-28)", "C1 (10-05)"]); ax.invert_yaxis()
ax.set_xlim(0, 30); ax.set_xlabel("판 수")
ax.spines[["top", "right"]].set_visible(False)
h, l = ax.get_legend_handles_labels(); uniq = dict(zip(l, h))
ax.legend(uniq.values(), uniq.keys(), frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3)
fig.tight_layout(); fig.savefig(f"{FIG}/fig03_failure_types.png", dpi=160); plt.close(fig)

# ------------------------------------------------------------------ 그림 4: 밀림과 유지
fig, ax = plt.subplots(figsize=(6.4, 3.8))
groups = [("B0\n유지", [B0[s]["slide"] for s in sets if B0[s]["outcome"] in ("success", "no_release")], C_B0),
          ("B0\n놓침", [B0[s]["slide"] for s in sets if B0[s]["outcome"] == "slip"], C_B0),
          ("C1\n유지", [C1[s]["slide"] for s in sets if C1[s]["outcome"] == "success"], C_C1),
          ("C1\n놓침", [C1[s]["slide"] for s in sets if C1[s]["outcome"] in ("slip", "drop_on_plate", "no_release") and C1[s]["slide"] is not None], C_C1)]
rng = np.random.default_rng(0)
for i, (name, v, col) in enumerate(groups):
    v = [a for a in v if a is not None]
    ax.scatter(i + rng.uniform(-0.12, 0.12, len(v)), v, color=col, alpha=0.8, s=28, edgecolor="white", lw=0.5)
    ax.text(i, -0.6, f"n={len(v)}", ha="center", fontsize=8.5, color="#555")
ax.axhline(4.0, color="#C62828", ls="--", lw=1)
ax.text(3.45, 4.1, "4 mm", color="#C62828", fontsize=9, ha="right")
ax.set_xticks(range(4)); ax.set_xticklabels([g[0] for g in groups])
ax.set_ylabel("밀림 [mm]  (닫은 직후 폭 − 이송 중 최소 폭)"); ax.set_ylim(-1, 10)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("밀림 4 mm 이상이면 B0·C1 모두 놓쳤다 (B0는 3.3~3.8 mm에서 놓친 판도 3개)", fontsize=9.5)
fig.tight_layout(); fig.savefig(f"{FIG}/fig04_slide.png", dpi=160); plt.close(fig)

# ------------------------------------------------------------------ 그림 5: 파지 높이와 폭 — 시연 대 롤아웃
fig, ax = plt.subplots(figsize=(6.6, 4.2))
ax.add_patch(Rectangle((47.9, 1.8), 69.0 - 47.9, 3.7 - 1.8, color="#9E9E9E", alpha=0.25, lw=0))
ax.scatter([58.6], [2.2], marker="*", s=160, color="#616161", zorder=3, label="시연 205판 중앙 (음영: 10–90 %)")
for name, D, col in (("B0", B0, C_B0), ("C1", C1, C_C1)):
    held = [s for s in sets if D[s]["outcome"] in ("success", "no_release") and D[s]["width"] > 0
            and not (name == "C1" and D[s]["outcome"] == "no_release")]
    lost = [s for s in sets if D[s]["outcome"] in ("slip", "drop_on_plate") or (name == "C1" and D[s]["outcome"] == "no_release")]
    ax.scatter([D[s]["gz"] * 1000 for s in held], [D[s]["width"] for s in held], color=col, s=34, label=f"{name} 유지")
    ax.scatter([D[s]["gz"] * 1000 for s in lost], [D[s]["width"] for s in lost], facecolor="none", edgecolor=col, s=34, lw=1.3, label=f"{name} 놓침")
ax.set_xlabel("파지 높이 z [mm]"); ax.set_ylabel("문 직후 그리퍼 폭 [mm, 제어판 pos 환산]")
ax.set_xlim(45, 75); ax.set_ylim(0, 12)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper right")
ax.set_title("같은 높이에서 롤아웃은 시연보다 넓게 문다", fontsize=10)
fig.tight_layout(); fig.savefig(f"{FIG}/fig05_grip_height_width.png", dpi=160); plt.close(fig)

# ------------------------------------------------------------------ 그림 6: 놓침 비율 — 시연 대 롤아웃
fig, ax = plt.subplots(figsize=(5.6, 3.4))
vals = [("시연\n205판", 3, 205, "#9E9E9E"),
        ("B0 롤아웃\n09-28", sum(1 for s in sets if B0[s]["outcome"] == "slip"), len(b0_grasp), C_B0),
        ("C1 롤아웃\n10-05", sum(1 for s in sets if C1[s]["outcome"] in ("slip", "drop_on_plate", "no_release")), len(c1_grasp), C_C1)]
for i, (n_, k, n, col) in enumerate(vals):
    p = k / n; lo, hi = wilson(k, n)
    ax.bar(i, p, 0.55, color=col)
    ax.errorbar(i, p, yerr=[[p - lo], [hi - p]], color="black", capsize=3, lw=1)
    ax.text(i, hi + 0.03, f"{k}/{n}", ha="center", fontsize=9)
ax.set_xticks(range(3)); ax.set_xticklabels([v[0] for v in vals])
ax.set_ylabel("물고 나서 놓친 비율"); ax.set_ylim(0, 1)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(f"{FIG}/fig06_drop_rate.png", dpi=160); plt.close(fig)

# ------------------------------------------------------------------ 그림 7: 공간 추종 (B0 대 C1, 같은 26세트)
common = sorted(bowl)
fig, axes = plt.subplots(1, 2, figsize=(9, 3.9))
track = {}
for ax, k, lab in ((axes[0], 0, "x"), (axes[1], 1, "y")):
    for name, D, col in (("B0", B0, C_B0), ("C1", C1, C_C1)):
        bx = np.array([bowl[s][k] for s in common]); gx = np.array([D[s]["gx" if k == 0 else "gy"] for s in common])
        a, b = np.polyfit(bx, gx, 1); r = np.corrcoef(bx, gx)[0, 1]
        track[(name, lab)] = (a, r)
        ax.scatter(bx, gx, color=col, s=24, alpha=0.85)
        xs = np.linspace(bx.min(), bx.max(), 10)
        ax.plot(xs, a * xs + b, color=col, lw=1.6, label=f"{name}  기울기 {a:.2f} (r = {r:.2f})")
    ax.set_xlabel(f"그릇 중심 {lab} [m]"); ax.set_ylabel(f"파지점 {lab} [m]")
    ax.spines[["top", "right"]].set_visible(False); ax.legend(frameon=False, fontsize=8.5)
fig.suptitle("공간 추종 — 그릇이 움직일 때 파지점이 따라가는 정도 (세트 1–10, 15–30)", fontsize=10)
fig.tight_layout(); fig.savefig(f"{FIG}/fig07_tracking.png", dpi=160); plt.close(fig)

# ------------------------------------------------------------------ 그림 8: 학습량
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ep = [("B0\n6k / FR5", 9.16, C_B0), ("FR5 12k\n(과적합)", 18.32, "#9E9E9E"), ("C1 6k\n(보조)", 4.39, "#F4C7A8"), ("C1 12k\n(주 비교)", 8.78, C_C1)]
for i, (n, v, col) in enumerate(ep):
    ax.bar(i, v, 0.55, color=col); ax.text(i, v + 0.4, f"{v:.1f}", ha="center", fontsize=9)
ax.axhline(18.32, color="#C62828", ls="--", lw=1); ax.text(3.4, 18.7, "과적합이 확인된 수준", color="#C62828", fontsize=8.5, ha="right")
ax.set_xticks(range(4)); ax.set_xticklabels([e[0] for e in ep]); ax.set_ylabel("에폭 (스텝 × 16 ÷ 프레임 수)")
ax.set_ylim(0, 21); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(f"{FIG}/fig08_epochs.png", dpi=160); plt.close(fig)

# ------------------------------------------------------------------ 그림 9: 정합 — 손끝 방향과 높이
fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), gridspec_kw={"width_ratios": [1, 1.2]})
ax = axes[0]; ax.set_aspect("equal"); ax.axis("off")
ax.add_patch(plt.Circle((0, 0), 1, fill=False, color="#BDBDBD"))
for ang, col, lab in ((2.2, C_B0, "FR3 시작 자세 +2.2°"), (-78.3, C_C1, "FR5 시작 자세 −78.3°")):
    t = math.radians(ang)
    ax.annotate("", xy=(math.cos(t), math.sin(t)), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=2))
    ax.text(1.12 * math.cos(t), 1.12 * math.sin(t) + (0.08 if ang > 0 else -0.12), lab, color=col, fontsize=8.5,
            ha="left" if ang > 0 else "center")
ax.add_patch(Arc((0, 0), 0.7, 0.7, theta1=-78.3, theta2=2.2, color="#555"))
ax.text(0.42, -0.42, "80.4°", fontsize=9, color="#333")
ax.set_xlim(-1.3, 1.9); ax.set_ylim(-1.35, 1.25)
ax.set_title("툴 x축 방위 (각 데이터 좌표계, 접근축 둘레)", fontsize=9.5)
ax = axes[1]
bars = [("FR3 원본", 76.7, C_B0), ("FR3 정합본", 57.5, "#90CAF9"), ("FR5", 57.5, C_C1)]
for i, (n, v, col) in enumerate(bars):
    ax.bar(i, v, 0.55, color=col); ax.text(i, v + 1.2, f"{v:.1f}", ha="center", fontsize=9)
ax.set_xticks(range(3)); ax.set_xticklabels([b[0] for b in bars]); ax.set_ylabel("처음 닫는 순간 TCP z 중앙값 [mm]")
ax.set_ylim(0, 90); ax.spines[["top", "right"]].set_visible(False)
ax.set_title("z 오프셋 −19.2 mm", fontsize=9.5)
fig.tight_layout(); fig.savefig(f"{FIG}/fig09_alignment.png", dpi=160); plt.close(fig)

# ------------------------------------------------------------------ 결과 숫자 출력 (문서 작성용)
print(stats)
for k, v in track.items():
    print(k, round(v[0], 3), round(v[1], 3))
for name, D in (("B0", B0), ("C1", C1)):
    print(name, {k: sum(1 for s in sets if D[s]["outcome"] == k) for k in order})
held_wide = lambda D, ok: sum(1 for s in sets if D[s]["width"] >= 5.4 and D[s]["outcome"] in ok)
print("wide>=5.4 B0 held", held_wide(B0, ("success", "no_release")), "lost", held_wide(B0, ("slip",)))
print("wide>=5.4 C1 held", held_wide(C1, ("success",)), "lost", held_wide(C1, ("slip", "drop_on_plate", "no_release")))
