# tools

이 실험에서 실제로 돌린 스크립트다. 공개용으로 홈 경로는 `$HOME`·`~`로, 주소는 `TRAIN_SERVER_IP` 같은 자리표시로 바꿨다.
`dry_probe.py`의 `HOST` 기본값과 전송 명령의 주소·계정은 실행 전에 자기 환경 값으로 바꿔야 한다.
실행 순서는 [docs/10_runbook.md](../docs/10_runbook.md).

| 폴더 | 파일 | 실행 위치 | 하는 일 |
|---|---|---|---|
| 01_audit | `fr_discovery.sh` | FR3 PC | 데이터·저장소·카메라·캘리브레이션 파일 찾기 (읽기 전용) |
| | `fr_meta.sh` | FR3 PC | LeRobot 메타, state/action 샘플, 수집 설정, SPACE 폴더 출력 |
| | `fr_docs.sh` | FR3 PC | FR3 쪽 기록 문서, IK 코드, FR5 셀 URDF 앞부분 |
| | `phase1_check.py` | 워크스테이션 | 두 데이터의 시작·파지·배치 위치, 회전, 이동량, 그리퍼 요약 |
| 02_coverage | `coverage_check.py` | 워크스테이션 | 시작 프레임 합성 (중앙값·최솟값·어두운 물체 빈도) |
| | `gap_count.py` | 워크스테이션 | 그릇 자동 검출 — **실패한 방법**, 기록용 |
| | `fr3_sheet.py` | 워크스테이션 | FR3 시작 프레임 시트 (눈으로 판정) |
| 03_align_merge | `axis_check.py` | 워크스테이션 | FR3·FR5 축 방향 일치 확인, z 오프셋 |
| | `align_fr3.py` | 워크스테이션 | FR3 → FR5 규약 사본 생성과 검증 |
| | `feature_check.py` | 워크스테이션 | 합치기 전 메타데이터 비교 |
| | `set_robot_type.sh` | 워크스테이션 | 정합 사본 robot_type 변경, 전송 |
| | `merge_fr5_fr3.py` | 학습 서버 | `aggregate_datasets`로 합치고 검증 |
| 04_train_serve | `show_train_cfg.sh` | 학습 서버 | B0 학습 설정 평탄 출력 |
| | `pre_train_check.sh` | 학습 서버 | aggregate 규칙, GPU 상태 |
| | `train_c1.sh` | 학습 서버 | C1 학습 (12,000스텝, GPU1) |
| | `start_servers.sh` | 학습 서버 | 정책 서버 3개 (:8200 B0, :8201 C1-6k, :8202 C1-12k) |
| | `restart_c1.sh` | 학습 서버 | `norm_stats.json` 복사 후 C1 서버 재시작 |
| 05_robot | `patch_box.py` | 제어 PC | 롤아웃에 작업 상자 추가 |
| | `patch_yaw.py` | 제어 PC | 롤아웃에 손목 고정 회전(`YAW_OFF`) 옵션 추가 |
| | `probe_points.py` | 제어 PC | TCP 좌표 기록 (고정물 측정용, 미사용) |
| | `dry_probe.py` | 제어 PC | 같은 관측을 세 서버에 보내 예측 파지점 비교 |
| 06_analysis | `grasp_wrist.py` | 워크스테이션 | 시연 파지 순간 손목 yaw·tilt |
| | `demo_slip.py` | 워크스테이션 | 시연의 문 뒤 밀림·폭·높이 |
| | `make_figs.py` | 어디서나 | `data/*.csv` → `fig/fig01~09` (Noto Sans CJK 폰트 경로를 환경에 맞출 것) |

패치 스크립트 두 개는 기준 줄이 대상 파일에 정확히 한 번 있을 때만 고치고, 고치기 전에 `.bak_날짜_시각` 백업을 남긴다.
