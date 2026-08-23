#!/usr/bin/env python3
"""Generate the Claude Code plugin marketplace from skills/.

usage: build-plugin.py [--check]

One plugin per family. The plugin ships exactly what the CLI installs, the sections named
by `agent_sections`, so the promise holds in both channels: the reasoning, the pitfalls and
the evidence stay in this repository and never reach a model.

Frontmatter is rewritten because the two formats disagree about identity. Ours is
`android/compose`, which is the installable name and contains a slash; a Claude Code skill
is invoked as `/android-compose` and takes its name from the directory.

The plugin version is derived rather than typed: it counts the minor and patch bumps of
the skills inside it, so it only ever moves forward and nobody has to remember to edit it.
"""
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / 'skills'
PLUGINS = ROOT / 'plugins'
MANIFEST = ROOT / '.claude-plugin' / 'marketplace.json'

OWNER = {'name': 'ahmmedrejowan', 'url': 'https://github.com/skyl-dev'}
HOME = 'https://skyl.dev'
REPO = 'https://github.com/skyl-dev/skyl'

FAMILY_BLURB = {
    'android': 'Curated rules for Android projects, split by language, UI toolkit and concern, '
               'so a project loads only the layers that apply to it.',
}


def frontmatter(text):
    block = text.split('---', 2)[1]
    out = {}
    for line in block.splitlines():
        m = re.match(r'^([a-z_]+):\s*(.*)$', line)
        if m:
            value = m.group(2).strip()
            # values are quoted where they have to be, and the quotes are syntax
            if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
                value = json.loads(value) if value[0] == '"' else value[1:-1]
            out[m.group(1)] = value
    return out


def section(text, heading):
    body = text.split('---', 2)[2]
    m = re.search(rf'^## {heading}\n(.*?)(?=\n## |\Z)', body, re.S | re.M)
    return m.group(1).strip() if m else None


def build():
    written = {}
    families = sorted(d.name for d in SKILLS.iterdir() if d.is_dir())

    for family in families:
        plugin_dir = PLUGINS / f'skyl-{family}'
        if plugin_dir.exists():
            shutil.rmtree(plugin_dir)

        minor = patch = 0
        count = 0

        for skill_dir in sorted(d for d in (SKILLS / family).iterdir() if d.is_dir()):
            source = skill_dir / 'SKILL.md'
            if not source.exists():
                continue
            text = source.read_text()
            fm = frontmatter(text)
            name = f"{family}-{skill_dir.name}"

            wanted = [s.strip() for s in fm.get('agent_sections', '[rules]').strip('[]').split(',')]
            parts = []
            for heading in wanted:
                found = section(text, heading.capitalize())
                if found is None:
                    sys.exit(f'{source}: agent_sections names `{heading}` and there is no such section')
                parts.append(f'## {heading.capitalize()}\n\n{found}')

            version = fm.get('version', '1.0.0')
            _, mi, pa = (int(x) for x in version.split('.'))
            minor += mi
            patch += pa
            count += 1

            target = plugin_dir / 'skills' / name
            target.mkdir(parents=True, exist_ok=True)
            (target / 'SKILL.md').write_text(
                '---\n'
                f'name: {name}\n'
                # a plain YAML scalar may not contain ": ", and every description does
                f'description: {json.dumps(fm["description"])}\n'
                '---\n\n'
                + '\n\n'.join(parts).rstrip() + '\n'
            )

            references = skill_dir / 'references'
            if references.is_dir():
                shutil.copytree(references, target / 'references')

        (plugin_dir / '.claude-plugin').mkdir(parents=True, exist_ok=True)
        version = f'1.{minor}.{patch}'
        (plugin_dir / '.claude-plugin' / 'plugin.json').write_text(json.dumps({
            'name': f'skyl-{family}',
            'displayName': f'skyl {family}',
            'version': version,
            'description': FAMILY_BLURB.get(family, f'Curated agent rules for {family} projects.'),
            'author': OWNER,
            'homepage': HOME,
            'repository': REPO,
            'license': 'MIT',
            'keywords': ['skyl', family, 'rules', 'skills'],
        }, indent=2) + '\n')

        written[family] = {'version': version, 'count': count}

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({
        'name': 'skyl',
        'owner': OWNER,
        'metadata': {
            'description': 'Composable agent skills, one layer per concern.',
            'version': '1.0.0',
        },
        'plugins': [
            {
                'name': f'skyl-{family}',
                'source': f'./plugins/skyl-{family}',
                'description': FAMILY_BLURB.get(family, f'Curated agent rules for {family} projects.'),
                'version': written[family]['version'],
                'author': OWNER,
                'homepage': HOME,
                'license': 'MIT',
                'category': 'development',
                'keywords': ['skyl', family],
            }
            for family in sorted(written)
        ],
    }, indent=2) + '\n')

    return written


if __name__ == '__main__':
    before = {p: p.read_text() for p in list(PLUGINS.rglob('*')) + [MANIFEST] if p.is_file()} \
        if '--check' in sys.argv else None

    result = build()

    if before is not None:
        after = {p: p.read_text() for p in list(PLUGINS.rglob('*')) + [MANIFEST] if p.is_file()}
        if before != after:
            print('ERROR  the generated plugin does not match skills/. Run scripts/build-plugin.py '
                  'and commit the result.')
            sys.exit(1)
        print('plugin output matches skills/')
        sys.exit(0)

    for family, info in result.items():
        print(f"skyl-{family}  v{info['version']}  {info['count']} skills")
