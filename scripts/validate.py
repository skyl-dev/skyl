#!/usr/bin/env python3
"""Validate every skill against spec/FORMAT.md.

usage: validate.py [skills-dir]   (default: skills)

Checks the things a reader cannot see are wrong until they matter:
frontmatter completeness, rule shape, id stability, and that a retired id is
never reused.
"""
import re, sys, pathlib

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'skills')
AXES = {'core', 'language', 'framework', 'service', 'topic'}
REQUIRED = ['name', 'axis', 'family', 'description', 'version', 'agent_sections']
HUMAN_SECTIONS = ['## Why', '## Pitfalls', '## Provenance']

errors, warnings, skills = [], [], 0

for f in sorted(root.rglob('SKILL.md')):
    rel = f.relative_to(root.parent)
    skills += 1
    text = f.read_text()
    def err(m): errors.append(f'{rel}: {m}')
    def warn(m): warnings.append(f'{rel}: {m}')

    if not text.startswith('---'):
        err('no frontmatter'); continue
    fm, body = text.split('---', 2)[1], text.split('---', 2)[2]

    for key in REQUIRED:
        if not re.search(rf'^{key}:', fm, re.M):
            err(f'frontmatter missing `{key}`')

    axis = re.search(r'^axis:\s*(\S+)', fm, re.M)
    if axis and axis.group(1) not in AXES:
        err(f'axis `{axis.group(1)}` is not one of {sorted(AXES)}')

    name = re.search(r'^name:\s*(\S+)', fm, re.M)
    if name and f'{name.group(1)}' != f'{f.parent.parent.name}/{f.parent.name}':
        err(f'name `{name.group(1)}` does not match its path')

    ver = re.search(r'^version:\s*(\S+)', fm, re.M)
    if ver and not re.fullmatch(r'\d+\.\d+\.\d+', ver.group(1)):
        err(f'version `{ver.group(1)}` is not semver')

    if '## Rules' not in body:
        err('no `## Rules` section')
    for s in HUMAN_SECTIONS:
        if s not in body:
            warn(f'no `{s}` section, required for a shipped skill')

    rules = re.findall(r'^- \*\*([A-Z0-9]+-\d+)\*\*\s+`(must|should)`', body, re.M)
    ids = [r[0] for r in rules]
    if not ids:
        err('no rules found, or rules do not match the format')
    for rid in ids:
        if ids.count(rid) > 1:
            err(f'duplicate rule id `{rid}`')

    retired = re.search(r'^retired:\s*\[(.*?)\]', fm, re.M | re.S)
    if retired:
        gone = [x.strip() for x in retired.group(1).split(',') if x.strip()]
        for rid in gone:
            # A retired entry must be a real rule id. A descriptive label such as
            # `ASK-3-ask-in-context` hides the fact that `ASK-3` itself was reused.
            if not re.fullmatch(r'[A-Z0-9]+-\d+', rid):
                err(f'retired entry `{rid}` is not a rule id. '
                    f'Use the bare id, so reuse of it is detectable.')
                continue
            if rid in ids:
                err(f'retired id `{rid}` is in use again, ids are never reused')

    # every rule states a boundary; without one it gets applied everywhere
    for block in re.split(r'^- \*\*', body, flags=re.M)[1:]:
        rid = re.match(r'([A-Z0-9]+-\d+)', block)
        if not rid:
            continue
        if '*Why:*' not in block:
            warn(f'{rid.group(1)}: no `*Why:*`')
        if '*Not when:*' not in block:
            warn(f'{rid.group(1)}: no `*Not when:*`, a rule with no boundary is applied everywhere')

for e in errors:
    print(f'ERROR   {e}')
for w in warnings:
    print(f'warn    {w}')
print(f'\n{skills} skill(s): {len(errors)} error(s), {len(warnings)} warning(s)')
sys.exit(1 if errors else 0)
