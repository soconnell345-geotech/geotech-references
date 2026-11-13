"""Check that every typed GEC-13 table row (chapters 2 to 10) splits into as many
cells as the table has columns ('; ' between cells, ' | ' between rows).

The column count is the number of cells in the header, found as the first '. '
split of the 'columns:' text where header and first row have the same count (the
print itself holds '. ' in heads such as 'No. of PVDs').  Run:
    python scripts/check_gec13_cells.py
Exit code 1 if any row is off.
"""
import json
import pathlib
import re
import sys
from collections import Counter

TEXT = pathlib.Path(__file__).resolve().parents[1] / "geotech_references" / "gec_13" / "text"
NOTES = re.compile(r"\.\s+Notes?:\s")


def split_entry(entry):
    """Return (header cells, [row cells ...]) of one typed table entry."""
    body = entry.split(" - columns: ", 1)[1]
    m = NOTES.search(body)
    if m:
        body = body[:m.start()]
    chunks = body.split(" | ")
    rest = [c.split("; ") for c in chunks[1:]]
    if rest:
        k = Counter(len(r) for r in rest).most_common(1)[0][0]
    else:
        k = None
    first = chunks[0]
    for mm in re.finditer(r"\.\s", first):
        h, r0 = first[:mm.start()].split("; "), first[mm.end():].split("; ")
        if (k is None and len(h) == len(r0)) or (k is not None and len(h) == k and len(r0) == k):
            return h, [r0] + rest
    return None, None


def main():
    bad = total = tables = 0
    for ch in range(2, 11):
        p = TEXT / f"chapter{ch:02d}.json"
        if not p.exists():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        for s in data["sections"]:
            for t in s.get("tables", []):
                m = re.match(r"Table (\d+-\d+): ", t)
                if not m or " - columns: " not in t:
                    continue
                tables += 1
                h, rows = split_entry(t)
                if h is None:
                    print(f"{m.group(1)}: header not found")
                    bad += 1
                    continue
                for i, r in enumerate(rows):
                    total += 1
                    if len(r) != len(h):
                        bad += 1
                        print(f"{m.group(1)} row {i}: {len(r)} cells for {len(h)} columns: {'; '.join(r)[:120]!r}")
    print(f"{tables} tables, {total} rows, {bad} off")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
