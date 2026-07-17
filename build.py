#!/usr/bin/env python3
"""
Build the Boccherini Sampler GitHub Pages site.

Assembles, for each of the two groups, one merged PDF per instrument
(V1, V2, VA, VC) containing that instrument's part for every piece the
group is playing, in program order, with a clickable bookmark per piece.
Also emits the individual per-piece parts.

Sources (relative to the parent Scores/ directory):
  - Boccherini-lilypond/   LilyPond-typeset parts (preferred)
  - Boccherini-imslp/      IMSLP scans (Op.44/4 individual; Op.33 whole-opus bundle)
  - Boccherini-KM/         Op.58 individual parts

Run from anywhere; paths are resolved relative to this file.
"""

import shutil
from pathlib import Path
from pypdf import PdfReader, PdfWriter

HERE = Path(__file__).resolve().parent          # boccherini-sampler/
SCORES = HERE.parent                            # Scores/
LP = SCORES / "Boccherini-lilypond"
IMSLP = SCORES / "Boccherini-imslp"
KM = SCORES / "Boccherini-KM"

INSTRUMENTS = ["V1", "V2", "VA", "VC"]

# Source helpers -------------------------------------------------------------
def lily(opus, no, g):
    """LilyPond part set: Boccherini-OOO-N-Gxxx-{V1,V2,VA,VC}.pdf"""
    base = f"Boccherini-{opus:03d}-{no}-G{g}"
    return {p: (LP / f"{base}-{p}.pdf", None) for p in INSTRUMENTS}

def imslp_individual(opus, no, g):
    base = f"Boccherini-{opus:03d}-{no}-G{g}"
    return {p: (IMSLP / f"{base}-{p}.pdf", None) for p in INSTRUMENTS}

def km58(no):
    names = {"V1": "violin 1", "V2": "violin 2", "VA": "viola", "VC": "cello"}
    return {p: (KM / f"Boccherini Quartet Op 58 No {no} {names[p]}.pdf", None)
            for p in INSTRUMENTS}

# op33/5 split from the whole-opus IMSLP bundle (pages verified visually)
OP33_5_RANGES = {"V1": (15, 18), "V2": (9, 10), "VA": (9, 10), "VC": (9, 10)}
def op33_5():
    return {p: (IMSLP / f"Boccherini-033-all-{p}.pdf", OP33_5_RANGES[p])
            for p in INSTRUMENTS}

# Program --------------------------------------------------------------------
# Each piece: (title, slug, source-dict, source-label)
GROUPS = {
    "Group 1": {
        "subtitle": "Harder cello",
        "players": "Jason / Leah, Kath, Josh  ·  Roberta / Grant (floating)",
        "pieces": [
            ("Op. 8 No. 2 (G.166)",  "Op08-No2-G166", lily(8, 2, 166),  "LilyPond"),
            ("Op. 15 No. 4 (G.180)", "Op15-No4-G180", lily(15, 4, 180), "LilyPond"),
            ("Op. 22 No. 4 (G.186)", "Op22-No4-G186", lily(22, 4, 186), "LilyPond"),
            ("Op. 24 No. 4 (G.192)", "Op24-No4-G192", lily(24, 4, 192), "LilyPond"),
            ("Op. 33 No. 5 (G.211)", "Op33-No5-G211", op33_5(),         "IMSLP"),
            ("Op. 58 No. 5 (G.246)", "Op58-No5-G246", km58(5),          "IMSLP"),
        ],
    },
    "Group 2": {
        "subtitle": "Easier cello",
        "players": "Casey / Stephen, Jon, Zon",
        "pieces": [
            ("Op. 2 No. 6 (G.164)",  "Op02-No6-G164", lily(2, 6, 164),  "LilyPond"),
            ("Op. 8 No. 1 (G.165)",  "Op08-No1-G165", lily(8, 1, 165),  "LilyPond"),
            ("Op. 8 No. 3 (G.167)",  "Op08-No3-G167", lily(8, 3, 167),  "LilyPond"),
            ("Op. 15 No. 1 (G.177)", "Op15-No1-G177", lily(15, 1, 177), "LilyPond"),
            ("Op. 24 No. 6 (G.194)", "Op24-No6-G194", lily(24, 6, 194), "LilyPond"),
            ("Op. 44 No. 4 (G.223)", "Op44-No4-G223", imslp_individual(44, 4, 223), "IMSLP"),
            ("Op. 58 No. 4 (G.245)", "Op58-No4-G245", km58(4),          "IMSLP"),
        ],
    },
}

