#!/usr/bin/env python3
"""Build index.json from skills/.

usage: build-index.py [skills-dir] > index.json

The index is what turns a directory of markdown into something resolvable. A client
asks "this project has these signals, which skills apply?" and answers it from one
file instead of reading every skill.

Deterministic: same input, same bytes. CI diffs the output against the committed
index and fails if it is stale.
"""
import json, re, sys, pathlib

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'skills')

def strip_quotes(val):
    """One layer of YAML quoting, and only when it wraps the whole scalar."""
    if len(val) >= 2 and val[0] == val[-1] and val[0] in '"\'':
        return val[1:-1]
    return val


def frontmatter(text):
    """Minimal YAML for the shapes this format uses. No dependency on pyyaml."""
    fm = text.split('---', 2)[1]
    out, key = {}, None
    for raw in fm.split('\n'):
        if not raw.strip() or raw.strip().startswith('#'):
            continue
        m = re.match(r'^(\w+):\s*(.*)$', raw)
        if m and not raw.startswith((' ', '\t')):
            key, val = m.group(1), m.group(2).strip()
            if val.startswith('[') and val.endswith(']'):
                out[key] = [x.strip() for x in val[1:-1].split(',') if x.strip()]
            elif val:
                # a quoted scalar keeps its quotes without this, and `description` is the
                # one field here that is always quoted, because it has a colon in it. The
                # index shipped every description wrapped in a literal pair of quotes.
                out[key] = strip_quotes(val)
            else:
                out[key] = {}
            continue
        m = re.match(r'^\s+(\w+):\s*(.*)$', raw)
        if m and isinstance(out.get(key), dict):
            sub, val = m.group(1), m.group(2).strip()
            if val.startswith('[') and val.endswith(']'):
                out[key][sub] = [x.strip().strip('"\'') for x in val[1:-1].split(',') if x.strip()]
            else:
                out[key][sub] = []
            continue
        m = re.match(r'^\s+-\s*(.+)$', raw)
        if m and isinstance(out.get(key), dict) and out[key]:
            out[key][list(out[key])[-1]].append(m.group(1).strip().strip('"\''))
        elif m and isinstance(out.get(key), list):
            out[key].append(m.group(1).strip().strip('"\''))
    return out

skills = []
for f in sorted(root.rglob('SKILL.md')):
    text = f.read_text()
    fm = frontmatter(text)
    body = text.split('---', 2)[2]

    rules = re.findall(r'^- \*\*([A-Z0-9]+-\d+)\*\*\s+`(must|should)`', body, re.M)

    # what an installer actually sends, so a client can budget context before fetching
    sections = fm.get('agent_sections', ['rules'])
    installed = []
    for name in sections:
        m = re.search(rf'^## {name.capitalize()}\n(.*?)(?=\n## |\Z)', body, re.S | re.M)
        if m:
            installed.append(m.group(1))
    words = len(' '.join(installed).split())

    skills.append({
        'name': fm.get('name'),
        'axis': fm.get('axis'),
        'description': fm.get('description'),
        'family': fm.get('family'),
        'version': fm.get('version'),
        'requires': fm.get('requires', []),
        'detect': fm.get('detect', {}),
        'path': str(f.parent.relative_to(root.parent)),
        'rules': {
            'total': len(rules),
            'must': sum(1 for _, p in rules if p == 'must'),
            'should': sum(1 for _, p in rules if p == 'should'),
            'ids': [r for r, _ in rules],
        },
        'retired': fm.get('retired', []),
        'installed_words': words,
    })

families = sorted({s['family'] for s in skills if s['family']})
index = {
    'version': 1,
    'families': families,
    'counts': {
        'skills': len(skills),
        'rules': sum(s['rules']['total'] for s in skills),
        'retired': sum(len(s['retired']) for s in skills),
    },
    'skills': skills,
}
print(json.dumps(index, indent=2, ensure_ascii=False, sort_keys=False))
