# Copyright (c) 2026 ICTU-CRIS contributors
# SPDX-License-Identifier: Apache-2.0
"""Add self-playing SMIL/CSS flow effects to the static pipeline SVG.

Regenerating docs/images/duong-ong-du-lieu.svg:
  1. Open docs/architecture/duong-ong-du-lieu.html in the archify viewer and
     export the dual-theme static SVG (no JavaScript in the export).
  2. Run: python3 docs/architecture/animate_pipeline_svg.py <exported.svg> docs/images/duong-ong-du-lieu.svg
  3. Commit the overwritten docs/images/duong-ong-du-lieu.svg.

GitHub renders README <img> SVGs without JavaScript, so the "trace" effect
that the viewer normally plays on hover/click is reproduced here with plain
SMIL (<animateMotion>) for the solid "a-emphasis" edges and a CSS
stroke-dashoffset keyframe animation for the dashed "a-dashed" edges. Both
start immediately (begin=0s plus a per-edge stagger) and loop forever, and
both are switched off under prefers-reduced-motion.

Only edges carrying a data-edge-id attribute are animated; the two sample
strokes in the legend have no data-edge-id and are left untouched. Colors
are not hardcoded: particles and glow reuse the var(--arrow-emphasis) custom
property the diagram already themes with, so they stay correct in the
existing dark/light (and preset) variants.

Running this script twice on its own output is a no-op: the injected CSS
block is stripped (by sentinel comment) and every prior <g class=
"flow-particles"> is removed before a fresh copy of each is computed, and
path ids are only added when missing.

Each particle <g> is placed immediately after its own edge <path>, not at
the end of the document, so the edge-label groups (drawn later in the
source SVG) still paint over it -- a label never gets covered by a
passing particle.
"""
import re
import sys

CSS_START = "/* animate-pipeline-svg:start */"
CSS_END = "/* animate-pipeline-svg:end */"
PARTICLE_GROUP_RE = re.compile(r'<g class="flow-particles"[^>]*>.*?</g>', re.S)

PATH_TAG_RE = re.compile(r"<path\b[^>]*?/>")
EDGE_ID_RE = re.compile(r'data-edge-id="([^"]*)"')
EDGE_KEY_RE = re.compile(r'data-edge-key="(\d+)"')
CLASS_RE = re.compile(r'class="([^"]*)"')
ID_ATTR_RE = re.compile(r'\sid="[^"]*"')
DASHED_RULE_RE = re.compile(r"\.a-dashed\s*\{[^}]*stroke-dasharray:\s*([0-9.]+)\s*,\s*([0-9.]+)")

PARTICLE_DUR = "2.2s"
PARTICLE_STAGGER = 0.3
DASH_DUR = "1.2s"


def strip_block(text, start, end):
    pattern = re.compile(r"\n?" + re.escape(start) + r".*?" + re.escape(end) + r"\n?", re.S)
    return pattern.sub("", text)


def add_particles(svg):
    """Ensure each a-emphasis edge path has an id, and follow it immediately
    with its <g class="flow-particles"> sibling so the edge label groups
    (which come later in the document) paint over the particle rather than
    the other way around -- keeps labels readable at every animation frame.
    """

    def repl(match):
        tag = match.group(0)
        edge_id = EDGE_ID_RE.search(tag)
        cls = CLASS_RE.search(tag)
        if not edge_id or not cls or "a-emphasis" not in cls.group(1).split():
            return tag
        if not ID_ATTR_RE.search(tag):
            tag = tag.replace("<path", f'<path id="edge-{edge_id.group(1)}"', 1)
        key = EDGE_KEY_RE.search(tag)
        order = int(key.group(1)) if key else 0
        return tag + build_particle_group(edge_id.group(1), order * PARTICLE_STAGGER)

    return PATH_TAG_RE.sub(repl, svg)


def dash_offset(svg):
    m = DASHED_RULE_RE.search(svg)
    if not m:
        return 8
    return -(float(m.group(1)) + float(m.group(2)))


def build_css_block(svg):
    offset = dash_offset(svg)
    return (
        f"\n{CSS_START}\n"
        "@keyframes pipeline-flow-dash { to { stroke-dashoffset: "
        f"{offset:g}px" + "; } }\n"
        f'path.a-dashed[data-edge-id] {{ animation: pipeline-flow-dash {DASH_DUR} linear infinite; }}\n'
        ".flow-particles .flow-halo { fill: var(--arrow-emphasis); opacity: .25; }\n"
        ".flow-particles .flow-particle { fill: var(--arrow-emphasis); }\n"
        "@media (prefers-reduced-motion: reduce) {\n"
        "  * { animation: none !important; }\n"
        "  .flow-particles { display: none; }\n"
        "}\n"
        f"{CSS_END}\n"
    )


def build_particle_group(edge_id, begin):
    target = f"edge-{edge_id}"
    motion = (
        f'<animateMotion dur="{PARTICLE_DUR}" repeatCount="indefinite" begin="{begin:g}s" '
        f'keyPoints="0;0.96" keyTimes="0;1" calcMode="linear"><mpath href="#{target}"/></animateMotion>'
    )
    return (
        f'<g class="flow-particles" data-edge-id="{edge_id}">'
        f'<circle class="flow-halo" r="7">{motion}</circle>'
        f'<circle class="flow-particle" r="3.5">{motion}</circle>'
        "</g>"
    )


def animate(svg):
    svg = strip_block(svg, CSS_START, CSS_END)
    svg = PARTICLE_GROUP_RE.sub("", svg)
    svg = add_particles(svg)

    css_block = build_css_block(svg)
    style_close = svg.rfind("</style>")
    if style_close == -1:
        raise ValueError("no <style> element found in input SVG")
    svg = svg[:style_close] + css_block + svg[style_close:]
    return svg


def main(argv):
    if len(argv) != 3:
        print(f"usage: {argv[0]} <in.svg> <out.svg>", file=sys.stderr)
        return 2
    src = open(argv[1], encoding="utf-8").read()
    out = animate(src)
    with open(argv[2], "w", encoding="utf-8") as f:
        f.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
