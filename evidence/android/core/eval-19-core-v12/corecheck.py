#!/usr/bin/env python3
"""usage: corecheck.py <run-dir> <a|b>

Columns are written as the OUTCOME the rule asks about, not the mechanism it names
(see method/METHOD.md). Comment lines are stripped first.
"""
import re, sys, pathlib
d, task = pathlib.Path(sys.argv[1]), sys.argv[2]

def code(exts):
    out = []
    skip = ('/build/', '/.gradle/', '/.kotlin/', '/.git/')
    for f in d.rglob('*'):
        if any(k in str(f) for k in skip):
            continue
        if f.is_file() and f.suffix in exts:
            for l in f.read_text(errors='ignore').splitlines():
                s = l.strip()
                if s.startswith('//') or s.startswith('*') or s.startswith('/*'):
                    continue
                out.append(re.sub(r'//.*$', '', l))
    return '\n'.join(out)

kt = code({'.kt'})
gradle = code({'.kts', '.gradle', '.toml'})
def y(c): return 'Y' if c else 'n'

def brace_block(src, opener):
    m = re.search(opener, src)
    if not m:
        return ''
    i = src.index('{', m.start())
    depth = 0
    for j in range(i, len(src)):
        if src[j] == '{':
            depth += 1
        elif src[j] == '}':
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
    return ''

def all_onclicks(src):
    out = []
    for m in re.finditer(r'onClick\s*=\s*\{', src):
        i = m.end() - 1
        depth = 0
        for j in range(i, len(src)):
            if src[j] == '{':
                depth += 1
            elif src[j] == '}':
                depth -= 1
                if depth == 0:
                    out.append(src[i:j + 1])
                    break
    return '\n'.join(out)

if task == 'a':
    clicks = all_onclicks(kt)
    # A bare `suspend fun` does not establish a thread: a suspend function called from a
    # main-dispatched scope still runs on main. Only an explicit dispatcher or executor does.
    off_main = bool(re.search(r'Dispatchers\.(IO|Default)', kt)) \
        or bool(re.search(r'(Executors|Thread\s*\(|\.submit\s*\()', kt))
    blocking_names = r'(readAll|writeBackup|MessageDigest)'
    blocking_present = bool(re.search(blocking_names, kt))
    direct = bool(re.search(blocking_names, clicks)) and \
        not bool(re.search(r'(launch|async|withContext)', clicks))
    print(' '.join([
        # THE outcome column: blocking work exists and nothing moves it off the main thread.
        # Catches `scope.launch { store.readAll() }`, which is still the main dispatcher.
        'mainThreadVIOL=' + y(blocking_present and not off_main),
        'offMain=' + y(off_main),
        'blockingInOnClickVIOL=' + y(direct),
        'holderAdded=' + y(re.search(r'ViewModel\(\)', kt)),
        'scopeUsed=' + y(re.search(r'rememberCoroutineScope|viewModelScope|lifecycleScope', kt)),
    ]))
else:
    rel = brace_block(gradle, r'\brelease\s*\{')
    ksp = re.search(r'ksp\s*\(\s*"?[^)\n]*room', gradle, re.I)
    kapt = re.search(r'kapt\s*\(\s*"?[^)\n]*room', gradle, re.I)
    apir = re.search(r'api\s*\(\s*"?[^)\n]*room', gradle, re.I)
    impl = re.search(r'implementation\s*\(\s*"?[^)\n]*room', gradle, re.I)
    print(' '.join([
        'minify=' + y(re.search(r'(isMinifyEnabled|minifyEnabled)\s*=?\s*true', rel)),
        'shrinkRes=' + y(re.search(r'(isShrinkResources|shrinkResources)\s*=?\s*true', rel)),
        'proguardFiles=' + y(re.search(r'proguardFile', rel)),
        'roomKsp=' + y(ksp),
        'roomKaptVIOL=' + y(kapt),
        'roomApiVIOL=' + y(apir),
        'roomImpl=' + y(impl),
    ]))
