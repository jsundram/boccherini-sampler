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
IMSLP_OPUS = SCORES / "Boccherini-imslp-opus"
KM = SCORES / "Boccherini-KM"

INSTRUMENTS = ["V1", "V2", "VA", "VC"]

SITE_URL = "https://jsundram.github.io/boccherini-sampler/"
DESC = ("Download your Boccherini string-quartet parts — one PDF per instrument "
        "for each group, plus bonus quartets graded by cello difficulty.")
DIFFICULTY_URL = ("https://docs.google.com/spreadsheets/d/"
                  "1QsMy2oQVhYf2KTSVJVKT4CxvkMuD9i87AHJLUqsRMUA/edit?gid=0#gid=0")
FLOATING = "Roberta / Grant"  # play with either group

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

def leduc39():
    # Op.39 (G.213) is a single quartet; the LeDuc bundle is that whole quartet.
    return {p: (IMSLP_OPUS / f"Boccherini-039-all-{p}.LeDuc.pdf", None)
            for p in INSTRUMENTS}

# Program --------------------------------------------------------------------
# Each piece: (title, slug, source-dict, source-label)
GROUPS = {
    "Group 1": {
        "subtitle": "Harder cello",
        "players": "Jason / Leah, Kath, Josh",
        # (title, slug, sources, source-label, cello-difficulty or None)
        "pieces": [
            ("Op. 8 No. 2 (G.166)",  "Op08-No2-G166", lily(8, 2, 166),  "LilyPond", None),
            ("Op. 15 No. 4 (G.180)", "Op15-No4-G180", lily(15, 4, 180), "LilyPond", 1),
            ("Op. 22 No. 4 (G.186)", "Op22-No4-G186", lily(22, 4, 186), "LilyPond", 2),
            ("Op. 24 No. 4 (G.192)", "Op24-No4-G192", lily(24, 4, 192), "LilyPond", 4),
            ("Op. 33 No. 5 (G.211)", "Op33-No5-G211", op33_5(),         "IMSLP",    3),
            ("Op. 58 No. 5 (G.246)", "Op58-No5-G246", km58(5),          "IMSLP",    2),
        ],
    },
    "Group 2": {
        "subtitle": "Easier cello",
        "players": "Casey / Stephen, Jon, Zon",
        "pieces": [
            ("Op. 2 No. 6 (G.164)",  "Op02-No6-G164", lily(2, 6, 164),  "LilyPond", 2),
            ("Op. 8 No. 1 (G.165)",  "Op08-No1-G165", lily(8, 1, 165),  "LilyPond", 1),
            ("Op. 8 No. 3 (G.167)",  "Op08-No3-G167", lily(8, 3, 167),  "LilyPond", 1),
            ("Op. 15 No. 1 (G.177)", "Op15-No1-G177", lily(15, 1, 177), "LilyPond", 2),
            ("Op. 24 No. 6 (G.194)", "Op24-No6-G194", lily(24, 6, 194), "LilyPond", 1),
            ("Op. 44 No. 4 (G.223)", "Op44-No4-G223", imslp_individual(44, 4, 223), "IMSLP", 1),
            ("Op. 58 No. 4 (G.245)", "Op58-No4-G245", km58(4),          "IMSLP",    3),
        ],
    },
}

INSTRUMENT_LABEL = {"V1": "Violin I", "V2": "Violin II", "VA": "Viola", "VC": "Cello"}

