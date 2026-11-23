#!/usr/bin/env python3
"""
Builds a local GitHub-faithful Light & Dark preview HTML page for README.md
(preview.html is gitignored). Zero external dependencies.

Usage:
    python scripts/preview.py
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"
PREVIEW_PATH = ROOT / "preview.html"


def render_inline(text: str) -> str:
    text = re.sub(
        r"\*\*\[([^\]]+)\]\(([^)]+)\)\*\*",
        r'<strong><a href="\2" target="_blank" rel="noopener">\1</a></strong>',
        text,
    )
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener">\1</a>',
        text,
    )
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def md_to_github_html(md: str, theme: str) -> str:
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S).strip()

    def _replace_picture(match: re.Match[str]) -> str:
        block = match.group(0)
        src_m = re.search(
            rf'media="\(prefers-color-scheme:\s*{theme}\)"\s+srcset="([^"]+)"', block
        )
        alt_m = re.search(r'alt="([^"]*)"', block)
        src = src_m.group(1) if src_m else ""
        alt = alt_m.group(1) if alt_m else ""
        return f'<p class="hero-wrap"><img src="{src}" alt="{html.escape(alt)}" /></p>'

    md = re.sub(r"<picture>.*?</picture>", _replace_picture, md, flags=re.S)

    lines = md.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        raw_line = lines[i]
        line = raw_line.strip()
        if not line:
            i += 1
            continue
        if line == "<br />":
            out.append('<div style="height:8px"></div>')
            i += 1
        elif line.startswith("<p "):
            out.append(line)
            i += 1
        elif line.startswith("<sub"):
            out.append(f"<p>{render_inline(line)}</p>")
            i += 1
        elif line == "---":
            out.append("<hr />")
            i += 1
        elif line.startswith("### "):
            out.append(f"<h3>{render_inline(line[4:])}</h3>")
            i += 1
        elif line.startswith("- "):
            items = []
            while i < len(lines):
                cur = lines[i].strip()
                if cur.startswith("- "):
                    item_parts = [cur[2:]]
                    i += 1
                    while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                        item_parts.append(lines[i].strip())
                        i += 1
                    items.append(f"<li>{render_inline(' '.join(item_parts))}</li>")
                elif not cur:
                    # Peek ahead to see if list continues
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith("- "):
                        i += 1
                        continue
                    break
                else:
                    break
            out.append(f"<ul>{''.join(items)}</ul>")
        else:
            out.append(f"<p>{render_inline(line)}</p>")
            i += 1
    return "\n".join(out)


def main() -> None:
    raw = README_PATH.read_text(encoding="utf-8")
    dark_html = md_to_github_html(raw, "dark")
    light_html = md_to_github_html(raw, "light")

    doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Yanagi42 GitHub Profile Preview</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: #1c2128;
    color: #adbac7;
  }}
  .toolbar {{
    position: sticky;
    top: 0;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 24px;
    background: #14181e;
    border-bottom: 1px solid #2d333b;
    font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
    font-size: 12px;
  }}
  .tabs button {{
    background: #22272e;
    color: #cdd9e5;
    border: 1px solid #373e47;
    padding: 5px 12px;
    border-radius: 4px;
    cursor: pointer;
    margin-left: 8px;
    font-family: inherit;
    font-size: 12px;
  }}
  .tabs button.active {{
    background: #b24c28;
    border-color: #b24c28;
    color: #fff;
  }}
  .stage {{
    max-width: 960px;
    margin: 28px auto 48px;
    padding: 0 20px;
  }}
  .gh-frame {{
    border-radius: 6px;
    padding: 28px 32px 34px;
    border: 1px solid transparent;
  }}
  .gh-frame.light {{
    background: #ffffff;
    border-color: #d0d7de;
    color: #1f2328;
    --fg-muted: #59636e;
    --fg-subtle: #8c959f;
    --border-soft: #d8dee4;
    --code-bg: rgba(175, 184, 193, 0.2);
    --link: #0969da;
  }}
  .gh-frame.dark {{
    background: #0d1117;
    border-color: #30363d;
    color: #e6edf3;
    --fg-muted: #9198a1;
    --fg-subtle: #656d76;
    --border-soft: #21262d;
    --code-bg: rgba(110, 118, 129, 0.28);
    --link: #58a6ff;
  }}
  .gh-header {{
    font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
    font-size: 12px;
    margin-bottom: 18px;
    color: var(--fg-subtle);
  }}
  .markdown-body {{
    max-width: 880px;
    margin: 0 auto;
    font-size: 14.5px;
    line-height: 1.75;
  }}
  .markdown-body .hero-wrap {{
    margin: 0 0 18px;
  }}
  .markdown-body img {{
    display: block;
    width: 100%;
    height: auto;
  }}
  .markdown-body h3 {{
    margin: 26px 0 12px;
    font-size: 16px;
    font-weight: 600;
    line-height: 1.3;
  }}
  .markdown-body p {{
    margin: 0 0 12px;
  }}
  .markdown-body code {{
    font-family: ui-monospace, SFMono-Regular, "Cascadia Mono", Consolas, monospace;
    font-size: 83%;
    padding: 0.16em 0.42em;
    border-radius: 5px;
    background: var(--code-bg);
  }}
  .markdown-body ul {{
    margin: 0 0 16px;
    padding-left: 20px;
  }}
  .markdown-body li {{
    margin: 12px 0;
  }}
  .markdown-body li br {{
    display: block;
    margin-top: 2px;
  }}
  .markdown-body sub {{
    font-size: 12.5px;
    color: var(--fg-subtle);
    vertical-align: baseline;
  }}
  .markdown-body a {{
    color: var(--link);
    text-decoration: none;
  }}
  .markdown-body a:hover {{
    text-decoration: underline;
  }}
  .hidden {{ display: none; }}
</style>
</head>
<body>
  <div class="toolbar">
    <span>PREVIEW // github.com/Yanagi42</span>
    <div class="tabs">
      <button id="btn-dark" class="active" onclick="show('dark')">GitHub Dark</button>
      <button id="btn-light" onclick="show('light')">GitHub Light</button>
      <button id="btn-both" onclick="show('both')">Both</button>
    </div>
  </div>
  <div class="stage">
    <section id="panel-dark" class="gh-frame dark">
      <div class="gh-header">Yanagi42 / README.md</div>
      <article class="markdown-body">{dark_html}</article>
    </section>
    <div style="height:24px" id="spacer" class="hidden"></div>
    <section id="panel-light" class="gh-frame light hidden">
      <div class="gh-header">Yanagi42 / README.md</div>
      <article class="markdown-body">{light_html}</article>
    </section>
  </div>
  <script>
    function show(mode) {{
      document.getElementById('panel-dark').classList.toggle('hidden', mode === 'light');
      document.getElementById('panel-light').classList.toggle('hidden', mode === 'dark');
      document.getElementById('spacer').classList.toggle('hidden', mode !== 'both');
      for (const m of ['dark', 'light', 'both']) {{
        document.getElementById('btn-' + m).classList.toggle('active', m === mode);
      }}
    }}
  </script>
</body>
</html>
"""
    PREVIEW_PATH.write_text(doc, encoding="utf-8")
    print(f"Wrote {PREVIEW_PATH}")


if __name__ == "__main__":
    main()
