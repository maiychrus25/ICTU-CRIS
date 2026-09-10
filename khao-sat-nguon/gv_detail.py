#!/usr/bin/env python3
# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Kéo 410 trang hồ sơ giảng viên: số đếm công bố + định danh ngoài + danh sách công trình."""
import json,re,sys,time,html
sys.path.insert(0,'.'); import harvest as H
gv=[json.loads(l) for l in open('out/giang-vien.jsonl',encoding='utf-8')]
out=[]
for i,g in enumerate(gv,1):
    try:
        b=H.main_block(H.get(g['url']))
        t=H.text(b)
        rec=dict(g)
        for lab,key in [('Bài báo','n_baibao'),('Đồ án','n_doan'),('Luận văn ThS','n_luanvan'),
                        ('Luận án TS','n_luanan'),('Học liệu số','n_hoclieu')]:
            m=re.search(r'(\d+)\s*'+re.escape(lab)+r'(?!\s*\()',t)
            rec[key]=int(m.group(1)) if m else None
        for lab,key in [('Ngày sinh','dob'),('Điện thoại','phone'),('Giới tính','gender')]:
            m=re.search(re.escape(lab)+r'\s+([^\s].{0,40}?)(?=\s{2}|\s(?:Email|Điện thoại|ORCID|Google|Ngày|Giới|Học|Họ)|$)',t)
            rec[key]=m.group(1).strip() if m else None
        m=re.search(r'orcid\.org/([\d]{4}-[\d]{4}-[\d]{4}-[\dX]{4})',b)
        rec['orcid']=m.group(1) if m else None
        rec['scholar']=bool(re.search(r'scholar\.google',b))
        rec['linked_baibao']=sorted(set(re.findall(r'href="(https://repository\.ictu\.edu\.vn/bai-bao/[^"]+)"',b)))
        rec['linked_doan']=sorted(set(re.findall(r'href="(https://repository\.ictu\.edu\.vn/do-an/[^"]+)"',b)))
        rec['linked_luanvan']=sorted(set(re.findall(r'href="(https://repository\.ictu\.edu\.vn/luan-van/[^"]+)"',b)))
        out.append(rec)
    except Exception as e:
        out.append(dict(g,_error=str(e)))
    if i%50==0: print(f"  {i}/{len(gv)}",file=sys.stderr)
    time.sleep(0.3)
with open('out/giang-vien.details.jsonl','w',encoding='utf-8') as f:
    for r in out: f.write(json.dumps(r,ensure_ascii=False)+"\n")
print(f"-> out/giang-vien.details.jsonl ({len(out)})",file=sys.stderr)
