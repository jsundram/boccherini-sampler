# Plan — boccherini-sampler as a focused "bundler"

## Why this exists / the trigger

Assembling parts for a reading party surfaced a class of bug: a whole-opus part
book was split by hand-typed page ranges, and one part (Op.33/5 Violin II) silently
dropped its final page. The fix that night was real, but the deeper lesson is that
**source selection, extraction, and completeness were all being improvised inside the
sampler** from ad-hoc filename scraping of `~/Dropbox/Docs/Scores/Boccherini-*`.

This plan separates the concerns so the sampler can "do one thing well," and so
"no missing pages" becomes a checkable invariant rather than a hope.

## Two repos, clear responsibilities

### `boccherini-quartet-data` — authoritative source-of-truth (step 0)
Already provides: the catalog (`generated/opera.json`, built from the Quartets +
Movements Google Sheets), the **LilyPond sources** that produce parts (Op. 2–26, 32,
33), and non-IMSLP provenance research (`docs/beyond_imslp.md`).

**To add (this plan's "task 1", owned by Jason):** a machine-readable
**editions manifest** — see `editions.schema.json` + `editions.example.json` here.
For every quartet it lists the available editions and, per part, the authoritative
**page count** (the completeness fact). Ideally it also *builds clean per-work
per-part PDFs* from LilyPond where possible, so the sampler never has to split.

### `boccherini-sampler` — the bundler (this repo)
Its one job: **given (a set of works, an edition choice per work, a player grouping),
produce per-player bundles that are provably complete, and publish them.**
Difficulty/comments are an annotation layer on top.

```
opera.json (catalog) ─┐
editions.json ────────┼─▶ resolve chosen editions ─▶ concatenate per player ─▶ VERIFY ─▶ publish site
difficulty sheet ─────┘        (edition = input)         (+ bookmarks)        (pages==declared,
                                                                               all parts present)
```

## Key decisions (agreed)

1. **Splitting lives in the data layer, not the sampler.** Prefer normalizing every
   usable source into clean per-work parts with declared page counts. Where a part
   still comes from a bundle, the manifest declares `source_pages` **and** `pages`,
   and the sampler asserts `len(source_pages) == pages`. Either way the sampler only
   ever *concatenates atomic, page-count-verified units* — so it structurally cannot
   drop a page.

2. **Edition preference is a sampler input, never hardcoded.** It can vary by player,
   group, or reading context. The manifest only lists what's *available*; the caller
   picks (with an optional default ordering, e.g. lilypond → clean scan → bundle).

3. **Completeness is verified against declared truth** (`pages`). This is what makes
   heterogeneous sources safe: for a LilyPond PDF the boundary is also text-checkable,
   but for an image-only scan the declared `pages` is the *only* signal — and it's
   enough. The sampler **fails closed**: any missing part, missing edition, or
   `actual_pages != declared_pages` stops the build.

## The contract

- **`editions.schema.json`** — JSON Schema (draft 2020-12) for the manifest.
- **`editions.example.json`** — a 4-work sample with **real page counts**, covering
  all three `form`s: `per-work-parts` (G166 LilyPond + KM), `opus-bundle` with
  `source_pages` (G211 — the exact Op.33/5 case), and image-only scans (G223, G246).
- Keyed by **Gérard number**. Catalog fields (title/key/movements/year/links) are
  **not** duplicated — join to `opera.json` by `gerard`.

## Migration roadmap (incremental — don't break the working build)

1. **[data repo]** Emit `editions.json` for what already exists (LilyPond Op. 2–26/32/33,
   KM Op. 58, IMSLP individual Op. 44/4, the Op. 33 bundle). Flag works with no parts.
2. **[sampler]** Add a resolver that reads `opera.json` + `editions.json` and returns
   verified part units. Keep the current hardcoded `GROUPS`/`BONUS` path working in
   parallel until the resolver is trusted.
3. **[sampler]** Difficulty-sheet ingestion: fetch the published CSV, **cache it in-repo**
   (`difficulty.csv`) so builds are reproducible/offline and the sheet's evolution shows
   up in git history; parse to per-work `{difficulty, comment}` joined by Gérard number.
4. **[sampler]** Move bundle selection into data: a `bundles.json` declaring each group's
   works, chosen edition per work, and player roster (replacing hardcoded tuples).
5. **[sampler]** Verification pass: `actual_pages == declared_pages` for every unit +
   all requested parts present; fail closed; emit a report. Retire the current
   text-boundary `verify_splits` once units are atomic (or keep it as a bonus check for
   `text: true` sources).
6. **[sampler]** Delete the filename-scraping of `Boccherini-*`; depend only on the
   manifest + resolved part files.

## Open questions

- **Where do the built part PDFs physically live**, and how does the sampler read them?
  Options: committed in the data repo, published to a base URL (`parts_base`), a git
  submodule, or a local path. (Affects `parts_base` and whether the sampler vendors a
  snapshot.)
- **Is `editions.json` committed** in the data repo (it currently gitignores `generated/`),
  or does the sampler fetch/vendor it? The sampler needs a stable, pinned copy per build.
- **Difficulty-sheet row identity**: it keys rows by `G###` and `opus#number`; confirm
  that's a clean join to Gérard numbers, and how edition-choice notes in that sheet
  (if any) relate to `editions.json`.
- **Multi-file parts** (a single part scanned across two PDFs) — extend `part` to accept
  an ordered list of `{file, pages}` if/when it comes up.
- **Score bundles**: do we want per-work scores in the sampler too, or parts-only?
