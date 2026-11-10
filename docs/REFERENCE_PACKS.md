# Local reference packs

A **reference pack** adds a deployment's own reference (an agency manual, a
design guide, a standard the deployment holds) to this library without
putting it in the public repositories or the wheel. Once a pack is in
place, `reference_search`, `reference_get`, `figure_search`, `figure_get`
and `resolve_pdf` treat it as they treat the built-in references: the same
BM25 ranking and synonym expansion, the same section tree, the same
citations, the same figure read-off.

A pack is **private deployment data**. Keep it outside this package and
outside any git work tree of the public repositories; `check` refuses a
pack in either place. Never commit a pack, its text or its PDF to a public
repository.

(BACKLOG REF-64; new in geotech-references 1.6.0.)

## The format

A pack is a folder in the layout of a built-in reference package, minus the
Python:

```
local_example_manual/          # the pack; the folder name is the pack id
  pack.json                    # who, what, which edition, which PDF
  text/chapter01.json ...      # one file per chapter, to the chapter schema
  figures_catalog.json         # optional: the figures, for search and read-off
  Example Manual 2026.pdf      # optional here; else found by name (below)
```

There is no executable code in a pack: no `tables.py`, no `figures.py`.
Numbers come from the printed text the librarian reads; computed lookups
stay in the public library.

### `pack.json`

| Key | Required | What |
|---|---|---|
| `id` | yes | Starts with `local_`, and is the folder's name. It never collides with a built-in reference, and every citation shows the reference is the deployment's own. |
| `reference_id` | yes | The designation as printed on the cover (the chapter files carry the same). |
| `reference_title` | yes | The title as printed (the chapter files carry the same). |
| `edition` or `date` | recommended | As printed. |
| `pdf_files` | recommended | The PDF file names: bare names only, with no folder, `..` or drive. |
| `prepared_by`, `prepared_on` | recommended | Who built the pack, and when. |
| `method` | recommended | `printed` (read off the print), `model` (written by a model to the schema) or `hand`. |
| `distribution` | recommended | A free-text note, for example "agency internal; not for the public repos". |

### Chapter files (`text/chapterNN.json`)

The schema is the one every built-in reference uses. It ships in the wheel;
`python -m geotech_references.packs schema > chapter_schema.json` saves a
copy. Top-level `reference_id`, `reference_title`, `volume`, `chapter`,
`chapter_title`, `sections`; each section `section_id`, `title`, `body`,
`key_points`, `equations`, `figures`, `tables`, `applicability`, optionally
`summary` and nested `subsections`. A file may list every level as its own
entry (`4`, `4.3`, `4.3.1`) or nest subsections; both are read into one
section tree.

A minimal chapter file (made up, as every example here is):

```json
{
  "reference_id": "EX-01",
  "reference_title": "Example Manual",
  "volume": null,
  "chapter": 4,
  "chapter_title": "Settlement of Made-up Fill",
  "sections": [
    {
      "section_id": "4.1",
      "title": "Scope",
      "body": "[p. 4-1] This chapter covers embankments built of a made-up fill.",
      "key_points": [],
      "equations": [],
      "figures": [],
      "tables": [],
      "applicability": "Embankments of the made-up fill."
    },
    {
      "section_id": "4.2",
      "title": "Settlement",
      "body": "[p. 4-2] The fill settles by a fixed share of its height, Equation 4-1. Figure 4-2 shows the settlement against the height.",
      "key_points": [],
      "equations": [
        {"id": "Eq. 4-1", "description": "settlement of the made-up fill",
         "formula": "s = 0.01 H", "source": "p. 4-2", "implemented_in": null}
      ],
      "figures": ["Figure 4-2 Settlement of a made-up fill"],
      "tables": [],
      "applicability": "Embankments of the made-up fill, any height."
    }
  ]
}
```

### Figure catalog (`figures_catalog.json`)

