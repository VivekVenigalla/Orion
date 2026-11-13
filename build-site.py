#!/usr/bin/env python3
"""Builds site/index.html (the public, standalone page) from portfolio-matrix.html.

The source file is a fragment made for the Claude artifact host, which supplies the
document skeleton. This wraps it in a full HTML document and adds what the host
would otherwise provide. Run from this folder:  python3 build-site.py
"""
import pathlib

here = pathlib.Path(__file__).resolve().parent
src = (here / "portfolio-matrix.html").read_text(encoding="utf-8")

title_line = "<title>Target-Driven Portfolio Matrix</title>\n"
meta_line = '<meta name="claude:viewport-fit-sides" content="cover">\n'
assert src.count(title_line) == 1 and src.count(meta_line) == 1
src = src.replace(title_line, "").replace(meta_line, "")

head_end = src.index("</style>") + len("</style>")
head_part, body_part = src[:head_end].strip(), src[head_end:].strip()
assert head_part.startswith('<link rel="stylesheet"') and body_part.startswith('<div id="root">')

# Styles the artifact host used to supply.
base = (
    "html { background: #060810; }\n"
    "body { margin: 0; }\n"
    ":root { padding: env(safe-area-inset-top, 0px) 0 env(safe-area-inset-bottom, 0px); }\n"
    "[hidden] { display: none !important; }\n"
    ".offline { position: absolute; inset: 0; display: grid; place-items: center; padding: 24px; "
    "text-align: center; color: #93A0BF; font: 15px/1.5 system-ui, sans-serif; }\n"
)
assert head_part.count("<style>\n") == 1
head_part = head_part.replace("<style>\n", "<style>\n" + base)

# A readable message instead of a blank page if the React CDN is unreachable.
iife = "(function () {\n'use strict';\n"
assert body_part.count(iife) == 1
guard = (
    iife
    + "if (!window.React || !window.ReactDOM) {\n"
    + "  document.getElementById('root').innerHTML = '<p class=\"offline\">This page could not load its "
    + "interface library. Check your internet connection and reload.</p>';\n"
    + "  return;\n}\n"
)
body_part = body_part.replace(iife, guard)

icon = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 18 18'%3E"
    "%3Crect width='18' height='18' rx='4' fill='%23060810'/%3E"
    "%3Cpath d='M4 4.5h3.5M10.5 4.5H14M9 6v6' fill='none' stroke='%23F6C453' stroke-width='1.5' stroke-linecap='round' opacity='.55'/%3E"
    "%3Ccircle cx='4' cy='4.5' r='2' fill='%23F6C453'/%3E%3Ccircle cx='14' cy='4.5' r='2' fill='%23F6C453'/%3E"
    "%3Ccircle cx='9' cy='13.5' r='2' fill='%23F6C453'/%3E%3C/svg%3E"
)

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Target-Driven Portfolio Matrix</title>
<meta name="description" content="Name a target and get the skills it takes as a skill tree where every node unlocks with a repo you ship. Earn XP, check repos on GitHub, and share a read-only proof page.">
<meta name="theme-color" content="#060810">
<link rel="icon" href="{icon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{head_part}
</head>
<body>
<noscript><p style="padding:24px;color:#93A0BF;font:15px system-ui">This prototype needs JavaScript turned on.</p></noscript>
{body_part}
</body>
</html>
"""
out = here / "site" / "index.html"
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({len(html):,} bytes)")
