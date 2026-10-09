# 5. 학습과 정책 서버

## 5.1 학습 설정

B0 체크포인트(`outputs/fr5_task6_abs/checkpoints/006000/pretrained_model/train_config.json`)의 설정을 그대로 쓰고
데이터셋·출력 경로·스텝만 바꿨다(`tools/04_train_serve/train_c1.sh`).

| 항목 | 값 |
|---|---|
| 정책 | LeRobot `groot`, GR00T N1.7 (`nvidia/GR00T-N1.7-3B`) |
| 시작 가중치 | `nvidia/gr00t17-lerobot-libero_spatial-640` |
| embodiment | `new_embodiment` 하나 |
| 학습 대상 | projector, diffusion model, vlln (LLM·비전 고정) |
| chunk / 실행 스텝 | 32 / 32 |
| action | `use_relative_actions=true`, 그리퍼 제외 |
| 정규화 | LeRobot 쪽 IDENTITY, GR00T 전처리기가 `meta/stats.json`을 사용 |
| 최적화 | AdamW lr 1e-4, weight decay 1e-5, cosine, warmup 500, grad clip 1.0 |
| batch / seed | 16 / 1000 |
| 영상 증강 | 끔 |
| 스텝 | **12,000** (주 비교), 6,000 저장 (보조) |

## 5.2 왜 12,000스텝인가

과적합은 스텝 수가 아니라 같은 샘플을 몇 번 보느냐로 정해진다.

| | 데이터 | 스텝 × batch | 에폭 | 결과 |
|---|---|---|---|---|
| B0 | FR5 10,482 프레임 | 6,000 × 16 | 9.2 | 기준선 |
| FR5 12k | FR5 10,482 프레임 | 12,000 × 16 | 18.3 | 과적합 — 공간 추종 0.35 → 0.1 |
| C1 12k | 합친 21,863 프레임 | 12,000 × 16 | 8.8 | 주 비교 |
| C1 6k | 합친 21,863 프레임 | 6,000 × 16 | 4.4 | 보조 |

C1을 6,000스텝으로 맞추면 FR5 데이터를 B0의 절반만 보게 된다. 그 상태에서 성능이 떨어지면 FR3가 해를 끼친 것인지
FR5를 덜 배운 것인지 가를 수 없다. 12,000스텝은 FR5 학습량을 B0와 같게 고정한다.

학습 로그에서 하나 더 알게 된 것이 있다.

```
WARNING sampler.py:89 Episode 172 has 31 frames but drop_n_first_frames=0 and drop_n_last_frames=31 removes all frames. Skipping.
```

32개 청크를 예측하려면 시작 프레임 뒤에 31프레임이 더 있어야 해서, 판마다 마지막 31프레임은 시작점으로 쓰이지 않는다.
172번(FR5, 길이 31)은 통째로 빠졌다. B0도 같은 설정이었으니 같은 판이 빠졌을 것이다. 실제 시작점이 될 수 있는 프레임은
FR5 약 4,127개, FR3 약 5,181개다. 이 기준으로 다시 세면 C1 12k가 FR5 프레임을 보는 횟수는 B0의 약 88 %다. 6k(44 %)보다
B0에 훨씬 가깝고 과적합 run보다 한참 아래라 결정은 그대로 뒀다.

**체크포인트 선택 규칙 (평가 전에 고정).** 주 비교는 C1-12k. `--dry` 추종 확인에서 C1-12k의 추종 기울기가 B0의 절반에
못 미치면 C1-6k로 바꾼다. 그 밖에는 바꾸지 않는다. dry 확인은 한 배치만 하고 접었고, 실물에서 C1-12k가 그릇을 따라
집는 것이 보여 C1-12k로 갔다.

## 5.3 학습 로그

```
시작   2026-10-03 19:07:30   GPU1 (RTX PRO 6000 Max-Q, 96 GB)   CUDA_VISIBLE_DEVICES=1
       dataset.num_frames=21863  dataset.num_episodes=405  learnable 1.62 B / total 3.14 B
step 50      loss 0.882   lr 5.1e-06   2.69 step/s   mem 35.95 GB
step 400     loss 0.044   lr 7.5e-05
step 12K     loss 0.006   epch 8.78
종료   2026-10-03 20:22:39   1:15:08
```

학습 동안에는 같은 GPU의 FR5 정책 서버를 껐다. 메모리는 충분했지만(여유 약 83 GB), 학습과 추론이 GPU 연산을 나눠 쓰면
추론 지연이 기준선 측정 때와 달라진다. GPU0은 다른 작업이 쓰고 있어 건드리지 않았다.

## 5.4 정책 서버

GPU1에 세 서버를 동시에 띄웠다(`start_servers.sh`). 서버 하나가 약 14 GB다.

```
:8200   B0       fr5_task6_abs/checkpoints/006000       REPO=local/fr5_task6_abs
:8201   C1-6k    fr5_fr3_task6_v1/checkpoints/006000    REPO=local/fr5_fr3_task6_v1
:8202   C1-12k   fr5_fr3_task6_v1/checkpoints/012000    REPO=local/fr5_fr3_task6_v1
```

서버(`fr5_policy_server.py`)는 환경 변수 `CKPT`와 `REPO`를 받는다. `REPO` 데이터셋의 메타데이터가 전처리·후처리기에
들어가므로 C1은 둘 다 바꿔야 한다. 체크포인트만 바꾸면 정규화 통계가 어긋나 출력 위치가 틀어질 수 있다.

### `ref_axis_angle = null` 문제

처음 띄웠을 때 C1 서버 두 개의 `/info`에서 `ref_axis_angle`이 `null`이었다.

```
30: ns = os.path.expanduser(f"~/.cache/huggingface/lerobot/local/{REPO.split('/')[-1]}/norm_stats.json")
31: REF_AA = json.load(open(ns))["ref_axis_angle"] if os.path.exists(ns) else None
```

서버는 이 값을 `REPO` 폴더의 `norm_stats.json`에서 읽는데, `aggregate_datasets`가 LeRobot 표준이 아닌 이 파일을 복사하지
않았다. 롤아웃은 이 값으로 현재 손끝 회전을 학습 때와 같은 축각 표현으로 맞춰 정책에 보내고, 시작 자세 유지 방향
(`R_HOLD`)을 정한다. 값이 없으면 회전 state가 학습 때와 다른 표현으로 들어간다.

FR5의 `norm_stats.json`을 합친 데이터셋 폴더에 복사하고 C1 서버를 다시 띄웠다(`restart_c1.sh`). FR3 정합도 같은 FR5
기준값으로 했고 합친 데이터셋 0번 판이 FR5 0번 판이라, 이 값이 맞다. 이후 세 서버 모두 같은 값을 냈다.

```
ref_axis_angle [-2.4425330290871115, 1.968073832566227, 0.0019828086840627443]   (:8200, :8201, :8202 모두)
```

롤아웃의 `SERVER` 기본값이 `:8200`(B0)이다. C1을 돌릴 때는 `SERVER`를 지정하고, 시작 화면의 ckpt 경로를 매번 확인했다.
