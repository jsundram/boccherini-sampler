# Boccherini Sampler

Downloadable string-quartet parts for a two-group Boccherini reading party.
Each group gets one merged PDF per instrument (Violin I / II, Viola, Cello)
containing every work the group is playing, in program order, with a
bookmark per work.

**➡ Live page:** https://jsundram.github.io/boccherini-sampler/

## Program

**Group 1 — harder cello** (Jason / Leah, Kath, Josh · Roberta / Grant floating)
Op. 8/2, 15/4, 22/4, 24/4, 33/5, 58/5

**Group 2 — easier cello** (Casey / Stephen, Jon, Zon)
Op. 2/6, 8/1, 8/3, 15/1, 24/6, 44/4, 58/4

## Sources

Parts are LilyPond-typeset editions where available (Boccherini Op. 2–26).
The remaining works use public-domain IMSLP material:

- **Op. 33 No. 5** — split out of a whole-opus IMSLP part bundle
  (V1 pp. 15–18; V2/VA/VC pp. 9–10).
- **Op. 44 No. 4** — individual IMSLP parts.
- **Op. 58 Nos. 4 & 5** — individual parts (KM edition).

## Rebuilding

`build.py` regenerates `parts/`, `pieces/`, and `index.html` from the source
PDF libraries that live one level up in the `Scores/` directory
(`Boccherini-lilypond/`, `Boccherini-imslp/`, `Boccherini-KM/`). Those source
libraries are **not** part of this repo; the generated PDFs are committed
directly.

```
python3 build.py      # needs pypdf
```