INSTRUMENT_LABEL = {"V1": "Violin I", "V2": "Violin II", "VA": "Viola", "VC": "Cello"}


def add_source(writer, src, page_range, bookmark):
    """Append a source PDF (optionally a page range) and bookmark its first page."""
    reader = PdfReader(str(src))
    start_index = len(writer.pages)
    if page_range is None:
        pages = range(len(reader.pages))
    else:
        a, b = page_range
        pages = range(a - 1, b)  # 1-based inclusive -> 0-based
    for i in pages:
        writer.add_page(reader.pages[i])
    writer.add_outline_item(bookmark, start_index)


def main():
    parts_dir = HERE / "parts"
    pieces_dir = HERE / "pieces"
    for d in (parts_dir, pieces_dir):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)

    missing = []
    bundle_pages = {}   # (gslug, inst) -> page count
    for gname, g in GROUPS.items():
        gslug = gname.replace(" ", "")
        for inst in INSTRUMENTS:
            writer = PdfWriter()
            for title, slug, sources, _lbl in g["pieces"]:
                src, rng = sources[inst]
                if not src.exists():
                    missing.append(str(src))
                    continue
                add_source(writer, src, rng, title)
                # also emit the individual piece part
                pw = PdfWriter()
                add_source(pw, src, rng, title)
                out = pieces_dir / f"{slug}-{inst}.pdf"
                with open(out, "wb") as fh:
                    pw.write(fh)
            out = parts_dir / f"{gslug}-{inst}.pdf"
            with open(out, "wb") as fh:
                writer.write(fh)
            n = len(PdfReader(str(out)).pages)
            bundle_pages[(gslug, inst)] = n
            print(f"{out.name}: {n} pages")

    if missing:
        print("\nMISSING SOURCES:")
        for m in missing:
            print("  ", m)
        raise SystemExit(1)

    write_index(bundle_pages)
    print("\nBuild OK")


