# ref

작업 중 다른 대화·저장소에서 넘겨받거나 따로 만든 정리 문서다. 본문과 숫자가 다른 곳은 본문(docs/01~10)이 나중에 확인한 값이다.

| 파일 | 내용 |
|---|---|
| `fr3_fr5_conversion_values.md` | FR5 작업 프레임(−77.2°), 공구 167.6 mm, DH, AG-95 변환, 데이터 규약, 파지점 치우침 (2026-09-28 기준) |
| `handover_transfer.md` | FR3 ↔ FR5 전이 인계 메모 (확정 사항, 보정 항목, 물리 규격 차이, 데이터 위치) |
| `fr3_fr5_extract_request.md` | 다른 채팅·기계에서 필요한 정보를 뽑기 위한 요청서 양식 |

본문에서 바로잡은 값:

- 인계 메모의 FR3 파지 높이 0.0875 m는 기준이 다른 값이다. 처음 닫는 순간 TCP z 중앙값은 0.0767 m이고, z 보정은 −19.2 mm로 했다.
- 손끝 자세 차이는 인계 메모의 약 77°가 아니라 시작 자세 평균끼리 맞춘 80.4°를 썼다.
- 인계 메모의 "FR3 데이터 위치 확인 필요"는 FR3 PC의 `~/.cache/huggingface/lerobot/local/task6_franka_v5`와 원본 `~/openvla_franka/task6/collect/episodes_groot`로 확인됐다.
