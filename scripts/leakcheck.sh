#!/usr/bin/env bash
# Fail if an installable section tells the model it is being evaluated.
#
# A skill carries its own evidence, and that evidence must never reach the agent:
# a rule that names its own control-arm score is telling the model what is being
# watched. This has caught two real leaks, the second named both the rule under
# observation and which model fails it.
#
# Only the sections listed in `agent_sections` are checked. Provenance and the
# human layer live outside them and are never installed.
# Run in CI on every skill. Exit 1 fails the build.
set -u
BAD='measured|unaided|control arm|eval-[0-9]|\bevals?/|skills/|arm-[0-9]|provenance'
fail=0
for f in "$@"; do
  # Given a SKILL.md, check only what agent_sections installs, the ## Rules section.
  # Provenance and the human layer live outside it and are never sent to a model.
  if grep -q '^## Rules' "$f" 2>/dev/null; then
    t=$(mktemp); awk '/^## Rules/{p=1} /^## /&&!/^## Rules/{if(p&&++n>0)exit} p' "$f" > "$t"
    target=$t
  else
    target=$f
  fi
  if grep -inE "$BAD" "$target" >/dev/null 2>&1; then
    echo "LEAK in $f:"; grep -inE "$BAD" "$target" | head -5; fail=1
  fi
  [ -n "${t:-}" ] && rm -f "$t" && unset t
done
[ $fail -eq 0 ] && echo "clean: $# skill(s)" || echo "FAILED: an installable section leaks evaluation language"
exit $fail
