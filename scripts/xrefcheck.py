#!/usr/bin/env python3
"""Verify every cross-skill rule reference resolves to a rule that exists.

usage: xrefcheck.py [family-dir ...]   (default: every family under skills/)

Nothing else checks this. A reference to a rule that was renamed, retired, or never
written is invisible until a reader follows it.

References resolve **within a family**. A rule cites another rule in its own family's
vocabulary, so families are checked separately and one family's ids can never silently
satisfy another family's reference.
"""
import re, sys, pathlib

roots = [pathlib.Path(a) for a in sys.argv[1:]]
if not roots:
    skills = pathlib.Path('skills')
    roots = sorted(p for p in skills.iterdir() if p.is_dir()) if skills.is_dir() else []

total_bad, total_skills = 0, 0

for root in roots:
    ids, bodies = {}, {}
    for d in sorted(root.iterdir()):
        f = d / 'SKILL.md'
        if not f.is_file():
            continue
        body = f.read_text().split('---', 2)[2]
        ids[d.name] = set(re.findall(r'^- \*\*([A-Z0-9]+-\d+)\*\*', body, re.M))
        bodies[d.name] = body
    if not ids:
        continue
    total_skills += len(ids)

    names = '|'.join(sorted(ids))
    bad = set()
    for skill, body in bodies.items():
        for m in re.finditer(rf'`?\b({names})\s+([A-Z0-9]+-\d+)`?', body):
            target, rid = m.group(1), m.group(2)
            if rid not in ids.get(target, ()):
                bad.add((root.name, skill, target, rid))
    for fam, s, t, r in sorted(bad):
        print(f'BROKEN  {fam}/{s} -> {t} {r}')
    total_bad += len(bad)

print(f'{total_bad} broken cross-reference(s) across {total_skills} skill(s) '
      f'in {len(roots)} famil{"y" if len(roots)==1 else "ies"}')
sys.exit(1 if total_bad else 0)
