# Builds assets/blueprint.svg: an engineering drawing of "surya" as an exploded isometric
# assembly -- interface / services / intelligence / infrastructure plates with callouts,
# a revision block (career history), general notes and a title block.
#
# Every element's static state is its FINAL state; SMIL only delays/fades things in, so a
# renderer that ignores animation still shows the finished sheet.
import os
from xml.sax.saxutils import escape as esc

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS, exist_ok=True)

W, H = 1000, 640
BG, INK, FAINT, CYAN, AMBER = "#0e3a6b", "#e6f0ff", "#9fbde0", "#8fd3ff", "#ffcf70"
FONT = "'JetBrains Mono','SF Mono',Consolas,'DejaVu Sans Mono',monospace"

S, T, GAP = 130, 8, 115          # plate size, plate thickness, vertical spacing
CX, CY0 = 250, 110               # stack centre x, first plate centre y
HX, HY = S * 0.866, S * 0.5      # iso half-width / half-height of a plate

out = []


def fade(t, dur=0.6):
    """Fade in at time t. Static value is 1, so non-animating renderers show it."""
    k = t / (t + dur)
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1" '
            f'dur="{t + dur:.2f}s" fill="freeze"/>')


def draw(t, dur=0.9):
    """Stroke draws itself from t (needs pathLength=1 + dasharray 1 1)."""
    k = t / (t + dur)
    return (f'<animate attributeName="stroke-dashoffset" values="1;1;0" keyTimes="0;{k:.3f};1" '
            f'dur="{t + dur:.2f}s" fill="freeze"/>')


def iso(cy, x, y):
    """Plate-local (x, y) in [-0.5, 0.5] -> screen point."""
    return CX + (x - y) * HX, cy + (x + y) * HY


def pts(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def text(x, y, s, size=11, fill=INK, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}" {extra}>{esc(s)}</text>')


def plate(cy, color, t):
    n, e, s, w = iso(cy, -.5, -.5), iso(cy, .5, -.5), iso(cy, .5, .5), iso(cy, -.5, .5)
    dn = lambda p: (p[0], p[1] + T)
    anim = f'pathLength="1" stroke-dasharray="1 1">{draw(t)}'
    return (f'<polygon points="{pts([w, s, dn(s), dn(w)])}" fill="#154a85" stroke="{color}" '
            f'stroke-width="1.2" {anim}</polygon>'
            f'<polygon points="{pts([s, e, dn(e), dn(s)])}" fill="#11416f" stroke="{color}" '
            f'stroke-width="1.2" {anim}</polygon>'
            f'<polygon points="{pts([n, e, s, w])}" fill="{BG}" stroke="{color}" '
            f'stroke-width="1.4" {anim}</polygon>')


def iso_rect(cy, x0, y0, x1, y1, color, width=1, dash=""):
    p = [iso(cy, x0, y0), iso(cy, x1, y0), iso(cy, x1, y1), iso(cy, x0, y1)]
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polygon points="{pts(p)}" fill="none" stroke="{color}" stroke-width="{width}"{d}/>'


def iso_line(cy, a, b, color, width=0.8, dash=""):
    (x1, y1), (x2, y2) = iso(cy, *a), iso(cy, *b)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
            f'stroke-width="{width}"{d}/>')


# ---------- plate surface details ----------
def detail_interface(cy):
    g = [iso_rect(cy, -.4, -.4, .02, .02, CYAN), iso_line(cy, (-.4, -.32), (.02, -.32), CYAN)]
    for i in range(3):
        g.append(iso_line(cy, (-.3 + i * .08, -.22), (-.3 + i * .08, -.02), FAINT, .6))
    g += [iso_rect(cy, .1, -.4, .4, -.08, CYAN), iso_line(cy, (.1, -.32), (.4, -.32), CYAN),
          iso_rect(cy, -.4, .1, .4, .4, CYAN), iso_line(cy, (-.4, .18), (.4, .18), CYAN),
          iso_rect(cy, .12, .02, .26, .06, FAINT, .6)]
    for i in range(4):
        g.append(iso_line(cy, (-.3 + i * .18, .26), (-.3 + i * .18, .34), FAINT, .6))
    return "".join(g)


