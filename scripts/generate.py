#!/usr/bin/env python3
"""
Minimalist generator for Yanagi42's GitHub Profile README & dual-theme
borderless header SVGs. Zero external dependencies (Python 3 stdlib only).

Usage:
    python scripts/generate.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "profile.json"
ASSETS_DIR = ROOT / "assets"
README_PATH = ROOT / "README.md"

W = 880
H = 120

FONT_SERIF = "Georgia, 'Noto Serif SC', 'Songti SC', 'STSong', serif"
FONT_MONO = "ui-monospace, 'SFMono-Regular', 'Cascadia Mono', Consolas, monospace"

THEMES: dict[str, dict[str, str]] = {
    "light": {
        "ink": "#1F2328",
        "ink_mute": "#76808B",
        "rule": "#D8DEE4",
        "willow_stem": "#8B9D96",
        "willow_leaf": "#5D7D74",
        "willow_accent": "#265C6B",
    },
    "dark": {
        "ink": "#E6EDF3",
        "ink_mute": "#76808B",
        "rule": "#262C36",
        "willow_stem": "#4F645E",
        "willow_leaf": "#6E9188",
        "willow_accent": "#7AB3C4",
    },
}


def _cubic(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    u: float,
) -> tuple[float, float, float]:
    """Return (x, y, tangent_deg_from_down) on a cubic Bezier curve at parameter u."""
    m = 1.0 - u
    x = m**3 * p0[0] + 3 * m**2 * u * p1[0] + 3 * m * u**2 * p2[0] + u**3 * p3[0]
    y = m**3 * p0[1] + 3 * m**2 * u * p1[1] + 3 * m * u**2 * p2[1] + u**3 * p3[1]
    dx = (
        3 * m**2 * (p1[0] - p0[0])
        + 6 * m * u * (p2[0] - p1[0])
        + 3 * u**2 * (p3[0] - p2[0])
    )
    dy = (
        3 * m**2 * (p1[1] - p0[1])
        + 6 * m * u * (p2[1] - p1[1])
        + 3 * u**2 * (p3[1] - p2[1])
    )
    angle = -math.degrees(math.atan2(dx, dy))
    return x, y, angle


def willow_motif(t: dict[str, str]) -> str:
    """Minimalist ink-style weeping-willow motif with exact curve-attached leaves."""
    bough = ((878.0, 5.0), (840.0, 9.0), (802.0, 20.0), (766.0, 40.0))
    tendrils = [
        (
            ((786.0, 29.0), (776.0, 52.0), (764.0, 77.0), (750.0, 102.0)),
            0.95,
            [
                (0.18, 26, 0.88, False, 0.56),
                (0.39, -24, 0.94, False, 0.66),
                (0.60, 24, 0.98, True, 0.82),
                (0.80, -22, 0.84, False, 0.52),
            ],
        ),
        (
            ((818.0, 18.0), (810.0, 42.0), (802.0, 67.0), (789.0, 94.0)),
            0.90,
            [
                (0.22, 24, 0.84, False, 0.52),
                (0.46, -24, 0.92, False, 0.64),
                (0.70, 22, 0.86, False, 0.54),
                (0.90, -20, 0.76, False, 0.44),
            ],
        ),
        (
            ((850.0, 10.0), (845.0, 32.0), (839.0, 56.0), (829.0, 80.0)),
            0.80,
            [
                (0.26, 24, 0.80, False, 0.48),
                (0.54, -22, 0.86, False, 0.54),
                (0.82, 20, 0.76, False, 0.42),
            ],
        ),
    ]

    leaf = "M 0,0 Q 2.5,5.8 0,13.5 Q -2.5,5.8 0,0 Z"
    b0, b1, b2, b3 = bough
    stem_paths = [
        f'<path d="M {b0[0]:.1f},{b0[1]:.1f} C {b1[0]:.1f},{b1[1]:.1f} '
        f'{b2[0]:.1f},{b2[1]:.1f} {b3[0]:.1f},{b3[1]:.1f}" stroke-width="1.15"/>'
    ]
    leaf_svgs = []
    for pts, sw, specs in tendrils:
        p0, p1, p2, p3 = pts
        stem_paths.append(
            f'<path d="M {p0[0]:.1f},{p0[1]:.1f} C {p1[0]:.1f},{p1[1]:.1f} '
            f'{p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}" stroke-width="{sw}"/>'
        )
        for u, side_deg, sc, is_accent, op in specs:
            lx, ly, tang = _cubic(p0, p1, p2, p3, u)
            fill = t["willow_accent"] if is_accent else t["willow_leaf"]
            leaf_svgs.append(
                f'<path d="{leaf}" transform="translate({lx:.1f},{ly:.1f}) '
                f'rotate({tang + side_deg:.1f}) scale({sc})" fill="{fill}" opacity="{op}"/>'
            )

    return (
        f'  <g fill="none" stroke="{t["willow_stem"]}" stroke-linecap="round" opacity="0.60">\n'
        + "\n".join(f"    {p}" for p in stem_paths)
        + "\n  </g>\n  <g>\n    "
        + "\n    ".join(leaf_svgs)
        + "\n  </g>"
    )


def render_header(cfg: dict, theme_name: str) -> str:
    t = THEMES[theme_name]
    name = escape(cfg["display_name"])
    handle = escape(cfg["handle"])
    title = f"{cfg['display_name']} (@{cfg['handle']})"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}">
  <title>{escape(title)}</title>
  <defs>
    <linearGradient id="ruleFade" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">
      <stop offset="0%" stop-color="{t['rule']}" stop-opacity="0.95"/>
      <stop offset="78%" stop-color="{t['rule']}" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="{t['rule']}" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <!-- Minimalist willow motif (right) -->
  {willow_motif(t)}

  <!-- Clean wordmark + handle -->
  <text x="2" y="60" font-family="{FONT_SERIF}" font-size="42" font-weight="400" letter-spacing="-0.4" fill="{t['ink']}">{name}</text>
  <text x="4" y="86" font-family="{FONT_MONO}" font-size="12.5" letter-spacing="0.2" fill="{t['ink_mute']}">@{handle}</text>

  <!-- Hairline separator -->
  <rect x="0" y="112" width="{W}" height="1" fill="url(#ruleFade)"/>
</svg>
"""


