# 10. 재현 순서

실제로 실행한 순서대로 적는다. 기계는 `[이름]`으로 표시한다.

공개용으로 주소와 계정은 자리표시로 바꿨다. 실행할 때 자기 환경 값으로 바꾼다.

```
TRAIN_SERVER_IP   학습 서버 (정책 서버 :8200~8202)
WORKSTATION_IP    워크스테이션
FR3_PC_IP         FR3 제어 PC
FR3_ROBOT_IP      FR3 로봇 (FR3 제어 PC 직결 대역)
FR3_USER          FR3 제어 PC 계정
SERVER_USER       학습 서버 계정
```

```
[FR3 PC]    FR3-PC         FR3 제어 PC — 읽기만 함
[워크스테이션] WORKSTATION_IP     /home/data/fr_transfer (~/fr_transfer 링크)
[학습 서버]  TRAIN_SERVER_IP       ~/lerobot (.venv), GPU1 사용
[제어 PC]   Jetson AGX Thor     ~/fr5cap, conda env openvla_py310
```

## 1. 데이터 찾기 (읽기 전용)

```bash
[FR3 PC]  bash tools/01_audit/fr_discovery.sh 2>&1 | tee /tmp/fr_discovery.txt
[FR3 PC]  bash tools/01_audit/fr_meta.sh 2>&1 | tee /tmp/fr_meta.txt
[FR3 PC]  bash tools/01_audit/fr_docs.sh 2>&1 | tee /tmp/fr_docs.txt
```

## 2. 워크스테이션으로 복사

```bash
[워크스테이션]  mkdir -p /home/data/fr_transfer/data /home/data/fr_transfer/assets && ln -s /home/data/fr_transfer ~/fr_transfer
[워크스테이션]  rsync -av FR3_USER@FR3_PC_IP:~/.cache/huggingface/lerobot/local/{task6_franka_v5,fr5_task6_abs} ~/fr_transfer/data/
[워크스테이션]  rsync -av FR3_USER@FR3_PC_IP:~/franka_web/robots/fr5 FR3_USER@FR3_PC_IP:~/Downloads/ik_franka_fr5.py ~/fr_transfer/assets/
```

분석용 venv. Ubuntu 기본 파이썬에 `ensurepip`가 없으면 `sudo apt install python3.12-venv`.

```bash
[워크스테이션]  python3 -m venv --without-pip /home/data/fr_transfer/.venv
[워크스테이션]  curl -sS https://bootstrap.pypa.io/get-pip.py | /home/data/fr_transfer/.venv/bin/python
[워크스테이션]  /home/data/fr_transfer/.venv/bin/pip install --no-cache-dir -q numpy pandas pyarrow scipy matplotlib av
```

`--no-cache-dir`은 거의 찬 루트 디스크에 pip 캐시가 쌓이지 않게 하려는 것이다.

## 3. 분석

```bash
[워크스테이션]  PY=/home/data/fr_transfer/.venv/bin/python; R=/home/data/fr_transfer
[워크스테이션]  $PY tools/01_audit/phase1_check.py $R
[워크스테이션]  $PY tools/02_coverage/coverage_check.py $R
[워크스테이션]  $PY tools/02_coverage/gap_count.py $R        # 실패한 검출기 — 기록용
[워크스테이션]  $PY tools/02_coverage/fr3_sheet.py $R
[워크스테이션]  $PY tools/03_align_merge/axis_check.py $R
[워크스테이션]  $PY tools/06_analysis/grasp_wrist.py
[워크스테이션]  $PY tools/06_analysis/demo_slip.py
```

## 4. 정합과 전송

```bash
[워크스테이션]  $PY tools/03_align_merge/align_fr3.py $R
[워크스테이션]  $PY tools/03_align_merge/feature_check.py $R
[워크스테이션]  bash tools/03_align_merge/set_robot_type.sh
[워크스테이션]  rsync -av $R/data/fr3_task6_aligned_v1 SERVER_USER@TRAIN_SERVER_IP:~/.cache/huggingface/lerobot/local/
```

## 5. 합치기와 학습

```bash
[학습 서버]  bash tools/04_train_serve/show_train_cfg.sh          # B0 학습 설정 확인
[학습 서버]  bash tools/04_train_serve/pre_train_check.sh         # aggregate 규칙, GPU 상태
[학습 서버]  cd ~/lerobot && ./.venv/bin/python tools/03_align_merge/merge_fr5_fr3.py
[학습 서버]  kill <FR5 정책 서버 pid>                                # 학습 중 롤아웃 금지
[학습 서버]  bash tools/04_train_serve/train_c1.sh
[학습 서버]  tail -c 300 ~/lerobot/outputs/fr5_fr3_task6_v1.log; ls ~/lerobot/outputs/fr5_fr3_task6_v1/checkpoints/
```

`checkpoints/`에 `006000`과 `012000`이 모두 있고 `pgrep -af lerobot-train`이 비어 있으면 끝난 것이다.

## 6. 정책 서버

```bash
[학습 서버]  L=~/.cache/huggingface/lerobot/local; cp -n $L/fr5_task6_abs/norm_stats.json $L/fr5_fr3_task6_v1/
[학습 서버]  bash tools/04_train_serve/start_servers.sh && sleep 90
[학습 서버]  for p in 8200 8201 8202; do curl -s http://127.0.0.1:$p/info; echo; done
```

세 포트 모두 `ok: true`, `ckpt`·`repo` 짝이 맞고 `ref_axis_angle`이 `[-2.4425…, 1.9680…, 0.0019…]`로 같아야 한다.

## 7. 제어 PC 준비

```bash
[제어 PC]  conda activate openvla_py310
[제어 PC]  python3 tools/05_robot/patch_box.py ~/fr5cap/fr5_rollout.py && python3 -m py_compile ~/fr5cap/fr5_rollout.py
[제어 PC]  python3 tools/05_robot/patch_yaw.py ~/fr5cap/fr5_rollout.py && python3 -m py_compile ~/fr5cap/fr5_rollout.py
```

`/leader`에서 [리더 추종 시작]을 눌러야 배치 안내(`p`)와 롤아웃이 로봇을 움직인다.

## 8. 평가

```bash
[제어 PC]  PYTHONUNBUFFERED=1 SERVER=http://TRAIN_SERVER_IP:8202 LATCH_MODE=full GRASP_DZ=0.008 \
             python3 ~/fr5cap/bench_runner_v3.py --tag c1_main --from 1 --to 30 --force-cycle 70 2>&1 | tee -a ~/fr5cap/c1_main.log
```

세트마다 `p`(배치 안내) → `g`(그리퍼 초기화, 힘 70 확인) → `h`(초기 자세) → `s`(시작). 판정 키는
`s` 성공 / `f` 실패 / `x` 무효, 실패면 단계 1~9와 원인 a 정체 · b 헛잡음 · c 이송 중 놓침 · d 접시 밖 · e 미해제.
미끄러져 접시에 떨어진 판은 `f`·`c`다.

```bash
[제어 PC]  grep "c1_main_S" ~/fr5cap/bench_runner.csv
[제어 PC]  grep -E "^세트|그리퍼 닫음|물체를 놓쳤다|놓음\.|파지 후 밀림|기록:" ~/fr5cap/c1_main.log
```

B0는 `SERVER=...:8200`, 태그만 바꿔 같은 명령으로 돈다.

## 9. 그림

```bash
python3 tools/06_analysis/make_figs.py      # data/*.csv → fig/fig01~09
```