# ---------------------------------------------------------------------------
def write_index(bundle_pages):
    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    sections = []
    for gname, g in GROUPS.items():
        gslug = gname.replace(" ", "")
        bundles = []
        for inst in INSTRUMENTS:
            pp = bundle_pages[(gslug, inst)]
            bundles.append(
                f'<a class="bundle" href="parts/{gslug}-{inst}.pdf" download>'
                f'<span class="inst">{INSTRUMENT_LABEL[inst]}</span>'
                f'<span class="pp">{pp} pp · PDF</span></a>'
            )
        rows = []
        for title, slug, _sources, lbl in g["pieces"]:
            links = " ".join(
                f'<a href="pieces/{slug}-{inst}.pdf" download>{inst}</a>'
                for inst in INSTRUMENTS
            )
            rows.append(
                f'<tr><td class="pc">{esc(title)}</td>'
                f'<td class="src">{lbl}</td>'
                f'<td class="lk">{links}</td></tr>'
            )
        sections.append(f"""
    <section class="group">
      <div class="ghead">
        <h2>{esc(gname)}</h2>
        <span class="tag">{esc(g['subtitle'])}</span>
      </div>
      <p class="players">{esc(g['players'])}</p>
      <div class="bundles">
        {''.join(bundles)}
      </div>
      <details>
        <summary>{len(g['pieces'])} works — individual parts</summary>
        <table>
          <thead><tr><th>Work</th><th>Source</th><th>Parts</th></tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </details>
    </section>""")

    html = TEMPLATE.replace("__SECTIONS__", "".join(sections))
    (HERE / "index.html").write_text(html, encoding="utf-8")
    print("index.html written")


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Boccherini Sampler</title>
<style>
:root{
  --bg:#f4efe6; --panel:#fbf8f2; --ink:#241f1a; --muted:#6f6455;
  --line:#e2d8c6; --accent:#7c2932; --accent-ink:#fff; --tag:#8a6d3b;
}
@media (prefers-color-scheme:dark){
  :root{ --bg:#17140f; --panel:#211c15; --ink:#ece4d6; --muted:#a89b85;
    --line:#352d22; --accent:#c8515e; --accent-ink:#1a1410; --tag:#d0aa62; }
}
:root[data-theme=light]{ --bg:#f4efe6; --panel:#fbf8f2; --ink:#241f1a; --muted:#6f6455;
  --line:#e2d8c6; --accent:#7c2932; --accent-ink:#fff; --tag:#8a6d3b; }
:root[data-theme=dark]{ --bg:#17140f; --panel:#211c15; --ink:#ece4d6; --muted:#a89b85;
  --line:#352d22; --accent:#c8515e; --accent-ink:#1a1410; --tag:#d0aa62; }
*{box-sizing:border-box}
html,body{overflow-x:hidden}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;}
.wrap{max-width:720px;margin:0 auto;padding:28px 18px 64px;}
header.top{text-align:center;padding:22px 0 8px;}
header.top .eyebrow{font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;
  color:var(--tag);margin:0 0 8px;}
header.top h1{font:600 2.15rem/1.08 Georgia,"Times New Roman",serif;
  margin:0;overflow-wrap:break-word;}
@media(min-width:480px){header.top h1{font-size:2.6rem;}}
header.top p{color:var(--muted);margin:10px 0 0;font-size:.95rem;}
.rule{height:1px;background:var(--line);margin:26px 0;}
.group{background:var(--panel);border:1px solid var(--line);border-radius:14px;
  padding:20px 18px;margin:22px 0;}
.ghead{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;}
.ghead h2{font:600 1.5rem Georgia,serif;margin:0;}
.tag{font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--accent-ink);
  background:var(--accent);padding:3px 9px;border-radius:999px;font-weight:600;}
.players{color:var(--muted);margin:8px 0 16px;font-size:.9rem;}
.bundles{display:grid;grid-template-columns:1fr 1fr;gap:10px;}
.bundle{display:flex;flex-direction:column;gap:3px;text-decoration:none;color:var(--ink);
  background:var(--bg);border:1px solid var(--line);border-radius:11px;
  padding:14px 16px;transition:.15s;}
.bundle:hover{border-color:var(--accent);transform:translateY(-1px);}
.bundle .inst{font-weight:600;font-size:1.05rem;}
.bundle .pp{font-size:.76rem;color:var(--muted);letter-spacing:.03em;}
details{margin-top:16px;}
summary{cursor:pointer;color:var(--muted);font-size:.86rem;padding:6px 0;
  list-style:none;}
summary::-webkit-details-marker{display:none}
summary::before{content:"▸ ";color:var(--accent);}
details[open] summary::before{content:"▾ ";}
table{width:100%;border-collapse:collapse;margin-top:10px;font-size:.86rem;}
th{text-align:left;color:var(--muted);font-weight:600;font-size:.72rem;
  text-transform:uppercase;letter-spacing:.08em;padding:6px 8px;border-bottom:1px solid var(--line);}
td{padding:8px;border-bottom:1px solid var(--line);vertical-align:middle;}
td.pc{font-weight:500;}
td.src{color:var(--muted);font-size:.78rem;}
td.lk{white-space:nowrap;}
td.lk a{display:inline-block;min-width:26px;text-align:center;text-decoration:none;
  color:var(--accent);font-weight:600;padding:2px 5px;border-radius:6px;}
td.lk a:hover{background:var(--accent);color:var(--accent-ink);}
footer{color:var(--muted);font-size:.8rem;text-align:center;margin-top:34px;line-height:1.7;}
footer a{color:var(--accent);}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <p class="eyebrow">String Quartets · Reading Party</p>
    <h1>Boccherini Sampler</h1>
    <p>Tap your instrument to download every part for your group in one PDF —
       works are bookmarked in program order. Individual works are below each group.</p>
  </header>
  <div class="rule"></div>
__SECTIONS__
  <footer>
    Parts typeset in <strong>LilyPond</strong> where available (Op.&nbsp;2–26),
    otherwise IMSLP / public-domain scans.<br>
    Boccherini quartets · assembled for tonight's reading.
  </footer>
</div>
</body>
</html>
"""


if __name__ == "__main__":
    main()