# Bonus works — every quartet in the difficulty sheet that we have parts for and
# that ISN'T already assigned to Group 1 or 2. Difficulty/key/duration are the
# cello-part figures from the sheet. Split later into Easier (<=3) / Harder (>=4).
# (title, slug, sources, source-label, difficulty, key, duration)
BONUS = [
    ("Op. 2 No. 1 (G.159)",  "Op02-No1-G159", lily(2, 1, 159),  "LilyPond", 3, "C minor",  "17–18 min"),
    ("Op. 2 No. 2 (G.160)",  "Op02-No2-G160", lily(2, 2, 160),  "LilyPond", 3, "B♭ major", "12–13 min"),
    ("Op. 2 No. 5 (G.163)",  "Op02-No5-G163", lily(2, 5, 163),  "LilyPond", 4, "E major",  "12–13 min"),
    ("Op. 8 No. 4 (G.168)",  "Op08-No4-G168", lily(8, 4, 168),  "LilyPond", 4, "G minor",  "14–15 min"),
    ("Op. 8 No. 6 (G.170)",  "Op08-No6-G170", lily(8, 6, 170),  "LilyPond", 2, "A major",  "15–16 min"),
    ("Op. 22 No. 1 (G.183)", "Op22-No1-G183", lily(22, 1, 183), "LilyPond", 2, "C major",  "7–8 min"),
    ("Op. 22 No. 3 (G.185)", "Op22-No3-G185", lily(22, 3, 185), "LilyPond", 5, "E♭ major", "10–11 min"),
    ("Op. 24 No. 1 (G.189)", "Op24-No1-G189", lily(24, 1, 189), "LilyPond", 3, "D major",  "17–18 min"),
    ("Op. 24 No. 5 (G.193)", "Op24-No5-G193", lily(24, 5, 193), "LilyPond", 5, "C minor",  "16–17 min"),
    ("Op. 39 (G.213)",       "Op39-G213",     leduc39(),        "IMSLP",    3, "A major",  "19–20 min"),
    ("Op. 58 No. 2 (G.243)", "Op58-No2-G243", km58(2),          "IMSLP",    4, "E♭ major", "20–21 min"),
]


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
            for title, slug, sources, _lbl, _diff in g["pieces"]:
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

    # bonus works: individual per-work parts only (no merged bundles)
    for title, slug, sources, _lbl, *_meta in BONUS:
        for inst in INSTRUMENTS:
            src, rng = sources[inst]
            if not src.exists():
                missing.append(str(src))
                continue
            pw = PdfWriter()
            add_source(pw, src, rng, title)
            with open(pieces_dir / f"{slug}-{inst}.pdf", "wb") as fh:
                pw.write(fh)
    print(f"bonus: {len(BONUS)} works -> individual parts")

    if missing:
        print("\nMISSING SOURCES:")
        for m in missing:
            print("  ", m)
        raise SystemExit(1)

    write_index(bundle_pages)
    write_qr()
    print("\nBuild OK")


def write_qr():
    import segno
    qr = segno.make(SITE_URL, error="m")
    # high-res PNG data URI -> self-contained and crisp when printed
    uri = qr.png_data_uri(scale=20, border=3, dark="#241f1a", light="#ffffff")
    html = QR_TEMPLATE.replace("__QR__", uri).replace("__URL__", SITE_URL)
    (HERE / "qr.html").write_text(html, encoding="utf-8")
    print(f"qr.html written ({qr.version=}, {len(uri)//1024} KB)")


