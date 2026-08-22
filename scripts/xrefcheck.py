#!/usr/bin/env python3
"""Verify every cross-skill rule reference resolves to a rule that exists.

usage: xrefcheck.py [skills-dir]   (default: skills/android)

Nothing else in the pipeline checks this. A reference to a rule that was renamed,
retired, or never written is invisible until a reader follows it.
"""
import re, sys, pathlib

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'skills/android')
ids, bodies = {}, {}
for d in sorted(root.iterdir()):
    f = d / 'SKILL.md'
    if not f.is_file():
        continue
    body = f.read_text().split('---', 2)[2]
    ids[d.name] = set(re.findall(r'^- \*\*([A-Z0-9]+-\d+)\*\*', body, re.M))
    bodies[d.name] = body

names = '|'.join(sorted(ids))
bad = []
for skill, body in bodies.items():
    for m in re.finditer(rf'`?\b({names})\s+([A-Z0-9]+-\d+)`?', body):
        target, rid = m.group(1), m.group(2)
        if rid not in ids.get(target, ()):
            bad.append((skill, target, rid))

for s, t, r in sorted(set(bad)):
    print(f'BROKEN  {s} -> {t} {r}')
print(f'{len(set(bad))} broken cross-reference(s) across {len(ids)} skills')
sys.exit(1 if bad else 0)