def detail_services(cy):
    g, c = [], [-.28, 0, .28]
    for i in c:
        for j in c:
            g.append(iso_rect(cy, i - .07, j - .07, i + .07, j + .07, CYAN))
    for i in c:
        g.append(iso_line(cy, (-.21, i), (-.07, i), FAINT))
        g.append(iso_line(cy, (.07, i), (.21, i), FAINT))
        g.append(iso_line(cy, (i, -.21), (i, -.07), FAINT, .8, "2 2"))
        g.append(iso_line(cy, (i, .07), (i, .21), FAINT, .8, "2 2"))
    return "".join(g)


def detail_intelligence(cy):
    layers = [(-.3, [-.22, .22]), (0, [-.3, 0, .3]), (.3, [-.22, .22])]
    g = []
    for (xa, ya), (xb, yb) in zip(layers, layers[1:]):
        for a in ya:
            for b in yb:
                g.append(iso_line(cy, (xa, a), (xb, b), AMBER, .6))
    for x, ys in layers:
        for y in ys:
            px, py = iso(cy, x, y)
            g.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="5.5" ry="3.2" fill="{BG}" '
                     f'stroke="{AMBER}" stroke-width="1.2"/>')
    g.append(iso_rect(cy, -.42, -.42, .42, .42, AMBER, .8, "4 3"))
    return "".join(g)


def detail_infra(cy):
    g = [iso_line(cy, (-.42, y), (.42, y), FAINT, .5, "1 3") for y in (-.3, -.1, .1, .3)]
    for x in (-.24, 0, .24):
        px, py = iso(cy, x, 0)
        top = py - 20
        g.append(f'<path d="M{px - 11:.1f},{py:.1f} V{top:.1f} M{px + 11:.1f},{py:.1f} V{top:.1f} '
                 f'M{px - 11:.1f},{py:.1f} A11,4.5 0 0 0 {px + 11:.1f},{py:.1f}" fill="none" '
                 f'stroke="{CYAN}" stroke-width="1"/>'
                 f'<ellipse cx="{px:.1f}" cy="{top:.1f}" rx="11" ry="4.5" fill="{BG}" stroke="{CYAN}" '
                 f'stroke-width="1"/>'
                 f'<path d="M{px - 11:.1f},{top + 7:.1f} A11,4.5 0 0 0 {px + 11:.1f},{top + 7:.1f}" '
                 f'fill="none" stroke="{FAINT}" stroke-width=".6"/>')
    return "".join(g)


LAYERS = [
    ("INTERFACE", CYAN, detail_interface,
     ["ANGULAR · REACT · REACT NATIVE", "TYPESCRIPT · HTML · CSS"]),
    ("SERVICES", CYAN, detail_services,
     ["JAVA · SPRING BOOT · NODE.JS", "PYTHON · FASTAPI · FLASK", "REST · GRAPHQL · MICROSERVICES"]),
    ("INTELLIGENCE", AMBER, detail_intelligence,
     ["LLMS · AWS BEDROCK · LANGCHAIN", "RAG · EMBEDDINGS · FAISS", "DOCUMENT AI · OCR  (SEE NOTE 2)"]),
    ("INFRASTRUCTURE", CYAN, detail_infra,
     ["AWS · DOCKER · LINUX", "POSTGRESQL · MYSQL · MONGODB"]),
]

# ---------- sheet: grid, frames, zone markers ----------
out.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>'
           f'<rect x="22" y="22" width="{W - 44}" height="{H - 44}" fill="url(#grid)"/>'
           f'<rect x="10" y="10" width="{W - 20}" height="{H - 20}" fill="none" stroke="{INK}" stroke-width="1.6"/>'
           f'<rect x="22" y="22" width="{W - 44}" height="{H - 44}" fill="none" stroke="{INK}" stroke-width=".8"/>')
