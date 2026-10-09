#!/usr/bin/env bash
# 읽기 전용 탐색 — 기존 파일을 만들거나 수정하지 않는다 (FR3 제어 PC에서 실행)
ROOTS=""
for d in "$HOME" /data /data1 /data2 /mnt /media /srv; do [ -d "$d" ] && ROOTS="$ROOTS $d"; done
f() { find $ROOTS -maxdepth 8 \( -name node_modules -o -name site-packages -o -name .git -o -name pkgs -o -name __pycache__ -o -name '.Trash-*' \) -prune -o "$@" -print 2>/dev/null; }
grp() { sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -${1:-20}; }

echo "== 탐색 루트:$ROOTS"
echo "== 디스크"; df -h -x tmpfs -x devtmpfs -x squashfs -x overlay 2>/dev/null
echo "== enp3s0 이웃 장치"; ip neigh show dev enp3s0
echo "== USB 장치 (카메라/U2D2 후보)"; lsusb 2>/dev/null | grep -Ei 'intel|realsense|stereolabs|zed|logitech|camera|future tech|ftdi|robotis' || echo "없음"
echo "== git 저장소 (경로 | remote | 마지막 커밋)"
find "$HOME" -maxdepth 5 -name .git -type d 2>/dev/null | while read -r g; do r=${g%/.git}; echo "$r | $(git -C "$r" remote get-url origin 2>/dev/null) | $(git -C "$r" log -1 --format=%cs 2>/dev/null)"; done | head -40
echo "== conda 환경"; ls -d "$HOME"/{miniconda3,anaconda3,miniforge3,mambaforge}/envs/* 2>/dev/null || echo "없음"
echo "== LeRobot meta/info.json"; f -type f -path '*/meta/info.json' | head -30
echo "== HDF5 (디렉터리별 개수)"; f -type f \( -name '*.hdf5' -o -name '*.h5' \) | grp
echo "== zarr"; f -type d -name '*.zarr' | head -20
echo "== RLDS/TFDS"; f -type f \( -name 'dataset_info.json' -o -name '*.tfrecord*' \) | grp
echo "== rosbag/mcap"; f -type f \( -name '*.bag' -o -name '*.mcap' -o -name '*.db3' \) | grp
echo "== npz/npy/pkl (디렉터리별 개수)"; f -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.pkl' \) | grp
echo "== mp4 (디렉터리별 개수)"; f -type f -name '*.mp4' | grp
echo "== URDF/xacro"; f -type f \( -iname '*.urdf' -o -iname '*.xacro' \) | grep -Ei 'fr3|fr5|franka|panda|fairino' | head -30
echo "== 캘리브레이션 후보"; f -type f \( -iname '*calib*' -o -iname '*extrinsic*' -o -iname '*intrinsic*' -o -iname '*hand_eye*' -o -iname '*handeye*' \) | head -40
echo "== GELLO 관련 디렉터리"; f -type d -iname '*gello*' | head -20