```json
{
  "reference_id": "EX-01",
  "reference_title": "Example Manual",
  "package": "local_example_manual",
  "volume": null,
  "pdf_path": "Example Manual 2026.pdf",
  "figures": [
    {"figure_number": "4-2", "caption": "Settlement of a made-up fill",
     "chapter": 4, "pdf_page_index": 57, "printed_page": 4,
     "page_estimated": false, "description": "",
     "bbox": [54, 90, 560, 640],
     "read_notes": "x axis is logarithmic; read at the curve's centreline"}
  ]
}
```

- `pdf_path` (catalog or figure) is a **bare file name only**, with no
  folder, `..` or drive, so no host path reaches the model and no pack
  leads outside its folder. A catalog that gives a path is refused by
  `check` and left out of the figure index.
- `pdf_page_index` is 0-based; `printed_page` is the number printed on the
  page. Set `page_estimated: true` where the page is a best estimate.
- Two **optional** fields give control over each figure's vision read
  (built-in figures carry neither; `figure_get` returns them only where
  given):
  - `bbox: [x0, y0, x1, y1]`, in PDF points with a top-left origin, the box
    of the chart on the page. The reader crops to it, so the chart, not the
    whole page, fills the image. Use it for dense curve families.
  - `read_notes`: at most 500 characters on how to read the chart (a
    logarithmic axis, how curves are labelled, where to read them).
- A table printed as a picture can go in the catalog as an entry numbered
  `Table 5-3`; it is read like a figure.

## The print-fidelity rules

A pack is held to the same rules as the built-in text: the librarian cites
it as it cites a printed manual, so what it says must be what the page
says.

1. **Bodies in the print's own wording**, with page markers: `[p. 4-12]`
   where the text on that page begins.
2. **`summary` and `key_points` only where they restate the print.** Leave
   them out rather than paraphrase beyond it.
3. **Each equation typed from the printed page**: `formula` as printed,
   `source` naming the page (`"p. 4-12"`), `implemented_in: null`.
4. **Tables as printed lines in the body**, row by row.
5. **Section numbers as printed.** The id patterns are those of the
   built-ins: `5.7.2`, `4-2.1`, `P-1`, an annex letter `A`, `D.3`.
6. **Figures by their printed numbers and captions**, on the pages they are
   printed on.

`check` warns where it can see a rule broken (an equation with a formula
and no `source`; a body with no page marker). The rest is the preparer's
care.

## Making a pack

1. **Skeleton.**

   ```
   python -m geotech_references.packs new <packs folder>/local_example_manual --title "Example Manual" --reference-id "EX-01" --pdf "Example Manual 2026.pdf"
   ```

   This writes `pack.json` and an empty `text/`. Fill in the rest of
   `pack.json`, and copy the PDF into the pack folder or to where the
   deployment's reference PDFs go.

2. **Text.** Write `text/chapterNN.json` to the schema and the rules above,
   by hand or with a model given the printed pages. Read the result
   against the print.

3. **Catalog.** From a source checkout of this repository, with PyMuPDF:

   ```
   python scripts/build_figure_catalog.py --pack <packs folder>/local_example_manual
   ```

   It reads the PDF's List of Figures, finds each figure's page by
   searching for its caption, enriches descriptions from the pack's own
   text, and keeps any `bbox` / `read_notes` already in the catalog.
   (`--sequential` for figures numbered "Figure 1", "Figure 2"; `--pdf` for
   another PDF.) On a host with only the installed package, write the
   catalog from the List of Figures by hand; `check` then confirms each
   number is printed on the page it names.

4. **Check** (next section) until it passes.

## Checking a pack

```
python -m geotech_references.packs check <packs folder>/local_example_manual
```

It exits 0 when the pack can be used and 1 when it cannot, and prints
every error, warning and finding:

1. `pack.json`: the required keys, the `local_` prefix, the id equal to the
   folder name, no built-in id, text where text belongs, `pdf_files` bare
   file names; the folder outside the installed package and outside any
   git work tree of the public repositories.
2. Every chapter file: each field of the right kind (text where text
   belongs, lists where lists belong, at every level), then the library's
   own schema check (the one `scripts/audit_chapter_text.py` runs on the
   built-ins), `reference_id` and `reference_title` matching `pack.json`,
   unique chapter numbers.