# ---------------------------------------------------------------------------
def pips(diff):
    """Difficulty as filled/empty dots + 'n/5' (or an em dash if unrated)."""
    if not diff:
        return '<span class="pips">·····</span> <span class="nd">n/a</span>'
    dots = f'<span class="on">{"●" * diff}</span>{"●" * (5 - diff)}'
    return f'<span class="pips">{dots}</span> {diff}/5'


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
        for title, slug, _sources, lbl, diff in g["pieces"]:
            links = " ".join(
                f'<a href="pieces/{slug}-{inst}.pdf" download>{inst}</a>'
                for inst in INSTRUMENTS
            )
            rows.append(
                f'<tr><td class="pc">{esc(title)}'
                f'<span class="meta">{lbl}</span></td>'
                f'<td class="diff">{pips(diff)}</td>'
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
        <table class="btbl">
          <thead><tr><th>Work</th><th>Cello diff.</th><th>Parts</th></tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </details>
    </section>""")

    floating = f"""
    <div class="floating">
      <span class="ftag">Floating</span>
      <span class="fnames">{esc(FLOATING)}</span>
      <span class="fnote">— play with either group</span>
    </div>"""
    body = (floating.join(sections) if len(sections) == 2
            else "".join(sections) + floating)

    # ---- bonus section --------------------------------------------------
    def bonus_card(label, tag, works):
        rows = []
        for title, slug, _src, _lbl, diff, key, dur in works:
            links = " ".join(
                f'<a href="pieces/{slug}-{inst}.pdf" download>{inst}</a>'
                for inst in INSTRUMENTS
            )
            rows.append(
                f'<tr><td class="pc">{esc(title)}'
                f'<span class="meta">{esc(key)} · {esc(dur)}</span></td>'
                f'<td class="diff">{pips(diff)}</td>'
                f'<td class="lk">{links}</td></tr>'
            )
        return f"""
    <section class="group bonus">
      <div class="ghead"><h2>{esc(label)}</h2><span class="tag">{esc(tag)}</span></div>
      <table class="btbl">
        <thead><tr><th>Work</th><th>Cello diff.</th><th>Parts</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>"""

    easier = [w for w in BONUS if w[4] <= 3]
    harder = [w for w in BONUS if w[4] >= 4]
    bonus_html = f"""
    <div class="rule"></div>
    <div class="bintro">
      <h2>Bonus quartets</h2>
      <p>More quartets we have parts for, beyond tonight's two programs — graded
         (cello part) from the <a href="{DIFFICULTY_URL}" target="_blank" rel="noopener">difficulty assessment</a>.
         Grab any part.</p>
    </div>
    {bonus_card("Bonus · Easier", "Difficulty 1–3", easier)}
    {bonus_card("Bonus · Harder", "Difficulty 4–5", harder)}"""

    html = (TEMPLATE
            .replace("__SECTIONS__", body)
            .replace("__BONUS__", bonus_html)
            .replace("__DIFFICULTY_URL__", DIFFICULTY_URL)
            .replace("__DESC__", esc(DESC))
            .replace("__SITE_URL__", SITE_URL))
    (HERE / "index.html").write_text(html, encoding="utf-8")
    print("index.html written")


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Boccherini Sampler</title>
<meta name="description" content="__DESC__">
<link rel="canonical" href="__SITE_URL__">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/favicon-48.png" sizes="48x48" type="image/png">
<meta name="theme-color" content="#f4efe6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#17140f" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Boccherini Sampler">
<meta property="og:title" content="Boccherini Sampler">
<meta property="og:description" content="__DESC__">
<meta property="og:url" content="__SITE_URL__">
<meta property="og:image" content="__SITE_URL__assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Boccherini Sampler">
<meta name="twitter:description" content="__DESC__">
<meta name="twitter:image" content="__SITE_URL__assets/og.png">
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
header.top .links{margin-top:14px;}
header.top .links a{display:inline-block;color:var(--accent);text-decoration:none;
  font-weight:600;font-size:.9rem;border:1px solid var(--line);border-radius:999px;
  padding:7px 16px;}
header.top .links a:hover{border-color:var(--accent);}
.rule{height:1px;background:var(--line);margin:26px 0;}
.floating{display:flex;align-items:center;gap:10px;flex-wrap:wrap;justify-content:center;
  text-align:center;margin:6px auto 2px;padding:12px 18px;max-width:520px;
  border:1px dashed var(--line);border-radius:999px;color:var(--muted);font-size:.9rem;}
.floating .ftag{font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--accent-ink);background:var(--tag);padding:3px 10px;border-radius:999px;font-weight:700;}
.floating .fnames{font-weight:600;color:var(--ink);}
.floating .fnote{font-size:.82rem;}
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
.bintro{text-align:center;max-width:560px;margin:0 auto;}
.bintro h2{font:600 1.6rem Georgia,serif;margin:0 0 6px;}
.bintro p{color:var(--muted);font-size:.9rem;margin:0;}
.bintro a{color:var(--accent);}
.group.bonus{padding-top:16px;}
table.btbl{width:100%;border-collapse:collapse;font-size:.86rem;}
table.btbl th{text-align:left;color:var(--muted);font-weight:600;font-size:.72rem;
  text-transform:uppercase;letter-spacing:.08em;padding:6px 8px;border-bottom:1px solid var(--line);}
table.btbl td{padding:9px 8px;border-bottom:1px solid var(--line);vertical-align:middle;}
table.btbl td.pc{font-weight:600;line-height:1.25;}
table.btbl td.pc .meta{display:block;font-weight:400;color:var(--muted);font-size:.76rem;margin-top:2px;}
table.btbl td.diff{white-space:nowrap;color:var(--muted);font-size:.8rem;}
.pips{letter-spacing:1px;color:var(--line);}
.pips .on{color:var(--accent);}
.nd{color:var(--muted);font-size:.78rem;font-style:italic;}
table.btbl td.lk{white-space:nowrap;text-align:right;}
table.btbl td.lk a{display:inline-block;min-width:26px;text-align:center;text-decoration:none;
  color:var(--accent);font-weight:600;padding:2px 5px;border-radius:6px;}
table.btbl td.lk a:hover{background:var(--accent);color:var(--accent-ink);}
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
    <p class="links"><a href="__DIFFICULTY_URL__" target="_blank" rel="noopener">Difficulty assessment&nbsp;↗</a></p>
  </header>
  <div class="rule"></div>
__SECTIONS__
__BONUS__
  <footer>
    Parts typeset in <strong>LilyPond</strong> where available (Op.&nbsp;2–26),
    otherwise IMSLP / public-domain scans.<br>
    Boccherini quartets · assembled for tonight's reading.
  </footer>
</div>
</body>
</html>
"""


QR_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Boccherini Sampler — Scan</title>
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/favicon-48.png" sizes="48x48" type="image/png">
<meta name="theme-color" content="#f4efe6">
<style>
:root{ --ink:#241f1a; --muted:#6f6455; --accent:#7c2932; --bg:#f4efe6; }
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--ink);
  font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;}
