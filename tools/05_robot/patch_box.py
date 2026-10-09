# 제어 PC: fr5_rollout.py 에 작업 상자를 넣는다. 기준 줄이 정확히 한 번 있을 때만 고치고 백업을 남긴다.
# 사용: python3 patch_box.py ~/fr5cap/fr5_rollout.py && python3 -m py_compile ~/fr5cap/fr5_rollout.py
import shutil, sys, time
P = sys.argv[1]
src = open(P).read()
A1 = 'GRIP_WAIT = float(os.environ.get("GRIP_WAIT", "0.8"))'
A2 = '            p_goal = np.array(a[:3], dtype=float)\n'
if 'BOX_XY' in src:
    sys.exit('이미 패치됨')
for a in (A1, A2):
    n = src.count(a)
    if n != 1:
        sys.exit(f'기준 줄이 {n}번 나옴 — 패치 중단: {a.strip()}')
i1 = src.index('\n', src.index(A1)) + 1
add1 = ('BOX_XY = [float(v) for v in os.environ.get("BOX_XY", "0.37,0.82,-0.08,0.44").split(",")]  # 작업 프레임 x0,x1,y0,y1 (m): FR5 시연 범위 + 1 cm\n'
        'BOX_ZMAX = float(os.environ.get("BOX_ZMAX", "0.39"))  # 목표 z 상한 (m)\n'
        'box_hits = 0\n')
src = src[:i1] + add1 + src[i1:]
add2 = ('            if not (BOX_XY[0] <= p_goal[0] <= BOX_XY[1] and BOX_XY[2] <= p_goal[1] <= BOX_XY[3] and p_goal[2] <= BOX_ZMAX):\n'
        '                box_hits += 1\n'
        '                print(f"  step {step:3d} k{k}: 작업 상자 밖 목표 {np.round(p_goal, 3)} -> 청크를 여기서 끊음 (누적 {box_hits})")\n'
        '                break\n')
i2 = src.index(A2) + len(A2)
src = src[:i2] + add2 + src[i2:]
bak = f'{P}.bak_{time.strftime("%Y%m%d_%H%M%S")}'
shutil.copy(P, bak)
open(P, 'w').write(src)
print('patched', P, '\nbackup ', bak)