for i in range(6):
    x = 22 + (W - 44) * (i + .5) / 6
    out.append(text(x, 19, str(i + 1), 8, FAINT, anchor="middle") + text(x, H - 12, str(i + 1), 8, FAINT, anchor="middle"))
    if i:
        xb = 22 + (W - 44) * i / 6
        out.append(f'<path d="M{xb:.0f},10 V22 M{xb:.0f},{H - 22} V{H - 10}" stroke="{INK}" stroke-width=".8"/>')
for i, ch in enumerate("ABCD"):
    y = 22 + (H - 44) * (i + .5) / 4
    out.append(text(16, y + 3, ch, 8, FAINT, anchor="middle") + text(W - 16, y + 3, ch, 8, FAINT, anchor="middle"))

# ---------- exploded assembly: guide lines first, then plates bottom -> top ----------
cys = [CY0 + i * GAP for i in range(4)]
guides = []
for a, b in zip(cys, cys[1:]):
    for corner in ((-.5, .5), (.5, .5), (.5, -.5)):
        (x1, y1), (x2, y2) = iso(a, *corner), iso(b, *corner)
        guides.append(f'<line x1="{x1:.1f}" y1="{y1 + T:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                      f'stroke="{FAINT}" stroke-width=".7" stroke-dasharray="6 3 1 3"/>')
out.append(f'<g>{fade(0.2)}{"".join(guides)}</g>')

for i in reversed(range(4)):
    name, color, detail, _ = LAYERS[i]
    t = 0.3 + (3 - i) * 0.35
    out.append(f'<g>{fade(t, 0.9)}{plate(cys[i], color, t)}</g>')
    out.append(f'<g>{fade(t + 0.7)}{detail(cys[i])}</g>')

# ---------- callouts ----------
for i, (name, color, _, items) in enumerate(LAYERS):
    cy, t = cys[i], 1.9 + i * 0.25
    sx, sy = iso(cy, .3, -.12)
    ty = cy - 22
    g = [f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="2.5" fill="{color}"/>',
         f'<polyline points="{sx:.1f},{sy:.1f} 410,{ty} 428,{ty}" fill="none" stroke="{color}" stroke-width=".9"/>',
         f'<circle cx="442" cy="{ty}" r="10" fill="{BG}" stroke="{color}" stroke-width="1.2"/>',
         text(442, ty + 4, str(i + 1), 11, color, 700, "middle"),
         text(460, ty + 4, name + " LAYER", 13, color, 700, extra='letter-spacing="1.5"')]
    for j, item in enumerate(items):
        g.append(text(460, ty + 22 + j * 15, item, 11, INK))
    out.append(f'<g>{fade(t)}{"".join(g)}</g>')

# overall dimension on the left
top, bot = iso(cys[0], -.5, -.5)[1], iso(cys[-1], .5, .5)[1] + T
dim = [f'<path d="M70,{top:.0f} H{CX - 10} M70,{bot:.0f} H{CX - 10}" stroke="{FAINT}" stroke-width=".6"/>',
       f'<line x1="78" y1="{top + 8:.0f}" x2="78" y2="{bot - 8:.0f}" stroke="{INK}" stroke-width=".8"/>',
       f'<path d="M78,{top:.0f} l-4,9 h8z M78,{bot:.0f} l-4,-9 h8z" fill="{INK}"/>',
       f'<rect x="70" y="{(top + bot) / 2 - 95:.0f}" width="16" height="190" fill="{BG}"/>',
       text(82, (top + bot) / 2, "EST. 2020 · STILL BUILDING", 10, INK, anchor="middle",
            extra=f'letter-spacing="1" transform="rotate(-90 82 {(top + bot) / 2:.0f})"')]
out.append(f'<g>{fade(1.6)}{"".join(dim)}</g>')
out.append(f'<g>{fade(2.9)}{text(CX, 606, "FIG. 1 — EXPLODED ISOMETRIC VIEW", 10, FAINT, anchor="middle", extra=chr(32) + "letter-spacing=" + chr(34) + "1.5" + chr(34))}</g>')

# ---------- revision block (top right) ----------
RX, RY, RW = 728, 34, 238
rev = [("A", "B.E. CSE, OSMANIA UNIV.", "2020"),
       ("B", "SW ENGINEER, OSI DIGITAL", "2024"),
       ("C", "AWS CLOUD PRACTITIONER", "2024"),
       ("D", "AI HACKATHON: 2ND OF 15", "2026"),
       ("E", "SHIPPED dep-impact TO NPM", "2026")]
g = [f'<rect x="{RX}" y="{RY}" width="{RW}" height="{18 + 17 * (len(rev) + 1)}" fill="{BG}" stroke="{INK}" stroke-width=".9"/>',
     text(RX + RW / 2, RY + 13, "REVISIONS", 10, INK, 700, "middle", 'letter-spacing="2"'),
     f'<line x1="{RX}" y1="{RY + 18}" x2="{RX + RW}" y2="{RY + 18}" stroke="{INK}" stroke-width=".6"/>']
hy = RY + 18
g += [text(RX + 12, hy + 12, "REV", 9, FAINT, anchor="middle"), text(RX + 30, hy + 12, "DESCRIPTION", 9, FAINT),
      text(RX + RW - 20, hy + 12, "DATE", 9, FAINT, anchor="middle")]
for k, (r, d, y) in enumerate(rev):
    yy = hy + 17 * (k + 1)
    g.append(f'<line x1="{RX}" y1="{yy}" x2="{RX + RW}" y2="{yy}" stroke="{FAINT}" stroke-width=".4"/>')
    g += [text(RX + 12, yy + 12, r, 10, CYAN, 700, "middle"), text(RX + 30, yy + 12, d, 10),
          text(RX + RW - 20, yy + 12, y, 10, anchor="middle")]
g.append(f'<path d="M{RX + 24},{hy} V{hy + 17 * (len(rev) + 1)} M{RX + RW - 40},{hy} V{hy + 17 * (len(rev) + 1)}" stroke="{FAINT}" stroke-width=".4"/>')
out.append(f'<g>{fade(2.6)}{"".join(g)}</g>')

# ---------- general notes (right column) ----------
notes = [("1.", ["ALL LAYERS DESIGNED, BUILT AND", "SHIPPED END TO END."]),
         ("2.", ["LAYER 3 UNDER ACTIVE DEVELOPMENT:", "LANGGRAPH · MCP · RAG EVALS · LORA."]),
         ("3.", ["DO NOT UPGRADE DEPENDENCIES", "WITHOUT RUNNING dep-impact FIRST."]),
         ("4.", ["TOLERANCE ON PRODUCTION BUGS: 0.", "ACTUAL VALUES MAY VARY."])]
g, ny = [text(RX, 190, "GENERAL NOTES", 10, INK, 700, extra='letter-spacing="2"'),
         f'<line x1="{RX}" y1="196" x2="{RX + 110}" y2="196" stroke="{INK}" stroke-width=".6"/>'], 216
for num, lines in notes:
    g.append(text(RX, ny, num, 10, AMBER if num == "2." else CYAN, 700))
    for li, l in enumerate(lines):
        g.append(text(RX + 20, ny + li * 14, l, 10))
    ny += 14 * len(lines) + 10
out.append(f'<g>{fade(2.8)}{"".join(g)}</g>')

# ---------- detail A: dep-impact finding a breaking change in a dependency tree ----------
RED = "#ff8f8f"
DX, DY, DR = 790, 425, 56
tree = {"root": (DX, DY - 36), "a": (DX - 30, DY), "b": (DX, DY), "c": (DX + 30, DY),
        "a1": (DX - 40, DY + 34), "a2": (DX - 20, DY + 34), "c1": (DX + 20, DY + 34), "c2": (DX + 40, DY + 34)}
edges = [("root", "a"), ("root", "b"), ("root", "c"), ("a", "a1"), ("a", "a2"), ("c", "c1"), ("c", "c2")]
g = [f'<circle cx="{DX}" cy="{DY}" r="{DR}" fill="{BG}" stroke="{INK}" stroke-width="1" stroke-dasharray="8 3 2 3"/>']
for u, v in edges:
    (x1, y1), (x2, y2) = tree[u], tree[v]
    bad = v == "c2"
    g.append(f'<line x1="{x1}" y1="{y1 + 4}" x2="{x2}" y2="{y2 - 4}" stroke="{RED if bad else FAINT}" '
             f'stroke-width="{1.2 if bad else .8}"{" stroke-dasharray=" + chr(34) + "3 2" + chr(34) if bad else ""}/>')
for k, (x, y) in tree.items():
    c = RED if k == "c2" else (CYAN if k == "root" else INK)
    g.append(f'<rect x="{x - 8}" y="{y - 4}" width="16" height="8" rx="1.5" fill="{BG}" stroke="{c}" stroke-width="1.1"/>')
rx, ry = tree["c2"]
g.append(f'<path d="M{rx + 12},{ry - 16} l7,12 h-14z" fill="{RED}"/>'
         + text(rx + 12, ry - 6, "!", 9, BG, 700, "middle"))
g += [text(860, DY - 26, "DETAIL A", 11, INK, 700, extra='letter-spacing="1.5"'),
      text(860, DY - 10, "dep-impact", 10, CYAN),
      text(860, DY + 5, "SCALE 4:1", 9, FAINT),
      f'<rect x="860" y="{DY + 16}" width="10" height="6" fill="none" stroke="{RED}"/>',
      text(875, DY + 22, "BREAKS HERE", 9, RED)]
out.append(f'<g>{fade(3.2)}{"".join(g)}</g>')

# ---------- title block (bottom right) ----------
TX, TY, TW, TH = 640, 500, W - 22 - 640, H - 22 - 500
cells = [("DRAWN", "S.T.S."), ("LOCATION", "HYDERABAD, IN"), ("SCALE", "1:1"), ("SHEET", "1 / 3"), ("REV", "E")]
cw = [48, 100, 44, 52, TW - 244]
g = [f'<rect x="{TX}" y="{TY}" width="{TW}" height="{TH}" fill="{BG}" stroke="{INK}" stroke-width="1.2"/>',
     text(TX + 12, TY + 16, "PROJECT", 8, FAINT, extra='letter-spacing="1"'),
     text(TX + 12, TY + 40, "SURYA TEJA SANKURI", 20, INK, 700, extra='letter-spacing="2"'),
     f'<line x1="{TX}" y1="{TY + 52}" x2="{TX + TW}" y2="{TY + 52}" stroke="{INK}" stroke-width=".7"/>',
     text(TX + 12, TY + 66, "TITLE", 8, FAINT, extra='letter-spacing="1"'),
     text(TX + 12, TY + 80, "SOFTWARE ENGINEER · GENERAL ASSEMBLY", 11, CYAN, 700),
     f'<line x1="{TX}" y1="{TY + 88}" x2="{TX + TW}" y2="{TY + 88}" stroke="{INK}" stroke-width=".7"/>']
cx = TX
for (label, val), w in zip(cells, cw):
    if cx > TX:
        g.append(f'<line x1="{cx}" y1="{TY + 88}" x2="{cx}" y2="{TY + TH}" stroke="{INK}" stroke-width=".5"/>')
    g += [text(cx + 6, TY + 99, label, 7, FAINT, extra='letter-spacing="1"'), text(cx + 6, TY + 112, val, 10, INK, 700)]
    cx += w
out.append(f'<g>{fade(3.0)}{"".join(g)}</g>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Blueprint of Surya Teja Sankuri as an exploded assembly: interface, services, intelligence and infrastructure layers, with a revision history and title block.">
<defs>
<pattern id="grid-minor" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="#ffffff" stroke-opacity=".05" stroke-width="1"/></pattern>
<pattern id="grid" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="url(#grid-minor)"/><path d="M100 0H0V100" fill="none" stroke="#ffffff" stroke-opacity=".11" stroke-width="1"/></pattern>
</defs>
<style>text{{font-family:{FONT}}}</style>
{chr(10).join(out)}
</svg>
'''
open(os.path.join(ASSETS, "blueprint.svg"), "w", encoding="utf-8").write(svg)
print("ok", len(svg), "bytes")


# =====================================================================================
# Companion sheets. GitHub strips colour/CSS from README text, so every section of the
# page is drawn as its own blueprint image; part cards and contact tiles are separate
# files so the README can wrap each one in a link.
# =====================================================================================
GRID_DEFS = ('<defs><pattern id="gm" width="20" height="20" patternUnits="userSpaceOnUse">'
             '<path d="M20 0H0V20" fill="none" stroke="#ffffff" stroke-opacity=".05"/></pattern>'
             '<pattern id="g" width="100" height="100" patternUnits="userSpaceOnUse">'
             '<rect width="100" height="100" fill="url(#gm)"/>'
             '<path d="M100 0H0V100" fill="none" stroke="#ffffff" stroke-opacity=".11"/></pattern></defs>')


def write_sheet(name, w, h, body, label, frame=True):
    border = (f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" fill="none" stroke="{INK}" stroke-width="1.4"/>'
              if frame else "")
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'role="img" aria-label="{esc(label)}">{GRID_DEFS}<style>text{{font-family:{FONT}}}</style>'
           f'<rect width="{w}" height="{h}" fill="{BG}"/><rect width="{w}" height="{h}" fill="url(#g)"/>'
           f'{border}{body}</svg>\n')
    open(os.path.join(ASSETS, f"{name}.svg"), "w", encoding="utf-8").write(doc)
    print("ok", name)


def ticks(w, h, n=5):
    """Registration marks in the corners, like a plotted sheet."""
    s = []
    for x, y, dx, dy in ((8, 8, 1, 1), (w - 8, 8, -1, 1), (8, h - 8, 1, -1), (w - 8, h - 8, -1, -1)):
        s.append(f'<path d="M{x},{y + dy * 10} V{y} H{x + dx * 10}" fill="none" stroke="{CYAN}" stroke-width="1.2"/>')
    return "".join(s)


# ---- intro / specification strip ----
spec = ["I'm a software engineer in Hyderabad. I like building the whole thing, from the database",
        "to the button, and lately that includes the layer where a language model makes a guess",
        "and the rest of the system decides whether to trust it."]
body = [text(30, 34, "SPECIFICATION", 10, FAINT, 700, extra='letter-spacing="2.5"'),
        f'<line x1="30" y1="42" x2="150" y2="42" stroke="{FAINT}" stroke-width=".6"/>']
for i, l in enumerate(spec):
    body.append(text(30, 72 + i * 25, l, 16, INK))
body.append(text(970, 34, "REF. SHEET 1", 10, FAINT, anchor="end", extra='letter-spacing="1.5"'))
write_sheet("spec", 1000, 150, ticks(1000, 150) + "".join(body), " ".join(spec), frame=False)


# ---- section headers ----
def header(name, num, title, hint):
    body = (f'<circle cx="34" cy="28" r="15" fill="{BG}" stroke="{CYAN}" stroke-width="1.4"/>'
            + text(34, 33, num, 13, CYAN, 700, "middle")
            + text(62, 33, title, 15, CYAN, 700, extra='letter-spacing="3"')
            + f'<line x1="{72 + len(title) * 12.5:.0f}" y1="28" x2="{960 - len(hint) * 7.2:.0f}" y2="28" '
              f'stroke="{FAINT}" stroke-width=".7" stroke-dasharray="10 4 2 4"/>'
            + text(970, 32, hint, 10, FAINT, anchor="end", extra='letter-spacing="1.5"'))
    write_sheet(name, 1000, 56, body, f"Sheet {num}: {title.title()}", frame=False)


header("sheet-2", "2", "PARTS LIST", "CLICK A PART TO OPEN ITS REPO")
header("sheet-3", "3", "CONTACT THE ENGINEER", "CLICK A CELL")

# ---- part cards (each is its own file so it can be a link) ----
PARTS = [
    ("dep-impact", "NPM CLI · TYPESCRIPT",
     ["Shows which files break before you upgrade a package.",
      "Diffs .d.ts files with the TypeScript Compiler API",
      "and traces each change to your call sites."],
     "$ npm i -g dep-impact"),
    ("Infinity2k24", "WEB · REACT · THREE.JS",
     ["Website for Infinity 2k24, the national technical",
      "symposium at UCE, Osmania University.",
      "React, three.js and Framer Motion."], None),
    ("devi-interior-website", "WEB · REACT · CSS",
     ["Site for a local doors and carpentry business.",
      "React and plain CSS. No UI kit, no icon library,",
      "zero image requests."], None),
    ("cNature", "MOBILE · REACT NATIVE",
     ["App for cataloguing plants and trees: geotagged",
      "photos, map browsing, and a reviewer queue that",
      "keeps the catalogue honest."], None),
]
REPO = {"cNature": "cNature-app"}
for n, (name, tag, lines, cmd) in enumerate(PARTS, 1):
    w, h = 500, 190
    tw = len(tag) * 6.6 + 16
    b = [ticks(w, h),
         f'<circle cx="36" cy="38" r="13" fill="{BG}" stroke="{CYAN}" stroke-width="1.3"/>',
         text(36, 42, f"{n}", 12, CYAN, 700, "middle"),
         text(60, 44, name, 19, CYAN, 700),
         f'<rect x="{w - 24 - tw:.0f}" y="24" width="{tw:.0f}" height="20" fill="none" stroke="{FAINT}" stroke-width=".8"/>',
         text(w - 24 - tw / 2, 38, tag, 10, FAINT, anchor="middle", extra='letter-spacing="1"'),
         f'<line x1="24" y1="58" x2="{w - 24}" y2="58" stroke="{FAINT}" stroke-width=".5"/>']
    for i, l in enumerate(lines):
        b.append(text(24, 84 + i * 21, l, 13.5, INK))
    if cmd:
        b.append(text(24, 152, cmd, 13.5, AMBER, 700))
    b.append(text(24, 174, f"→ github.com/Surya-Teja-Sankuri/{REPO.get(name, name)}", 10.5, FAINT))
    b.append(text(w - 24, 174, f"ITEM {n:02d}", 10, FAINT, anchor="end", extra='letter-spacing="1.5"'))
    write_sheet(f"part-{n}", w, h, "".join(b), f"Part {n}: {name}. {' '.join(lines)}")

# ---- contact tiles ----
for key, label, value in (("linkedin", "LINKEDIN", "/in/surya-teja-sankuri"),
                          ("email", "EMAIL", "suryatejasankuri95@gmail.com"),
                          ("npm", "NPM", "dep-impact")):
    w, h = 330, 78
    b = [text(20, 28, label, 10, FAINT, 700, extra='letter-spacing="2.5"'),
         f'<line x1="20" y1="35" x2="{20 + len(label) * 9 + 10}" y2="35" stroke="{FAINT}" stroke-width=".6"/>',
         text(20, 60, value, 14, CYAN, 700), text(w - 18, 60, "→", 16, AMBER, 700, "end")]
    write_sheet(f"contact-{key}", w, h, "".join(b), f"{label.title()}: {value}")

# ---- footer strip ----
write_sheet("footer", 1000, 40,
            text(500, 25, "DRAWN IN PYTHON · NO DESIGN TOOLS WERE INVOLVED · SHEET 3 OF 3 · END OF DRAWING",
                 10, FAINT, anchor="middle", extra='letter-spacing="2"'),
            "Drawn in Python. No design tools were involved.", frame=False)
