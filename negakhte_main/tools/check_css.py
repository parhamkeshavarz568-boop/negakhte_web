#!/usr/bin/env python3
"""Fail the build on structurally broken CSS.

Why this exists: a single missing closing brace makes a browser silently
discard every rule after the fault — no error, no warning, the page just
renders without them. It happened here. An edit script's regex matched a
one-line rule INSIDE an @media block and ran through to that block's closing
brace, so `@media (prefers-reduced-motion: reduce) {` was never closed and
every rule after it — an entire animation system — was absorbed into a query
that does not match. The stylesheet looked perfect in the editor and the
feature simply did not exist in the browser.

Brace balance is a two-line check. Losing an afternoon to this is not.
"""
import glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def strip_comments(css):
    # keep length so reported line numbers stay true
    return re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), css, flags=re.S)

def check(path):
    raw = open(path, encoding="utf-8").read()
    problems = []
    if raw.count("/*") != raw.count("*/"):
        problems.append(f"unterminated comment: {raw.count('/*')} '/*' vs {raw.count('*/')} '*/'")
    body = strip_comments(raw)
    depth, line = 0, 1
    for ch in body:
        if ch == "\n":
            line += 1
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                problems.append(f"line {line}: one '}}' too many")
                depth = 0
    if depth:
        # report the last point the file was at top level — the fault is after it
        d, last_zero = 0, 0
        for n, L in enumerate(body.split("\n"), 1):
            d += L.count("{") - L.count("}")
            if d == 0:
                last_zero = n
        problems.append(f"{depth} unclosed block(s); last balanced at line {last_zero}, "
                        f"so every rule after it is swallowed")
    return problems

fail = False
for path in sorted(glob.glob(os.path.join(ROOT, "assets", "*.css"))):
    probs = check(path)
    name = os.path.relpath(path, ROOT)
    if probs:
        fail = True
        print(f"  ✗ {name}")
        for pr in probs:
            print(f"      {pr}")
    else:
        print(f"  ✓ {name} — braces and comments balanced")
sys.exit(1 if fail else 0)