3. The catalog: required fields, each field of the right kind, unique
   numbers, a page index of 0 or more, `pdf_path` a bare file name,
   `read_notes` of at most 500 characters, a well-formed `bbox`. With
   PyMuPDF installed and the PDF found (in the pack
   folder or `GEOTECH_REFERENCES_DOCS`): the page index within the PDF, the
   figure's number printed on that page (a warning, unless
   `page_estimated` is set) and the `bbox` inside the page.
4. Print-fidelity warnings (not errors).
5. A smoke test: it indexes the built-ins plus this pack (an error for any
   pack file the indexes leave out), searches for each chapter's title in
   the pack (and reports where its first hit ranks across the whole
   library), runs `figure_get` on the first figure and `resolve_pdf` on it.

A wrong value is reported as an `ERROR` line, never as a traceback.

Also:

- `python -m geotech_references.packs list` shows what
  `GEOTECH_REFERENCES_PACKS` resolves to, with counts and any pack skipped:
  what the app will see.
- `python -m geotech_references.packs index --rebuild` rebuilds the search
  indexes.
- `python -m geotech_references.packs schema` prints the chapter-file
  schema (above).

## Where packs live, and how they are found

`GEOTECH_REFERENCES_PACKS` holds one or more folders, separated by the
system's path separator (`:` on Linux and macOS, `;` on Windows). Each
folder is either a pack (it holds `pack.json`) or a folder of packs. It is
read at each call, as `GEOTECH_REFERENCES_DOCS` is.

A pack is skipped, and named by `list` (and `_packs.problems()`), when its
`pack.json` cannot be read, its id is a built-in reference's name or lacks
the `local_` prefix, or an earlier pack has the same id.

A bad pack file cannot break search. A chapter file or catalog that is not
readable JSON, has a list or an object where text belongs, or (a catalog)
names its PDF by a path is left out of the search indexes and named the
same way; the built-ins, the pack's other files and the other packs still
index. Each pack file is indexed under its own SQLite savepoint, so one
that fails anyway is rolled back and named.

The search indexes are built in the local temp folder, keyed by the pack
set (each indexed file's path, size and modification time), so a read-only
pack folder is fine and an edited pack gets a fresh index. With the setting
unset the library is exactly as it was before packs.

A pack figure's PDF is looked for by its file name in the pack's own
folder, then in `GEOTECH_REFERENCES_DOCS`, and nowhere else (never relative
to this repository, as a built-in's is in a source checkout). Where neither
has it, `resolve_pdf` raises `FileNotFoundError`, and an app that has a
fetcher for reference PDFs asks it by file name, so a pack's PDF can go
wherever the deployment's built-in PDFs go.

| Host | Packs live | Set |
|---|---|---|
| Foundry | committed in the workspace repository beside the app's entry file (for example `references/packs/`, next to the reference PDFs); or, if committed folders do not reach the published app, in the deployment's dataset store, copied to a temp folder at boot by the same step that fetches the PDFs | `os.environ.setdefault("GEOTECH_REFERENCES_PACKS", "<that folder>")` in the entry file |
| Databricks | a Workspace folder or a Unity Catalog volume | the environment variable, set before the app is launched |
| Tiny Apps | not needed: Tiny Apps hosts Document Review alone (`aec-document-review`), which has no librarian | — |

The Foundry workspace repository and the Tiny Apps wrapper repository are
the deployment's own, not the public repositories, so a pack may be
committed there.

## What packs deliberately do not do

- **No Python.** Running a deployment folder's code on a locked-down host is
  a security and review problem.
- **No raw PDFs indexed on the fly.** Unchecked text cannot carry
  page-accurate citations or formulas from the print.
- **No embeddings.** Lexical search plus the curated synonym groups is the
  library's lever, for packs as for the built-ins.
- **No pack-specific synonym groups.** The synonym table is global and
  curated; a pack's synonyms would move the ranking of built-in queries.
