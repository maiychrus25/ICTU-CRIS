# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
import json,glob,os,collections
D=os.path.join(os.path.dirname(__file__),'out')
def load(t):
    p=os.path.join(D,f'{t}.jsonl')
    return [json.loads(l) for l in open(p,encoding='utf-8')] if os.path.exists(p) else []
print("# Kho dữ liệu repository.ictu.edu.vn — thống kê nhanh\n")
for t in ['bai-bao','do-an','luan-van','luan-an','hoc-lieu-so','giang-vien']:
    r=load(t); print(f"- {t}: {len(r)} bản ghi")
print()
bb=load('bai-bao')
if bb:
    yr=collections.Counter(x['year'] for x in bb if x.get('year'))
    ty=collections.Counter(x['pub_type'] for x in bb if x.get('pub_type'))
    print("## Bài báo theo năm:", dict(sorted(yr.items(),reverse=True)))
    print("## Bài báo theo loại (top10):", ty.most_common(10))
gv=load('giang-vien')
if gv:
    rk=collections.Counter(x.get('rank') for x in gv)
    dg=collections.Counter(x.get('degree') for x in gv)
    em=sum(1 for x in gv if x.get('email'))
    print(f"## Giảng viên: {len(gv)} | có email: {em} | học hàm: {dict(rk)} | học vị: {dict(dg)}")