def render_readme(cfg: dict) -> str:
    alt = f"{cfg['display_name']} (@{cfg['handle']})"
    lines = [
        "<!-- Generated by scripts/generate.py from profile.json -->",
        "",
        "<picture>",
        '  <source media="(prefers-color-scheme: dark)" srcset="./assets/header-dark.svg" />',
        '  <source media="(prefers-color-scheme: light)" srcset="./assets/header-light.svg" />',
        f'  <img alt="{escape(alt)}" src="./assets/header-light.svg" width="100%" />',
        "</picture>",
        "",
        "### 最近在做",
        "",
    ]

    for proj in cfg["projects"]:
        title = f"**[{proj['name']}]({proj['repo']})**"
        if proj.get("demo"):
            title += f"（[在线演示]({proj['demo']})）"
        stack = " ".join(f"`{s}`" for s in proj["stack"])
        lines.append(f"- {title} &nbsp;{stack}")
        lines.append(f"  <br />{proj['summary']}")
        lines.append("")

    if cfg.get("blog"):
        blog_label = cfg["blog"].replace("https://", "").rstrip("/")
        lines.extend([f"<sub>[{blog_label}]({cfg['blog']})</sub>", ""])

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    keep = {"header-light.svg", "header-dark.svg"}
    for stale in ASSETS_DIR.glob("*.svg"):
        if stale.name not in keep:
            stale.unlink()

    for theme in ("light", "dark"):
        (ASSETS_DIR / f"header-{theme}.svg").write_text(
            render_header(cfg, theme), encoding="utf-8"
        )

    README_PATH.write_text(render_readme(cfg), encoding="utf-8")
    print(f"Generated {len(list(ASSETS_DIR.glob('*.svg')))} SVGs and updated {README_PATH.name}.")


if __name__ == "__main__":
    main()