.card{width:100%;max-width:520px;text-align:center;}
.eyebrow{font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;
  color:var(--accent);margin:0 0 8px;font-weight:700;}
h1{font:600 2.2rem/1.05 Georgia,"Times New Roman",serif;margin:0 0 6px;}
.sub{color:var(--muted);margin:0 0 26px;}
.qr{width:70%;max-width:340px;height:auto;margin:0 auto;display:block;
  border-radius:12px;background:#fff;padding:14px;
  box-shadow:0 1px 0 rgba(0,0,0,.06);}
.url{margin:22px auto 0;font:600 .72rem/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;
  color:var(--ink);white-space:nowrap;}
@media(min-width:600px){ .url{font-size:1rem;} }
.hint{color:var(--muted);font-size:.9rem;margin-top:8px;}
@media print{
  @page{ size:letter; margin:0.6in; }
  :root{ --bg:#fff; }
  html,body{background:#fff;}
  body{display:block;padding:0;min-height:0;}
  .card{max-width:none;margin:1in auto 0;}
  h1{font-size:32pt;}
  .sub{font-size:13pt;margin-bottom:0.45in;}
  .qr{width:3.8in;max-width:none;padding:0;box-shadow:none;border-radius:0;}
  .url{font-size:15pt;margin-top:0.4in;}
  .hint{font-size:11pt;}
}
</style>
</head>
<body>
  <main class="card">
    <p class="eyebrow">String Quartets · Reading Party</p>
    <h1>Boccherini Sampler</h1>
    <p class="sub">Scan to download your parts</p>
    <img class="qr" src="__QR__" alt="QR code linking to __URL__" width="360" height="360">
    <p class="url">__URL__</p>
    <p class="hint">Point your phone camera at the code, or type the address above.</p>
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    main()
