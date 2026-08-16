"""Interactive 2-D / 3-D room view for ADA's Room Simulator tab.

The renderer is a dependency-free vanilla-JS app under ``static/roomsim`` (plan
canvas, orbiting 3-D view, SPL heat map). Its acoustics engine is a port of
ADA's own physics — see the provenance header in ``static/roomsim/js/engine.js``
— so the numbers here agree with the Modal Analysis and RT60 tabs.

Streamlit components have no web server of their own, so the CSS and JS are
inlined into a single HTML document and handed to ``components.html`` as one
srcdoc, matching the pattern used by ``digital_lab.py`` and
``experiment_simulator.py``.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import streamlit.components.v1 as components

ROOMSIM_DIR = Path(__file__).parent / "static" / "roomsim"

# Load order matters: engine defines window.Acoustics, which the rest consume.
SCRIPTS = ("engine.js", "charts.js", "editor.js", "view3d.js", "app.js")

# components.html needs a fixed height — the iframe cannot size itself to its
# content. Measured content height is ~2225 px at desktop widths (room view +
# tiles + RT60, SPL and mode cards), so this fits without a scrollbar. Below the
# simulator's ~960 px breakpoint the side panel stacks underneath and the page
# grows past 3000 px, which no single height can cover; `scrolling=True` lets
# those viewports scroll inside the frame instead of clipping the mode chart.
COMPONENT_HEIGHT = 2260

# ADA's dark slate palette, mapped onto the simulator's theme tokens. The 2-D
# canvas, the 3-D view and the SVG charts all read these through Charts.theme(),
# so this block is the single place the embedded view gets recoloured.
ADA_THEME = """
:root, :root[data-theme="dark"] {
  color-scheme: dark;
  --surface-1: #1e293b;
  /* Both canvases clear themselves by filling with --page-plane, so this must
     stay opaque — a transparent value paints nothing and every orbit frame
     smears on top of the last. The page background is made transparent on
     `body` below instead. */
  --page-plane: #172033;
  --text-primary: #e2e8f0;
  --text-secondary: #cbd5e1;
  --text-muted: #94a3b8;
  --gridline: #334155;
  --axis: #475569;
  --border: rgba(148, 163, 184, 0.22);
  --series-1: #38bdf8;
  --series-2: #f59e0b;
  --series-3: #22c55e;
}
body {
  background: transparent;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
/* The host page already provides the page title and framing. */
.app-header { display: none; }
.app { padding: 0; }
"""


@lru_cache(maxsize=1)
def _asset_bundle() -> tuple[str, str, str]:
    """Return (body_markup, css, js), read once per process."""
    index = (ROOMSIM_DIR / "index.html").read_text(encoding="utf-8")
    # Take everything inside <body>, minus the <script> tags we inline ourselves.
    body = index.split("<body>", 1)[1].split("</body>", 1)[0]
    body = body.split("<script", 1)[0]

    css = (ROOMSIM_DIR / "css" / "style.css").read_text(encoding="utf-8")
    js = "\n".join(
        (ROOMSIM_DIR / "js" / name).read_text(encoding="utf-8") for name in SCRIPTS
    )
    return body, css, js


def render_room_simulator(length: float, width: float, height: float) -> None:
    """Render the 2-D/3-D room view seeded from ADA's Room Geometry sliders.

    The seed is one-way: the view opens on the room described by the sliders,
    and edits made inside the canvas stay in the component. Moving a slider
    changes the seed signature, which re-seeds the view on the next rerun.
    """
    body, css, js = _asset_bundle()
    seed = {
        "L": round(float(length), 3),
        "W": round(float(width), 3),
        "H": round(float(height), 3),
    }
    seed["sig"] = f"{seed['L']}x{seed['W']}x{seed['H']}"

    document = f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{css}</style>
<style>{ADA_THEME}</style>
</head>
<body>
{body}
<script>window.__ADA_SEED__ = {json.dumps(seed)};</script>
<script>{js}</script>
</body>
</html>"""

    components.html(document, height=COMPONENT_HEIGHT, scrolling=True)
