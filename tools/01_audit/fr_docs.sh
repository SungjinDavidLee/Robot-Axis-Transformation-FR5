#!/usr/bin/env bash
# FR3 쪽 기록 문서와 IK·URDF 파일 앞부분을 읽는다 (읽기 전용)
T6=$HOME/openvla_franka/task6
for f in "$T6/camera_before/NOTE.md" "$T6/FINDINGS.md" "$T6/collect/README.md"; do
  echo "===== $f"; head -30 "$f" 2>/dev/null
done
echo "===== ik_franka_fr5.py (앞 30줄)"; head -30 $HOME/Downloads/ik_franka_fr5.py 2>/dev/null
echo "===== fr5_cell.urdf 링크·조인트 이름"
grep -oE '<(link|joint) name="[^"]+"' $HOME/franka_web/robots/fr5/fr5_cell.urdf 2>/dev/null | head -30
