# 제어 PC: fr5_rollout.py 에 손목 고정 회전 옵션(YAW_OFF, 도)을 넣는다. 기본값 0 이면 동작이 바뀌지 않는다.
import shutil, sys, time
P = sys.argv[1]
src = open(P).read()
A = 'R_HOLD = aa_to_R(canon(_aa0, REF_AA))'
if 'YAW_OFF' in src:
    sys.exit('이미 패치됨')
if src.count(A) != 1:
    sys.exit(f'기준 줄이 {src.count(A)}번 나옴 — 패치 중단')
i = src.index('\n', src.index(A)) + 1
add = ('YAW_OFF = float(os.environ.get("YAW_OFF", "0"))  # 시작 자세 대비 접근축 둘레 고정 회전(도). 시연 파지 순간 중앙 -15.1\n'
       'if YAW_OFF:\n'
       '    _c, _s = math.cos(math.radians(YAW_OFF)), math.sin(math.radians(YAW_OFF))\n'
       '    R_HOLD = R_HOLD @ np.array([[_c, -_s, 0.0], [_s, _c, 0.0], [0.0, 0.0, 1.0]])\n'
       '    print(f"손목 고정 회전 {YAW_OFF:+.1f}도 (접근축 둘레)")\n')
src = src[:i] + add + src[i:]
bak = f'{P}.bak_{time.strftime("%Y%m%d_%H%M%S")}'
shutil.copy(P, bak); open(P, 'w').write(src)
print('patched', P, '\nbackup ', bak)
