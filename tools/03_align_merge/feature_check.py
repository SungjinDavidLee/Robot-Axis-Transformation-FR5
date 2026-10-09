import json, sys
R = sys.argv[1]
a = json.load(open(f'{R}/data/fr3_task6_aligned_v1/meta/info.json'))
b = json.load(open(f'{R}/data/fr5_task6_abs/meta/info.json'))
for k in ['codebase_version', 'robot_type', 'fps', 'chunks_size', 'data_files_size_in_mb', 'video_files_size_in_mb', 'data_path', 'video_path']:
    print(f'{k:24s} FR3 {str(a.get(k)):42.42s} FR5 {b.get(k)}')
fa, fb = a['features'], b['features']
print('features 동일' if fa == fb else 'features 다름')
for k in sorted(set(fa) | set(fb)):
    if fa.get(k) != fb.get(k):
        print(' ', k); print('    FR3', fa.get(k)); print('    FR5', fb.get(k))
