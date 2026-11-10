"""Read a manual printed in the Army publication layout off its pages (no API).

``scripts/build_printed_text.py`` hands a volume to this module when its
manifest entry says ``"layout": "army"``. The layout is the one USACE engineer
manuals typeset in Word share (EM 1110-1-1905, 31 July 2025, is the first
built this way):

* pages numbered straight through ("EM 1110-1-1905 • 31 July 2025" and the
  page number in the footer), so a page marker is ``[p. 104]``;
* paragraphs numbered ``5–5.`` with a bold heading, their subparagraphs
  lettered and numbered the way the manual cites them: ``5–5a``,
  ``5–5a(2)``, ``5–5a(2)(b)``, ``2–7a(2)(c)1``. Every printed level is a
  section, and its ``section_id`` is that citation with a hyphen for the en
  dash (``5-5a(2)``). A subparagraph's title is its italic run-in heading;
  one printed without a heading takes its opening words as its title, and
  its ``applicability`` says so;
* equations set as Word equation objects and numbered ``(5–21)`` at the
  right margin. The text layer holds such an object as glyphs in no
  reading order, so every numbered equation must be typed in from the
  rendered page in the manifest's ``printed_equations`` (``number``,
  ``page``, ``formula``, ``variables``, optional ``notes``); the body shows
  the typed formula followed by ``[Eq. 5-21]``. A numbered equation with no
  typed formula stops the build unless ``--draft`` is given;
* tables set as ruled Word tables: a table's cells are read from its rules
  (cells of one printed row on one line, ``" | "`` between cells), a merged
  cell repeated on each row it spans. A table whose cells are equations is
  typed in from the rendered page (``printed_tables``: ``number``,
  ``rows``), and so is one printed as a picture;
* figures placed as pictures over a caption ``Figure 5–4. ...``; lettering
  the text layer holds inside a picture is left out.

Text outside the numbered equations is the print's own wording. Where the
print sets mathematics in running text or in a table cell, its characters
are placed by where they sit on the page, not by their order in the file: a
raised character is written after ``^`` (``ft^2``, ``tan^2``), a lowered one
straight after its symbol (``qult``, ``Nq``), a built-up fraction from the
bar the page draws as ``(numerator)/(denominator)``, a root as ``√(...)``;
a raised note mark in a table is ``[1]``. An en dash between the parts of a
number is written as a hyphen (``Table 5-2``, ``paragraph 5-5a(2)``), the
way section, figure and equation numbers are written everywhere else in the
library. Mathematics the placement rules cannot read (pieces stacked where
no fraction bar is drawn) is listed by the build and stops it until the
manifest types the passage in (``printed_passages``: ``page``, ``find``,
``replace``) or accepts it as read (``accepted_math``).

Requires PyMuPDF.
"""

from __future__ import annotations

import json
import re
from collections import Counter
import unicodedata
from dataclasses import dataclass, field, replace

try:
    import pymupdf as fitz
except ImportError:  # older PyMuPDF
    import fitz

# ---------------------------------------------------------------------------
# characters
# ---------------------------------------------------------------------------

#: Private-use code points of the Symbol font, each checked on the rendered
#: page it is printed on (EM 1110-1-1905 pp. 27 and 106).
SYMBOL_FONT = {0xF062: "β", 0xF06D: "μ", 0xF070: "π", 0xF071: "θ"}
#: Characters written another way: the phi and epsilon variants as the plain
#: Greek letters, the multiplication dots as one dot, slashes as "/".
_FOLD = {"ϕ": "φ", "ϵ": "ε", "∙": "·", "⋅": "·", "∕": "/", "‑": "-", "Ʌ": "Λ", "ʋ": "υ",
         "∗": "*", "ﬁ": "fi", "ﬂ": "fl", "∆": "Δ"}
_FRACTION_SLASH = "⁄"
_PRIMES = "′″‴*"
_DELIMS = "()[]{}|⌈⌉⌊⌋"
#: A unit a raised number in the text font is a power of ("ft2", "psf-1");
#: so is a raised negative number, or one after a 10. Any other raised mark
#: in the text font is a note mark.
_UNIT_END = re.compile(r"(?:ft|in|yd|mi|mm|cm|km|m|sec|s|psf|ksf|tsf|pcf|kcf|lb|kg|kN|N)$")
_NEGATIVE = re.compile(r"[−–-]\d+")


def plain_char(ch: str, font: str) -> str:
    """One character of the text layer as plain text."""
    o = ord(ch)
    if 0xE000 <= o <= 0xF8FF:
        if "Symbol" in font and o in SYMBOL_FONT:
            return SYMBOL_FONT[o]
        raise ValueError(f"private-use character U+{o:04X} in font {font} has "
                         "no checked reading (SYMBOL_FONT)")
    if 0x1D400 <= o <= 0x1D7FF or ch == "ℎ":
        ch = unicodedata.normalize("NFKC", ch)
    return _FOLD.get(ch, ch)


@dataclass
class Ch:
    """A character (or a fraction already read, ``frac``) placed on the page."""
    t: str
    x0: float
    x1: float
    y: float          # baseline
    top: float
    bot: float
    size: float
    math: bool = False
    bold: bool = False
    italic: bool = False
    frac: bool = False
    role: str = "base"  # base / sup / sub
    doubt: bool = False  # holds a root whose bar was not found

    @property
    def xc(self) -> float:
        return (self.x0 + self.x1) / 2


@dataclass
class Bar:
    """A short horizontal rule: a fraction bar, a root's bar or an underline."""
    y: float
    x0: float
    x1: float


@dataclass
class Row:
    """One printed line of text, its characters in reading order."""
    items: list
    y: float
    size: float
    text: str = ""
    crowded: bool = False   # set where rows stack closer than lines of text do
    spaces: list = field(default_factory=list, repr=False)
    radicals: tuple = field(default=(), repr=False)

    @property
    def x0(self) -> float:
        return min(i.x0 for i in self.items)

    @property
    def x1(self) -> float:
        return max(i.x1 for i in self.items)

    @property
    def top(self) -> float:
        return min(i.top for i in self.items)

    @property
    def bot(self) -> float:
        return max(i.bot for i in self.items)

    @property
    def bold(self) -> bool:
        """Whether the line is set in bold (a symbol in the mathematics
        font inside a bold caption has no bold of its own)."""
        base = [i for i in self.items
                if i.role == "base" and i.t.isalnum() and not i.math and not i.frac]
        return bool(base) and all(i.bold for i in base)

    @property
    def type_size(self) -> float:
        """The size most of the line's text is set in (a symbol of the
        mathematics font in a 10 pt caption may be 12 pt)."""
        base = [round(i.size, 1) for i in self.items if i.role == "base" and not i.frac]
        text = [round(i.size, 1) for i in self.items
                if i.role == "base" and not i.math and not i.frac] or base
        return max(set(text), key=text.count) if text else self.size

    @property
    def math_share(self) -> float:
        base = [i for i in self.items if not i.t.isspace()]
        return sum(i.math for i in base) / len(base) if base else 0.0


def page_chars(page) -> tuple[list[Ch], list[tuple[float, float]]]:
    """Every upright character of a page, and where its spaces sit (x, y)."""
    chars, spaces = [], []
    for b in page.get_text("rawdict")["blocks"]:
        if b["type"] != 0:
            continue
        for ln in b["lines"]:
            if abs(ln["dir"][0] - 1) > 1e-3:      # lettering set on its side
                continue
            for s in ln["spans"]:
                font = s["font"]
                math = font.startswith("Cambria") or "Symbol" in font
                for c in s["chars"]:
                    ch = c["c"]
                    x0, top, x1, bot = c["bbox"]
                    if ch.isspace():
                        spaces.append((x0, c["origin"][1]))
                        continue
                    if unicodedata.combining(ch) and chars and not math:
                        # an accent set as its own character ("Hete" + accent
                        # + "nyi") belongs on the letter before it
                        chars[-1].t = unicodedata.normalize("NFC", chars[-1].t + ch)
                        continue
                    chars.append(Ch(plain_char(ch, font), x0, x1, c["origin"][1],
                                    top, bot, s["size"], math,
                                    "Bold" in font, "Italic" in font))
    return chars, spaces


def page_rules(page):
    """A page's ruled lines: ``(thin, heavy, bars, verticals)``. ``thin``
    are table cell borders ``(y, x0, x1)``, ``heavy`` the rules over a table
    ``(y, x0, x1)``, ``bars`` the fraction bars, root bars and underlines,
    ``verticals`` cell borders ``(x, y0, y1)``."""
    thin, heavy, bars, vert = [], [], [], []
    for d in page.get_drawings():
        for it in d["items"]:
            if it[0] != "re":
                continue
            r = it[1]
            if r.width > 3 and r.height <= 2.6:
                y = (r.y0 + r.y1) / 2
                if r.height >= 1.5:
                    heavy.append((y, r.x0, r.x1))
                elif r.height <= 0.55:
                    thin.append((y, r.x0, r.x1))
                else:
                    bars.append(Bar(y, r.x0, r.x1))
            elif r.height > 3 and r.width <= 0.55:
                vert.append(((r.x0 + r.x1) / 2, r.y0, r.y1))
    return thin, heavy, bars, vert


# ---------------------------------------------------------------------------
# a set of characters as printed lines
# ---------------------------------------------------------------------------

def _wrap(text: str, symbols: int = 1) -> str:
    """Brackets round a numerator or denominator unless it is one number
    or one symbol (``symbols`` is how many full-size letters it holds)."""
    if re.fullmatch(r"[\d.,]+%?", text):
        return text
    if symbols <= 1 and re.fullmatch(r"[^\W\d][\w.′°%]*", text):
        return text
    return f"({text})"


def _symbols(items: list) -> int:
    return sum(1 for i in items if i.role == "base" and (i.frac or i.t.isalpha()))


def _doubt(items: list, radicals) -> bool:
    """Whether ``items`` hold a root sign with no bar found for it (what
    stands under the root is then not known)."""
    return any(i.doubt or (i.t == "√" and not any(sign is i for _, sign in radicals))
               for i in items)


def read_slant_fractions(items: list[Ch], spaces, radicals: list) -> list[Ch]:
    """``items`` with each fraction set on a slant read: the characters
    raised before a fraction slash are its numerator, those lowered after
    it its denominator, and the three become one ``frac`` item
    ``numerator/denominator``. A slash between characters on the line
    ("1⁄3" in running text) is left as it is."""
    items = list(items)
    for slash in sorted((it for it in items if it.t == _FRACTION_SLASH),
                        key=lambda c: c.x0):
        size = slash.size
        near = [it for it in items if it is not slash and abs(it.y - slash.y) <= 0.95 * size]
        num, edge = [], slash.x0 + 1.5
        for it in sorted((i for i in near if i.x1 <= slash.x0 + 1.5), key=lambda c: -c.x1):
            if edge - it.x1 > 0.6 * size or slash.y - it.y < 1.5:
                break
            num.append(it)
            edge = it.x0
        # the line's own baseline: the character before the numerator
        before = [i for i in near if i.x1 <= edge + 0.5 and edge - i.x1 <= 0.6 * size
                  and i not in num]
        main = max(before, key=lambda c: c.x1).y if before else slash.y + 0.5
        den, edge = [], slash.x1 - 1.5
        for it in sorted((i for i in near if i.x0 >= slash.x1 - 1.5), key=lambda c: c.x0):
            if it.x0 - edge > 0.6 * size or it.y - main < 0.9:
                break
            den.append(it)
            edge = it.x1
        if not num or not den:
            continue
        top, bottom = (_rows_text(num, spaces, radicals),
                       _rows_text(den, spaces, radicals))
        text = _wrap(top, _symbols(num)) + "/" + _wrap(bottom, _symbols(den))
        used = {id(it) for it in num + den + [slash]}
        items = [it for it in items if id(it) not in used]
        both = num + den
        items.append(Ch(text, min(i.x0 for i in both), max(i.x1 for i in both), main,
                        min(i.top for i in both), max(i.bot for i in both), size,
                        True, frac=True, doubt=_doubt(both, radicals)))
    return items


def read_fractions(items: list[Ch], bars: list[Bar], spaces, radicals: list,
                   unread: list) -> list[Ch]:
    """``items`` with each built-up fraction read from its bar: the
    characters over and under a bar become one ``frac`` item
    ``(numerator)/(denominator)`` set where the bar is. A bar with a root
    sign at its left end is the root's bar and is noted in ``radicals``.
    A bar with mathematics on one side only goes to ``unread``."""
    # a root's bar: the topmost bar that starts where a root sign ends (a
    # tall root over a fraction has the fraction's bar there too, lower)
    roots = {}
    for sign in (it for it in items if it.t == "√"):
        cand = [b for b in bars if b.x0 - 2.5 <= sign.x1 <= b.x0 + 3.0
                and sign.y - 2.8 * sign.size <= b.y <= sign.bot - 2]
        if cand:
            top = min(cand, key=lambda b: b.y)
            roots[id(top)] = sign
            radicals.append((top, sign))
    items = read_slant_fractions(items, spaces, radicals)
    for bar in sorted(bars, key=lambda b: b.x1 - b.x0):
        if id(bar) in roots:
            continue
        near = [it for it in items if it.math
                and bar.x0 - 0.8 <= it.xc <= bar.x1 + 0.8
                and abs(it.y - bar.y) <= 1.6 * max(it.size, 10.0)]
        if not near:
            continue
        size = max(it.size for it in near)
        num = [it for it in near if bar.y - 1.35 * size <= it.y <= bar.y - 0.08 * size]
        den = [it for it in near if bar.y + 0.35 * size <= it.y <= bar.y + 1.45 * size]
        if not num or not den:
            if num or den:
                unread.append(bar)
            continue
        top, bottom = (_rows_text(num, spaces, radicals),
                       _rows_text(den, spaces, radicals))
        text = _wrap(top, _symbols(num)) + "/" + _wrap(bottom, _symbols(den))
        used = {id(it) for it in num + den}
        items = [it for it in items if id(it) not in used]
        both = num + den
        items.append(Ch(text, min(bar.x0, min(i.x0 for i in both)),
                        max(bar.x1, max(i.x1 for i in both)),
                        bar.y + 0.28 * size, min(i.top for i in both),
                        max(i.bot for i in both), size, True, frac=True,
                        doubt=_doubt(both, radicals)))
    return items


def _rows_text(items: list[Ch], spaces, radicals) -> str:
    """A numerator or denominator as text (its lines joined, should it hold
    more than one)."""
    return " ".join(r.text for r in cluster_rows(items, spaces, radicals))


#: The index of a root (the 4 of a fourth root), written raised before the sign.
_RAISED = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶",
           "7": "⁷", "8": "⁸", "9": "⁹", "n": "ⁿ", "y": "ʸ", "i": "ⁱ"}
#: A character under this size is a raised or lowered one where a line of
#: full-size characters runs beside it.
_SCRIPT_SIZE = 9.0
#: Full-size characters whose baselines are this close are one line (a tall
#: bracket is set about 2 pt off the baseline of the line it stands in;
#: lines of text are 11 pt apart or more).
_SAME_LINE = 2.5


def cluster_rows(items: list[Ch], spaces, radicals=()) -> list[Row]:
    """``items`` as printed lines, top to bottom. Full-size characters on
    one baseline are a line; a small character takes the line it is raised
    from or lowered to."""
    base = sorted((it for it in items if it.size >= _SCRIPT_SIZE or it.frac),
                  key=lambda c: (c.y, c.x0))
    small = [it for it in items if not (it.size >= _SCRIPT_SIZE or it.frac)]
    rows: list[Row] = []
    for it in base:
        it.role = "base"
        for r in reversed(rows[-4:]):
            if abs(r.y - it.y) <= _SAME_LINE:
                r.items.append(it)
                break
        else:
            rows.append(Row([it], it.y, it.size))
    for r in rows:
        r.size = max(i.size for i in r.items)
        # the baseline most of the line stands on (a tall bracket's is lower)
        ys = sorted(round(i.y, 1) for i in r.items)
        r.y = max(set(ys), key=ys.count)
    # a tall bracket or a lone sign set a little off the baseline belongs to
    # the line it stands in
    lone = [r for r in rows if all(i.t in _DELIMS + "√∑∫" for i in r.items)]
    for r in lone:
        host = min((h for h in rows if h is not r and h not in lone
                    and abs(h.y - r.y) <= 0.75 * h.size
                    and h.x0 - 12 <= r.x0 <= h.x1 + 12),
                   key=lambda h: abs(h.y - r.y), default=None)
        if host is not None:
            host.items.extend(r.items)
            rows.remove(r)
    # the limits of a sum, set under and over its sign: ∑(i=1 to n)
    for r in rows:
        for sign in [i for i in r.items if i.t == "∑"]:
            lims = [c for c in small if sign.x0 - 4 <= c.xc <= sign.x1 + 4
                    and not any(abs(b.y - c.y) <= 6 and abs(b.xc - c.xc) <= 25
                                for b in base if b is not sign)]
            lower = sorted((c for c in lims if 0.6 * r.size < c.y - r.y <= 2.0 * r.size),
                           key=lambda c: c.x0)
            upper = sorted((c for c in lims if -2.2 * r.size <= c.y - r.y < -r.size),
                           key=lambda c: c.x0)
            if not lower:
                continue
            sign.t = "∑(" + "".join(c.t for c in lower) + (
                " to " + "".join(c.t for c in upper) if upper else "") + ")"
            gone = {id(c) for c in lower + upper}
            small = [c for c in small if id(c) not in gone]
    loose = []
    for it in small:
        best = None
        for r in rows:
            dy = it.y - r.y
            if -0.95 * r.size <= dy <= 0.45 * r.size \
                    and r.x0 - 16 <= it.xc <= r.x1 + 0.9 * r.size:
                if best is None or abs(dy) < abs(it.y - best.y):
                    best = r
        if best is None:
            loose.append(it)
            continue
        dy = it.y - best.y
        it.role = ("sup" if dy < -0.15 * best.size
                   else "sub" if dy > 0.06 * best.size else "base")
        best.items.append(it)
    # a power on a tall bracket (one round a built-up fraction) is set at the
    # bracket's top, higher than a power on a letter; a subscript at its
    # foot, lower than one on a letter
    for it in sorted(loose, key=lambda c: c.x0):
        for r in rows:
            fracs = [f for f in r.items if f.frac]
            if not fracs or not (min(f.top for f in fracs) - 3 <= it.y
                                 <= max(f.bot for f in fracs) + 3):
                continue
            role = "sup" if it.y < r.y else "sub"
            after = [d for d in r.items
                     if -1.0 <= it.x0 - d.x1 <= 0.6 * r.size
                     and ((d.t in ")]}" and d.role == "base"
                           and any(f.x1 <= d.x0 + 1.5 for f in fracs))
                          or (d.role == role and abs(d.y - it.y) <= 1.0))]
            if after:
                it.role = role
                r.items.append(it)
                loose.remove(it)
                break
    small_rows: list[Row] = []
    for it in sorted(loose, key=lambda c: (c.y, c.x0)):
        it.role = "base"
        for r in reversed(small_rows[-4:]):
            if abs(r.y - it.y) <= 1.0:
                r.items.append(it)
                break
        else:
            small_rows.append(Row([it], it.y, it.size))
    rows += small_rows
    rows.sort(key=lambda r: r.y)
    for r in rows:
        r.spaces, r.radicals = spaces, tuple(radicals)
        r.text = linear(r, spaces, radicals)
    # lines closer than lines of text are set, one over the other
    for a, b in zip(rows, rows[1:]):
        if b.y - a.y < 0.92 * max(a.size, b.size) \
                and min(a.x1, b.x1) - max(a.x0, b.x0) > 2:
            a.crowded = b.crowded = True
    return rows


def _space_between(a: Ch, b: Ch, row_y: float, spaces) -> bool:
    """Whether a space is printed between two neighbouring characters: a
    gap wider than a fifth of the smaller one's size, or a space character
    of the text layer that starts between them."""
    if b.x0 - a.x1 > 0.2 * min(a.size, b.size):
        return True
    lo, hi = a.xc, b.x0 + 0.6
    return any(lo <= sx <= hi and abs(sy - row_y) <= 6 for sx, sy in spaces)


def linear(row: Row, spaces, radicals=()) -> str:
    """The characters of one printed line in reading order as plain text."""
    order = {"sup": 0, "base": 1, "sub": 2}
    items = sorted(row.items, key=lambda c: (round(c.x0, 1), order[c.role]))
    # the characters under a root's bar
    under = {}
    for bar, sign in radicals:
        if not any(it is sign for it in items):
            continue
        inside = [it for it in items if bar.x0 - 0.8 <= it.xc <= bar.x1 + 0.8
                  and it is not sign]
        if inside:
            under[id(inside[0])] = "open"
            under[id(inside[-1])] = under.get(id(inside[-1]), "") + "close"
    runs: list[list] = []   # [role, [items]]
    for it in items:
        if runs and runs[-1][0] == it.role:
            runs[-1][1].append(it)
        else:
            runs.append([it.role, [it]])
    # a raised group set over a subscript: a prime belongs to the symbol,
    # before the subscript (σ′z0 for σ with z0 under a prime); a power comes
    # after the whole subscript (N60^m for N with 60 under m)
    k = 1
    while k < len(runs):
        role, its = runs[k]
        before = runs[k - 1]
        if role == "sup" and before[0] == "sub" and its[0].x0 < before[1][-1].x1 + 0.5:
            split = k + 1 < len(runs) and runs[k + 1][0] == "sub"
            if all(i.t in _PRIMES for i in its):
                runs[k - 1], runs[k] = runs[k], runs[k - 1]
                if split:
                    runs[k][1].extend(runs[k + 1][1])
                    del runs[k + 1]
                k = max(1, k - 1)
                continue
            if split:
                before[1].extend(runs[k + 1][1])
                del runs[k + 1]
                continue
        k += 1
    # the limits of a sum set beside its sign: ∑(1 to i)
    k = 0
    while k < len(runs):
        role, its = runs[k]
        after = [r for r in runs[k + 1:k + 3] if r[0] in ("sup", "sub")]
        if role == "base" and its[-1].t == "∑" and after and runs[k + 1][0] != "base":
            if len(after) == 2 and after[0][0] == after[1][0]:
                after = after[:1]
            lims = {r[0]: "".join(i.t for i in r[1]) for r in after}
            if "sub" in lims:
                its[-1].t = "∑(" + lims["sub"] + (
                    " to " + lims["sup"] if "sup" in lims else "") + ")"
                gone = {id(i) for r in after for i in r[1]}
                row.items = [i for i in row.items if id(i) not in gone]
                del runs[k + 1:k + 1 + len(after)]
        k += 1
    out = ""
    prev = None
    for k, (role, its) in enumerate(runs):
        text = ""
        last = None
        for it in its:
            if last is not None and (
                    _space_between(last, it, row.y, spaces) if role == "base"
                    else it.x0 - last.x1 > 0.45 * min(last.size, it.size)):
                text += " "
            mark = under.get(id(it), "")
            if "open" in mark:
                text += "\x02"
            if it.frac:
                # a fraction set against a symbol (one before it or after
                # it, with no sign between): a space, and brackets round it
                k2 = its.index(it)
                after = its[k2 + 1] if k2 + 1 < len(its) else None
                prior = (out + text).replace("\x02", "").replace("\x03", "")[-1:]
                tight = prior.isalnum() or prior in ("′", ")", "]")
                if tight:
                    text += " "
                if tight or (after is not None and (after.t[:1].isalnum()
                                                    or after.t[:1] == "(" or after.frac)):
                    text += f"({it.t})"
                else:
                    text += it.t
            else:
                text += it.t
            if "close" in mark:
                text += "\x03"
            last = it
        gap = prev is not None and _space_between(prev, its[0], row.y, spaces)
        nxt = runs[k + 1][1][0] if k + 1 < len(runs) else None
        if role == "sup":
            body = text.replace("\x02", "").replace("\x03", "")
            is_math = all(i.math for i in its)
            if all(c in _PRIMES for c in body):
                piece = body
            elif nxt is not None and nxt.t == "√" and all(c in _RAISED for c in body):
                piece = " " + "".join(_RAISED[c] for c in body)   # a root's index
            elif body in ("o", "∘", "°") and out[-1:].isdigit():
                piece = "°"
            elif not is_math and not _NEGATIVE.fullmatch(body) \
                    and not (body.isdigit() and (_UNIT_END.search(out)
                                                 or out.endswith("10"))):
                piece = f"[{body}]"                     # a note mark
            elif re.fullmatch(r"[\w.]+", body):
                piece = "^" + body
            else:
                piece = f"^({body})"
            # where a root's bar starts or ends over the raised group
            piece = ("\x02" if "\x02" in text else "") + piece \
                + ("\x03" if "\x03" in text else "")
            # a symbol set straight after a raised group starts a new factor
            if "^" in piece and nxt is not None and nxt.role == "base" \
                    and nxt.t[:1].isalnum():
                piece += " "
            out += piece
        elif role == "sub":
            body = text.replace("\x02", "").replace("\x03", "")
            out += ("\x02" if "\x02" in text else "") + body \
                + ("\x03" if "\x03" in text else "")
            if nxt is not None and nxt.role == "base" and nxt.t[:1].isalnum() \
                    and body[-1:].isalnum() \
                    and not _space_between(its[-1], nxt, row.y, spaces):
                out += " "
        else:
            out += (" " if gap else "") + text
        prev = its[-1]
    out = re.sub(rf"\s*{_FRACTION_SLASH}\s*", "/", out)
    # a root: √N, or √(...) round more than one symbol
    out = re.sub(r"√\s*\x02([^\x02\x03]*)\x03",
                 lambda m: "√" + _wrap(m.group(1).strip()), out)
    out = out.replace("\x02", "").replace("\x03", "")
    out = re.sub(r"\(\s+", "(", out)
    out = re.sub(r"\s+\)", ")", out)
    out = re.sub(r"\s+([,;])", r"\1", out)
    return re.sub(r"\s+", " ", out).strip()


def rows_of(chars: list[Ch], bars: list[Bar], spaces, unread: list) -> list[Row]:
    """The printed lines of a set of characters, fractions and roots read."""
    radicals: list = []
    items = read_fractions(chars, bars, spaces, radicals, unread)
    rows = cluster_rows(items, spaces, radicals)
    for r in rows:
        if _doubt(r.items, radicals):
            r.crowded = True      # a root with no bar found for it
    return rows


# ---------------------------------------------------------------------------
# numbered equations
# ---------------------------------------------------------------------------

#: A figure, table, paragraph or equation number as printed ("5–21", "B–3a").
NUM = r"(?:\d{1,2}|[A-Z])[–-]\d{1,3}[a-z]?"
_EQ_NUMBER = re.compile(rf"\(({NUM})\)")


def hyphen(number: str) -> str:
    """A printed number with a hyphen for its en dash ('5–21' -> '5-21')."""
    return number.replace("–", "-")


def take_equation_numbers(chars: list[Ch]) -> tuple[list[Ch], list[dict]]:
    """An equation's number is printed in the text font, alone at the right
    of its equation: ``(5–21)`` with 15 pt or more of space before it and
    nothing after it on its line. Returns the other characters and each
    number found as ``{"num", "y", "top", "bot", "x0"}``."""
    cand = sorted((c for c in chars if not c.math and not c.bold and c.size >= _SCRIPT_SIZE),
                  key=lambda c: (round(c.y), c.x0))
    lines: list[list[Ch]] = []
    for c in cand:
        if lines and abs(lines[-1][0].y - c.y) <= 1.0:
            lines[-1].append(c)
        else:
            lines.append([c])
    found, used = [], set()
    for line in lines:
        line.sort(key=lambda c: c.x0)
        text = "".join(c.t for c in line)
        k = text.rfind("(")
        if k < 0:
            continue
        m = _EQ_NUMBER.fullmatch(text[k:])
        if not m:
            continue
        tail = line[k:]
        if any(b.x0 - a.x1 > 3 for a, b in zip(tail, tail[1:])):
            continue
        first, last = tail[0], tail[-1]
        beside = [c for c in chars if abs(c.y - first.y) <= 4 and c not in tail]
        if any(c.x0 > last.x1 for c in beside):
            continue
        if any(first.x0 - 15 < c.x1 <= first.x0 + 0.5 for c in beside):
            continue
        found.append({"num": hyphen(m.group(1)), "y": first.y,
                      "top": min(c.top for c in tail), "bot": max(c.bot for c in tail),
                      "x0": first.x0, "x1": last.x1})
        used.update(id(c) for c in tail)
    return [c for c in chars if id(c) not in used], found


def _opens_with_math(row: Row) -> bool:
    first = min(row.items, key=lambda c: c.x0)
    return first.math and row.x0 > MARGIN + 20


@dataclass
class Line:
    """One line of a page as the build uses it: a printed line of text, or
    a numbered equation in place of the lines that print it."""
    text: str
    y: float
    x0: float
    x1: float
    size: float
    row: Row | None = None
    eq: str | None = None
    crowded: bool = False
    auto: list = field(default_factory=list)   # an equation's lines as read
    figures: list = field(default_factory=list)  # (number, caption) captioned in a cell
    mathy: bool = False              # mostly mathematics (a formula on its own line)


def _formula_row(r: Row) -> bool:
    """Whether a row is a displayed formula's, or a piece of one: mostly
    mathematics, or opening with it in from the margin."""
    return r.math_share >= 0.6 or (r.math_share >= 0.3 and _opens_with_math(r))


#: A piece of a numbered equation lies no further than this from its number.
_EQUATION_REACH = 90.0


def lines_of(chars: list[Ch], bars: list[Bar], spaces, book) -> list[Line]:
    """A region's characters as lines, top to bottom, each numbered equation
    as one line: its formula as typed in from the page (``book.formula``)
    followed by ``[Eq. 5-21]``.

    A numbered equation is every piece of mathematics printed between the
    line of text above its number and the line of text below it. Where
    several numbers stand with no text between them, the pieces are shared
    out at the widest gap between one number's line and the first piece that
    reaches the level of the next number."""
    chars, numbers = take_equation_numbers(chars)
    rows = rows_of(chars, bars, spaces, book.unread_bars)
    numbers.sort(key=lambda n: n["y"])
    taken: dict[int, dict] = {}
    # words set under the number, against the right margin (the equation's
    # source, the soil it is for), are part of its line
    for n in numbers:
        n["rows"] = []
        edge = n["bot"]
        for r in sorted(rows, key=lambda r: r.y):
            if id(r) not in taken and r.x0 > 250 and abs(r.x1 - n["x1"]) <= 10 \
                    and -2 <= r.top - edge <= 9:
                n["rows"].append(r)
                taken[id(r)] = n
                edge = r.bot
    free = [r for r in rows if id(r) not in taken]
    pieces = sorted((r for r in free if _formula_row(r)), key=lambda r: r.y)
    words = [r.y for r in free if not _formula_row(r)]
    for n in numbers:
        n["band"] = (max((y for y in words if y < n["y"] - 4), default=-1e9),
                     min((y for y in words if y > n["y"] + 4), default=1e9))
    k = 0
    while k < len(numbers):
        group = [numbers[k]]
        while k + len(group) < len(numbers) \
                and numbers[k + len(group)]["band"] == group[0]["band"]:
            group.append(numbers[k + len(group)])
        k += len(group)
        top, bot = group[0]["band"]
        cand = [r for r in pieces if top < r.y < bot
                and min(abs(r.y - n["y"]) for n in group) <= _EQUATION_REACH]
        cuts = [-1e9]
        for one, two in zip(group, group[1:]):
            between = [r for r in cand if r.y >= one["y"] - 3]
            reach = next((j for j, r in enumerate(between) if r.bot >= two["top"] - 2),
                         len(between) - 1)
            between = between[:reach + 1]
            gaps = [(q.top - r.bot, (q.top + r.bot) / 2)
                    for r, q in zip(between, between[1:])]
            cuts.append(max(gaps)[1] if gaps else (one["y"] + two["y"]) / 2)
        cuts.append(1e9)
        for r in cand:
            n = next(g for g, lo, hi in zip(group, cuts, cuts[1:]) if lo <= r.y < hi)
            n["rows"].append(r)
            taken[id(r)] = n
    for n in numbers:
        if not any(_formula_row(r) for r in n["rows"]):
            # its line reads as text (words in the text font beside a symbol)
            near = [r for r in free if id(r) not in taken
                    and min(r.bot, n["bot"]) - max(r.top, n["top"]) >= 2.5
                    and r.x0 > MARGIN + 4 and r.math_share >= 0.15]
            for r in near[:1]:
                n["rows"].append(r)
                taken[id(r)] = n
    out: list[Line] = []
    done = set()
    for r in rows:
        n = taken.get(id(r))
        if n is None:
            out.append(Line(r.text, r.y, r.x0, r.x1, r.type_size, row=r,
                            crowded=r.crowded, mathy=r.math_share >= 0.5))
            continue
        if id(n) in done:
            continue
        done.add(id(n))
        out.append(_equation_line(n, book))
    for n in numbers:
        if id(n) not in done:
            book.note(f"Eq. {n['num']}: no printed symbols found beside its number")
            out.append(_equation_line(n, book))
    out.sort(key=lambda ln: ln.y)
    return out


def _equation_line(n: dict, book) -> Line:
    auto = [r.text for r in sorted(n["rows"], key=lambda r: (not _formula_row(r), r.y))]
    typed = book.formula(n["num"], auto)
    rows = n["rows"]
    y = min([r.y for r in rows] + [n["y"]])
    x0 = min([r.x0 for r in rows] + [n["x0"]])
    return Line(f"{typed} [Eq. {n['num']}]", y, x0, n["x0"] + 30,
                max([r.size for r in rows] + [10.0]), eq=n["num"], auto=auto, mathy=True)


# ---------------------------------------------------------------------------
# ruled tables
# ---------------------------------------------------------------------------

#: Text in a cell starts this far inside the cell's border.
CELL_PAD = 5.4
#: A merged cell longer than this is not repeated on each row it spans.
REPEAT_CHARS = 120
#: A row's last cell with more text than this keeps its line breaks.
LINES_KEPT_CHARS = 150
_DITTO = "″"


def _levels(values, tol: float) -> list[float]:
    """Sorted values, those within ``tol`` of the one before as one."""
    groups: list[list[float]] = []
    for v in sorted(values):
        if groups and v - groups[-1][-1] <= tol:
            groups[-1].append(v)
        else:
            groups.append([v])
    return [sum(g) / len(g) for g in groups]


def _first_word_width(line: Line) -> float:
    """How wide a line's first word is (what the line before it had no
    room for, if the two are one paragraph)."""
    if line.row is None:
        return 1e9
    items = sorted((i for i in line.row.items if i.role == "base"), key=lambda c: c.x0)
    if not items:
        return 1e9
    end = items[0].x1
    for a, b in zip(items, items[1:]):
        if _space_between(a, b, line.row.y, line.row.spaces):
            break
        end = b.x1
    return end - items[0].x0


def _join(a: str, b: str) -> str:
    """Two lines of one paragraph as running text; a word broken at its
    hyphen stays one word ("punch-" "through")."""
    if not a or not b:
        return a + b
    if a.endswith("-") and b[:1].islower() and not a.endswith(" -"):
        return a + b
    if a.endswith("–") and b[:1].isdigit() and a[-2:-1].isalnum():
        return a + b                 # a number broken at its dash ("5–" "29")
    return a + " " + b


def paragraphs(lines: list[Line], left: float, right: float,
               starts=None) -> list[Line]:
    """Lines of one cell or one notes block as paragraphs: a line the next
    word would not have fitted on runs on into the next line; a line with
    room left ended its paragraph. A numbered equation stands alone, and a
    line that matches ``starts`` (a note's mark) opens a paragraph."""
    out: list[Line] = []
    for k, ln in enumerate(lines):
        if not out or ln.eq or out[-1].eq or (starts and starts.match(ln.text)):
            out.append(Line(ln.text, ln.y, ln.x0, ln.x1, ln.size, ln.row, ln.eq,
                            ln.crowded, list(ln.auto), mathy=ln.mathy))
            continue
        prev = lines[k - 1]
        if ln.row is not None and prev.row is not None and ln.row.bold != prev.row.bold:
            # a caption or a heading set in bold inside a cell stands apart
            out.append(Line(ln.text, ln.y, ln.x0, ln.x1, ln.size, ln.row, ln.eq,
                            ln.crowded, list(ln.auto), mathy=ln.mathy))
            continue
        centred = (prev.x0 - left > 4
                   and abs((prev.x0 - left) - (right - prev.x1)) < 4)
        slack = ((right - left) - (prev.x1 - prev.x0)) if centred else right - prev.x1
        if slack < _first_word_width(ln) + 0.25 * ln.size + 1:
            out[-1].text = _join(out[-1].text, ln.text)
            out[-1].crowded = out[-1].crowded or ln.crowded
        else:
            out.append(Line(ln.text, ln.y, ln.x0, ln.x1, ln.size, ln.row, ln.eq,
                            ln.crowded, list(ln.auto), mathy=ln.mathy))
    return out


@dataclass
class Cell:
    i0: int
    i1: int
    j0: int
    j1: int
    x0: float
    x1: float
    y0: float
    y1: float
    chars: list = field(default_factory=list)
    paras: list = field(default_factory=list)

    def text(self, last: bool) -> str:
        """The cell's text on one line; in a row's last cell, where it is
        a long one (the steps of a procedure, a worked solution), its lines
        that end short stay lines."""
        long = last and sum(len(p.text) for p in self.paras) > LINES_KEPT_CHARS
        out = ""
        for k, p in enumerate(self.paras):
            if k:
                # a formula on its own line stays apart from what is beside it
                beside = p.mathy or self.paras[k - 1].mathy
                if long or (beside and last):
                    out += "\n"
                elif beside and not out.endswith((".", ";", ":", ",")):
                    out += "; "
                else:
                    out += " "
            out += p.text
        return out


class Grid:
    """A ruled table, or the part of one on a page: its cells from its rules.
    ``hsegs`` are its cell borders ``(y, x0, x1)``, ``vsegs`` the vertical
    ones ``(x, y0, y1)``. Boxes of the grid with no rule between them are
    one (merged) cell."""

    def __init__(self, hsegs, vsegs):
        self.hsegs, self.vsegs = hsegs, vsegs
        self.ys = _levels([y for y, _, _ in hsegs], 1.2)
        self.y0, self.y1 = self.ys[0], self.ys[-1]
        vsegs = [v for v in vsegs if v[2] > self.y0 - 1 and v[1] < self.y1 + 1]
        self.xs = _levels([x for _, a, b in hsegs for x in (a, b)]
                          + [x for x, _, _ in vsegs], 2.5)
        ys, xs = self.ys, self.xs
        n, m = len(ys) - 1, len(xs) - 1
        parent = {(i, j): (i, j) for i in range(n) for j in range(m)}

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        def hcov(i, j):
            return any(abs(y - ys[i]) <= 1.2 and a <= xs[j] + 2.6 and b >= xs[j + 1] - 2.6
                       for y, a, b in hsegs)

        def vcov(i, j):
            return any(abs(x - xs[j]) <= 2.6 and a <= ys[i] + 2.6 and b >= ys[i + 1] - 2.6
                       for x, a, b in vsegs)

        for i in range(n):
            for j in range(m):
                if i + 1 < n and not hcov(i + 1, j):
                    parent[find((i + 1, j))] = find((i, j))
                if j + 1 < m and not vcov(i, j + 1):
                    parent[find((i, j + 1))] = find((i, j))
        groups: dict = {}
        for box in parent:
            groups.setdefault(find(box), []).append(box)
        self.cells: list[Cell] = []
        self.box: dict = {}
        for boxes in groups.values():
            i0, i1 = min(b[0] for b in boxes), max(b[0] for b in boxes)
            j0, j1 = min(b[1] for b in boxes), max(b[1] for b in boxes)
            cell = Cell(i0, i1, j0, j1, xs[j0], xs[j1 + 1], ys[i0], ys[i1 + 1])
            self.cells.append(cell)
            for b in boxes:
                self.box[b] = cell

    def holds(self, c: Ch) -> bool:
        ym = c.y - 0.3 * c.size
        return self.y0 - 0.5 <= ym <= self.y1 + 0.5 and self.xs[0] - 3 <= c.xc <= self.xs[-1] + 3

    def add(self, c: Ch) -> None:
        ym = c.y - 0.3 * c.size
        i = max(0, min(len(self.ys) - 2, sum(1 for y in self.ys[1:] if y <= ym)))
        j = max(0, min(len(self.xs) - 2, sum(1 for x in self.xs[1:] if x <= c.xc)))
        self.box[(i, j)].chars.append(c)

    def read(self, bars, spaces, book) -> None:
        for cell in self.cells:
            own = [b for b in bars if cell.x0 - 1 <= (b.x0 + b.x1) / 2 <= cell.x1 + 1
                   and cell.y0 - 1 <= b.y <= cell.y1 + 1]
            lines = lines_of(cell.chars, own, spaces, book)
            cell.paras = paragraphs(lines, cell.x0 + CELL_PAD, cell.x1 - CELL_PAD)

    def lines(self) -> list[Line]:
        """The table's printed rows, one line each, cells left to right with
        ``" | "`` between them; a merged cell is repeated on each row it
        spans (a long one as a ditto mark)."""
        out: list[Line] = []
        m = len(self.xs) - 1
        # a merged cell whose text stands on rows apart, with rows between
        # that hold none of it (a procedure's step round a table set inside
        # it: a line over the inner table, a total under it), sets each
        # paragraph on the row it stands on; a merged cell's text on rows
        # next to each other is one text (a source wrapped over two rows)
        spread: dict = {}
        for c in self.cells:
            if c.i1 > c.i0 and c.paras:
                rows: dict = {}
                for p in c.paras:
                    ym = p.y - 0.3 * p.size
                    i = max(c.i0, min(c.i1, sum(1 for y in self.ys[1:] if y <= ym)))
                    rows.setdefault(i, []).append(p)
                if max(rows) - min(rows) + 1 > len(rows):
                    spread[id(c)] = rows

        def own_at(c, i):
            if id(c) in spread:
                return spread[id(c)].get(i, [])
            return c.paras if c.i0 == i else []

        for i in range(len(self.ys) - 1):
            cells = []
            for j in range(m):
                c = self.box[(i, j)]
                if c not in cells and not (not c.paras and c.x1 - c.x0 < 6):
                    cells.append(c)
            if not any(own_at(c, i) for c in cells):
                continue
            while cells and not cells[-1].paras:
                cells.pop()
            parts = []
            for k, c in enumerate(cells):
                last = k == len(cells) - 1
                if id(c) in spread:
                    mine = spread[id(c)].get(i)
                    parts.append(replace(c, paras=mine).text(last) if mine else
                                 _DITTO if i > min(spread[id(c)]) else "")
                elif c.i0 == i:
                    parts.append(c.text(last))
                else:
                    t = c.text(False)
                    parts.append(t if len(t) <= REPEAT_CHARS else _DITTO)
            own = [p for c in cells for p in own_at(c, i)]
            figs = []
            for q in own:
                cap = re.match(rf"^Figure ({NUM})\.\s*(.*)$", q.text)
                bold = q.row is not None and q.row.bold
                if cap and bold:
                    figs.append([hyphen(cap.group(1)), cap.group(2)])
                elif figs and bold and own[own.index(q) - 1].row is not None \
                        and own[own.index(q) - 1].row.bold:
                    figs[-1][1] = _join(figs[-1][1], q.text)   # the caption runs on
            out.append(Line(" | ".join(parts), self.ys[i], self.xs[0], self.xs[-1], 10.0,
                            crowded=any(p.crowded for p in own),
                            eq=",".join(p.eq for p in own if p.eq) or None,
                            auto=[t for p in own for t in ([p.text] if p.crowded else [])],
                            figures=figs))
        return out


def find_grids(thin, vert, heavy=()) -> tuple[list[Grid], list[Bar]]:
    """The ruled tables of a page from its thin rules, and the thin rules
    that are not cell borders (a border's ends meet other borders' ends; a
    short rule on its own is a fraction bar of small type). A rule of
    ``heavy`` whose ends meet thin borders' ends is a border too (the rule
    under a table's column headings; the rules that frame a figure inside a
    cell meet none)."""
    ends = [(y, x) for y, a, b in thin for x in (a, b)]

    def shared(y, x):
        return any(abs(x - x2) <= 2.6 and abs(y - y2) > 1.2 for y2, x2 in ends)

    borders = [s for s in thin if shared(s[0], s[1]) and shared(s[0], s[2])]
    loose = [Bar(*s) for s in thin if s not in borders]
    borders += [s for s in heavy if shared(s[0], s[1]) and shared(s[0], s[2])]
    if len(_levels([y for y, _, _ in borders], 1.2)) < 2:
        return [], loose
    return [Grid(borders, vert)], loose


def split_grids(grids: list[Grid], cuts: list[float]) -> list[Grid]:
    """A grid cut where a rule over a table's caption crosses it (two
    tables on one page are separate grids)."""
    out = []
    for g in grids:
        inside = sorted(c for c in cuts if g.y0 + 2 < c < g.y1 - 2)
        if not inside:
            out.append(g)
            continue
        edges = [g.y0 - 1.3] + inside + [g.y1 + 1.3]
        for lo, hi in zip(edges, edges[1:]):
            segs = [s for s in g.hsegs if lo <= s[0] <= hi]
            if len(_levels([y for y, _, _ in segs], 1.2)) >= 2:
                out.append(Grid(segs, g.vsegs))
    return out


# ---------------------------------------------------------------------------
# a page
# ---------------------------------------------------------------------------

#: The footer ("EM 1110-1-1905 • 31 July 2025" and the page number) is
#: within this of the foot of the page (a few pages are set landscape).
FOOTER = 57.0
#: Running text and paragraph headings start at the left margin, and the
#: right margin is as far from the page's right edge; a subparagraph's first
#: line is indented.
MARGIN, INDENT = 72.0, 90.0


@dataclass
class PageData:
    index: int                 # 0-based PDF page
    label: str                 # the printed page number
    flow: list                 # Line and Grid objects, top to bottom
    right: float = 540.0       # the right margin
    lettering: int = 0         # characters left out as lettering in a picture
    pictures: list = field(default_factory=list)


def _figure_bands(chars: list[Ch], spaces, frame: list, pictures: list) -> list:
    """The heights ``(y0, y1)`` of a page that hold a figure's own lettering:
    in the space between two frame rules that holds pictures and, below
    them, a bold caption ``Figure 4–7. ...``, the text set from the top of
    the pictures to just above the caption. Text a picture's box does not
    cover (a chart drawn in lines with its labels as text, the letters of a
    figure's parts set between its pictures) is the figure's, not the
    manual's running text."""
    out = []
    ys = sorted(h[0] for h in frame)
    for a, b in zip(ys, ys[1:]):
        pics = [r for r in pictures if a < (r.y0 + r.y1) / 2 < b]
        inside = [c for c in chars if a < (c.top + c.bot) / 2 < b]
        if not pics or not inside:
            continue
        rows = sorted(cluster_rows(inside, spaces), key=lambda r: r.y)
        if any(r.bold and r.text.startswith("Table ") for r in rows):
            continue
        cap = next((r for r in rows if r.bold and re.match(r"^Figure \d", r.text)), None)
        if cap is None:
            continue
        y0 = max(a, min(r.y0 for r in pics) - 6)
        y1 = min(cap.top - 1, max(r.y1 for r in pics) + 6)
        if y1 > y0:
            out.append((y0, y1))
    return out


def read_page(page, index: int, book) -> PageData:
    chars, spaces = page_chars(page)
    thin, heavy, bars, vert = page_rules(page)
    foot_y = page.rect.height - FOOTER
    foot = [c for c in chars if c.y > foot_y]
    chars = [c for c in chars if c.y <= foot_y]
    foot_text = " ".join(r.text for r in cluster_rows(foot, spaces))
    label = foot_text.split()[-1] if foot_text.split() else ""
    pictures = [fitz.Rect(i["bbox"]) for i in page.get_image_info()]
    # a heavy rule drawn from just left of the margin to just right of it
    # frames a figure or stands over a table's caption, and separates two
    # tables on a page; one drawn cell by cell is a cell border (the rule
    # under a table's column headings)
    frame = [h for h in heavy if h[1] < MARGIN - 0.6]
    drawn = _figure_bands(chars, spaces, frame, pictures)
    kept, lettering = [], 0
    for c in chars:
        ym = (c.top + c.bot) / 2
        if any(r.x0 - 1 <= c.xc <= r.x1 + 1 and r.y0 - 1 <= ym <= r.y1 + 1
               and r.width > 40 and r.height > 40 for r in pictures) \
                or any(y0 <= ym <= y1 for y0, y1 in drawn):
            lettering += 1
        else:
            kept.append(c)
    book.page = label
    grids, loose = find_grids(thin, vert, [h for h in heavy if h not in frame])
    bars = bars + loose
    grids = split_grids(grids, [h[0] for h in frame])
    free = []
    for c in kept:
        g = next((g for g in grids if g.holds(c)), None)
        if g is None:
            free.append(c)
        else:
            g.add(c)
    free_bars = [b for b in bars if not any(g.y0 - 1 <= b.y <= g.y1 + 1 for g in grids)]
    flow: list = list(lines_of(free, free_bars, spaces, book))
    for g in grids:
        g.read([b for b in bars if g.y0 - 1 <= b.y <= g.y1 + 1], spaces, book)
        flow.append(g)
    flow.sort(key=lambda e: e.y if isinstance(e, Line) else e.y0)
    return PageData(index, label, flow, page.rect.width - MARGIN, lettering, pictures)


# ---------------------------------------------------------------------------
# what a build carries from page to page
# ---------------------------------------------------------------------------

_LOWERED = {v: k for k, v in _RAISED.items()}


def _letters(text: str) -> Counter:
    """The letters and digits of a formula, counted (its signs, brackets and
    spaces left out): what a typed formula must share with the page."""
    return Counter(_LOWERED.get(c, c) for c in text if c.isalnum())


class Book:
    """The typed-in formulas and tables of a volume's manifest entry, and
    what the build finds for a reader to settle (``problems``, which stop a
    build) or to look at (``notes``)."""

    def __init__(self, vol: dict, draft: bool = False):
        self.typed = {e["number"]: e for e in vol.get("printed_equations", [])}
        self.tables = {}
        for t in vol.get("printed_tables", []):
            why = t.get("why", "equations")
            note = (f"[Table {t['number']} is printed as a picture; its rows, read "
                    "off the page:]" if why == "picture" else
                    f"[The cells of Table {t['number']} are equations; its rows as "
                    "typed in from the printed page:]")
            self.tables[t["number"]] = {"note": t.get("note", note), "rows": t["rows"]}
        self.passages = vol.get("printed_passages", [])
        self.accepted = {(str(a["page"]), a["text"]) for a in vol.get("accepted_math", [])}
        self.draft = draft
        self.page = ""
        self.front: dict = {}
        self.notes: list[str] = []
        self.problems: list[str] = []
        self.unread_bars: list = []
        self.drafts: dict[str, list] = {}   # equation number -> its lines as read
        self.used: set[str] = set()
        self.used_tables: set[str] = set()
        self.untyped: list[tuple[str, str]] = []
        self.crowded: list[tuple[str, str, str]] = []   # (page, section, text)
        self.lettering: dict[str, int] = {}
        self.page_index: dict[str, int] = {}

    def note(self, message: str) -> None:
        self.notes.append(f"p. {self.page}: {message}")

    def formula(self, number: str, auto: list[str]) -> str:
        """The formula typed in for a numbered equation; where none is typed
        in (a draft build), its lines as the placement rules read them."""
        self.drafts.setdefault(number, []).append({"page": self.page, "auto": auto})
        entry = self.typed.get(number)
        if entry and entry.get("formula"):
            self.used.add(number)
            if not entry.get("differs_from_text_layer"):
                page, typed = _letters(" ".join(auto)), _letters(entry["formula"])
                if page != typed:
                    self.problems.append(
                        f"Eq. {number} (p. {self.page}): the typed formula and the "
                        "characters the page holds beside the number differ (on the page "
                        f"only: {''.join(sorted((page - typed).elements()))!r}; typed only: "
                        f"{''.join(sorted((typed - page).elements()))!r}; read: "
                        f"{' | '.join(auto)!r})")
            return entry["formula"]
        self.untyped.append((number, self.page))
        return " ".join(auto) or "(equation printed on the page)"

    def finish(self, chapters: dict) -> None:
        """Apply the manifest's typed-in passages to the bodies, and list
        what is left for a reader: equations with no typed formula,
        mathematics the placement rules could not read, typed entries the
        build found no place for."""
        typed_over: dict[str, list] = {}
        for k, f in enumerate(self.passages):
            hit = False
            if not f.get("differs_from_text_layer") \
                    and _letters(f["find"]) != _letters(f["replace"]):
                self.problems.append(f"printed_passages[{k}] ({f['section']}): the typed "
                                     "passage and the text it replaces differ in their "
                                     "letters and digits")
            for data in chapters.values():
                for sec in data["sections"]:
                    sid = sec["section_id"]
                    if (sid == f["section"] or sid.startswith(f["section"] + ".")) \
                            and f["find"] in sec["body"] and not hit:
                        sec["body"] = sec["body"].replace(f["find"], f["replace"], 1)
                        typed_over.setdefault(sid.split(".")[0], []).append(f["replace"])
                        hit = True
            if not hit:
                self.problems.append(f"printed_passages[{k}] ({f['section']}): its "
                                     "'find' text is not in that section's body")
        # each section's text (its split parts together) without the passages
        # typed in over it
        left: dict[str, str] = {}
        for data in chapters.values():
            for sec in data["sections"]:
                base = sec["section_id"].split(".")[0]
                left[base] = left.get(base, "") + "\n" + sec["body"]
        for base, typed in typed_over.items():
            for t in typed:
                left[base] = left[base].replace(t, "\n")
        for number, page in dict.fromkeys(self.untyped):
            self.problems.append(f"Eq. {number} (p. {page}): no formula typed in")
        for number in self.typed:
            if number not in self.used and number not in self.drafts:
                self.problems.append(f"printed_equations {number}: no such equation "
                                     "number found on the built pages")
        for number in self.tables:
            if number not in self.used_tables:
                self.problems.append(f"printed_tables {number}: no such table found")
        for page, sid, text in dict.fromkeys(self.crowded):
            # still a problem while the stacked piece is in its section's text
            # outside the passages typed in over it
            if (page, text) in self.accepted \
                    or number_hyphens(text) not in left.get(sid.split(".")[0], ""):
                continue          # accepted as read, or typed over
            self.problems.append(f"p. {page} ({sid}): mathematics set in stacked "
                                 f"pieces, read as {text!r}; type the passage in "
                                 "(printed_passages) or accept it (accepted_math)")


# ---------------------------------------------------------------------------
# front matter: the contents and the lists of tables and figures
# ---------------------------------------------------------------------------

_FRONT_HEADINGS = ("Contents", "Appendixes", "Table List", "Figure List",
                   "Glossary of Terms", "Summary of Change")


def read_front(doc, first: int, last: int, book) -> dict:
    """The printed contents (PDF pages ``first`` to ``last``, 1-based):
    ``chapters`` {number: (title, page)}, ``appendixes`` {letter: (title,
    page)}, ``paragraphs`` {number: (title, page)}, ``tables`` and
    ``figures`` {number: (caption, page)}; numbers with a hyphen."""
    out = {"chapters": {}, "appendixes": {}, "paragraphs": {}, "tables": {}, "figures": {}}
    acc = ""
    last_page = 0
    for i in range(first - 1, last):
        for e in read_page(doc[i], i, book).flow:
            if not isinstance(e, Line):
                continue
            if e.text in _FRONT_HEADINGS:       # a list's own heading
                acc, last_page = "", 0
                continue
            # an entry ends with its page after a dotted leader; a few are
            # printed with one dot or none before the page
            m = re.match(r"^(.*?)\s*\.{2,}\s*(\d+)$", e.text) \
                or re.match(r"^(.*?)\s+\.?\s*(\d{1,3})$", e.text)
            if not m or int(m.group(2)) < last_page:
                acc = (acc + " " + e.text).strip()
                continue
            entry, page = (acc + " " + m.group(1)).strip(), int(m.group(2))
            acc, last_page = "", page
            for key, pat in (("chapters", r"^Chapter (\d+) (.+)$"),
                             ("appendixes", r"^Appendix ([A-Z]) (.+)$"),
                             ("paragraphs", rf"^({NUM})\. (.+)$"),
                             ("tables", rf"^Table ({NUM}) (.+)$"),
                             ("figures", rf"^Figure ({NUM})\. (.+)$")):
                mm = re.match(pat, entry)
                if mm:
                    out[key][hyphen(mm.group(1))] = (number_hyphens(mm.group(2)), page)
                    break
            else:
                book.note(f"contents entry not read: {entry[:60]!r}")
    return out


def number_hyphens(text: str) -> str:
    """An en dash between the parts of a number as a hyphen ('Table 5–2' ->
    'Table 5-2', 'paragraph 5–5a(2)' -> 'paragraph 5-5a(2)')."""
    return re.sub(r"(?<=[0-9A-Z])–(?=\d)", "-", text)


# ---------------------------------------------------------------------------
# a chapter's pages as blocks
# ---------------------------------------------------------------------------

@dataclass
class Block:
    """A paragraph, a list, a table, a figure caption, or the start of a
    paragraph or subparagraph of the manual, with the page of each piece."""
    kind: str                       # para / list / table / figure / head / sub
    pieces: list = field(default_factory=list)   # (page label, text)
    sep: str = " "
    number: str = ""                # table, figure or section number
    title: str = ""
    untitled: bool = False
    page: str = ""
    crowded: list = field(default_factory=list)  # (page, text) read from crowded lines
    shown: bool = True              # False: a caption already in a table cell's text

    @property
    def text(self) -> str:
        return self.sep.join(t for _, t in self.pieces)


_HEAD = re.compile(rf"^({NUM})\.\s*(.*)$")
_MARKS = (re.compile(r"^([a-z]{1,2})\.(?:\s+|$)"), re.compile(r"^\((\d{1,2})\)\s*"),
          re.compile(r"^\(([a-z]{1,2})\)\s*"), re.compile(r"^(\d{1,2})\.(?:\s+|$)"))
_ITEM = re.compile(r"^[^=]{1,30}\s=\s")
_EXAMPLE = re.compile(r"^Example [A-Z][-–]\d+[a-z]?\s")
_NOTE_START = re.compile(r"^(?:\[[\w,]+\]|Notes?[:.])(?:\s|$)")


def _succ(mark: str) -> str:
    return str(int(mark) + 1) if mark.isdigit() else chr(ord(mark[-1]) + 1)


def _mark_text(level: int, mark: str) -> str:
    return (mark, f"({mark})", f"({mark})", mark)[level - 1]


def _lead_title(lines: list, k: int, skip: int) -> str:
    """The italic run-in heading that opens the line ``lines[k]`` after its
    first ``skip`` characters (the subparagraph's mark), read on into the
    next lines while they stay italic; '' where the text is not italic."""
    got: list[str] = []
    ended = False
    for ln in lines[k:k + 4]:
        if not isinstance(ln, Line) or ln.row is None:
            break
        items = sorted((i for i in ln.row.items), key=lambda c: (round(c.x0, 1)))
        if ln is lines[k]:
            n = 0
            rest = []
            for it in items:
                if n < skip and it.role == "base":
                    n += len(it.t)
                    continue
                rest.append(it)
            items = rest
        lead = []
        for it in items:
            if it.italic or (it.math and lead) or (it.role != "base" and lead):
                lead.append(it)
            else:
                break
        if not lead:
            break
        row = Row(lead, ln.row.y, ln.row.size)
        row.spaces = ln.row.spaces
        got.append(linear(row, ln.row.spaces, ln.row.radicals))
        if len(lead) < len(items):
            # a heading ends at its full stop ("Depth of shear zone."); italic
            # words that run on into the sentence are emphasis, not a heading
            ended = got[-1].endswith((".", ":")) or items[len(lead)].t in (".", ":")
            break
        if got[-1].endswith((".", ":")):
            ended = True
            break
    title = " ".join(got).strip()
    if not ended or not any(c.isalpha() for c in title):
        return ""
    return title.rstrip(".:").strip()


class Flow:
    """Turns a chapter's pages into blocks."""

    def __init__(self, book, number_prefix: str, lists: dict):
        self.book = book
        self.prefix = number_prefix
        self.lists = lists
        self.blocks: list[Block] = []
        self.para: Block | None = None      # the paragraph or list being read
        self.table: Block | None = None     # the table being read
        self.notes: list = []               # its note lines, on the page being read
        self.caption: Block | None = None   # a caption whose lines are being read
        self.head: Block | None = None      # a heading whose lines are being read
        self.prev: Line | None = None
        self.sid = ""
        self.path: list[str] = []
        self.page = ""
        self.right = 540.0
        self.item_x = 0.0
        self.seen_grid = False
        self.titles: list[str] = []         # the chapter's own title lines

    # -- helpers -----------------------------------------------------------
    def close_para(self):
        self.para = None

    def close_table(self):
        if self.table is not None:
            self._flush_notes()
        self.table = None
        self.seen_grid = False

    def _flush_notes(self):
        if self.notes:
            for p in paragraphs(self.notes, MARGIN, self.right, _NOTE_START):
                self.table.pieces.append((self.page, p.text))
                if p.crowded:
                    self.table.crowded.append((self.page, p.text))
        self.notes = []

    def add(self, block: Block) -> Block:
        self.blocks.append(block)
        return block

    # -- one page ----------------------------------------------------------
    def read(self, pd: PageData):
        if self.table is not None:
            self._flush_notes()
        self.page = pd.label
        self.right = pd.right
        self.prev = None
        self.head = self.caption = None
        flow = pd.flow
        k = 0
        while k < len(flow):
            e = flow[k]
            k += 1
            if isinstance(e, Grid):
                self.close_para()
                self.caption = self.head = None
                if self.table is None:
                    self.book.note("a ruled table with no caption over it")
                    self.table = self.add(Block("table", sep="\n", page=self.page))
                self._flush_notes()
                self.seen_grid = True
                for ln in e.lines():
                    self.table.pieces.append((self.page, ln.text))
                    if ln.crowded:
                        self.table.crowded.extend((self.page, t) for t in ln.auto)
                    for num, cap in ln.figures:
                        self.add(Block("figure", number=num, title=cap, page=self.page,
                                       shown=False))
                self.prev = None
                continue
            ln = e
            row = ln.row
            small = ln.size < 11.0
            bold = row is not None and row.bold
            text = ln.text
            # the chapter's own title lines ("Chapter 5" and its title) come
            # before its first paragraph heading
            if bold and not small and not self.sid and not _HEAD.match(text):
                self.titles.append(text)
                self.prev = ln
                continue
            # a heading's or a caption's further lines
            if bold and not small and self.head is not None and self.prev is not None \
                    and ln.y - self.prev.y < 17:
                self.head.title = _join(self.head.title, text)
                self.prev = ln
                continue
            if bold and small and self.caption is not None and self.prev is not None \
                    and ln.y - self.prev.y < 15 and not re.match(r"^(Table|Figure) ", text) \
                    and (self.caption.kind == "figure" or abs(ln.x0 - MARGIN) < 2):
                self.caption.title = _join(self.caption.title, text)
                self.prev = ln
                continue
            self.head = self.caption = None
            m = _HEAD.match(text) if (bold and not small and abs(ln.x0 - MARGIN) < 3) else None
            if m:
                self.close_para()
                self.close_table()
                self.sid, self.path = hyphen(m.group(1)), []
                self.head = self.add(Block("head", number=self.sid, title=m.group(2),
                                           page=self.page))
                self.prev = ln
                continue
            m = re.match(rf"^Table ({NUM})\s*(.*)$", text) if (bold and small) else None
            if m:
                self.close_para()
                self.close_table()
                self.table = self.caption = self.add(
                    Block("table", sep="\n", number=hyphen(m.group(1)),
                          title=m.group(2), page=self.page))
                self.prev = ln
                continue
            m = re.match(rf"^Figure ({NUM})\.\s*(.*)$", text) if (bold and small) else None
            if m:
                self.close_para()
                self.close_table()
                self.caption = self.add(Block("figure", number=hyphen(m.group(1)),
                                              title=m.group(2), page=self.page))
                self.prev = ln
                continue
            if self.table is not None and small and not ln.eq \
                    and (not bold or not self.seen_grid):
                # a table's notes (a table on a new page may open with
                # them), or a heading set over its columns
                self.notes.append(ln)
                self.prev = ln
                continue
            self.close_table()
            self.body_line(ln, flow, k - 1)
            self.prev = ln
        if self.table is not None:
            self._flush_notes()

    # -- running text ------------------------------------------------------
    def body_line(self, ln: Line, flow: list, k: int):
        text = ln.text
        row = ln.row
        if ln.eq:
            self.close_para()
            b = self.add(Block("para", [(self.page, text)], page=self.page))
            return
        # a subparagraph's mark opens its first line
        if row is not None and abs(ln.x0 - INDENT) < 3 and ln.size >= 11.0:
            for level, pat in enumerate(_MARKS, 1):
                m = pat.match(text)
                if not m:
                    continue
                mark = m.group(1)
                have = self.path[level - 1] if len(self.path) >= level else None
                if (have and mark == _succ(have)) or (not have and mark in ("a", "1")):
                    if len(self.path) < level - 1:
                        self.book.note(f"{self.sid}: mark {m.group(0).strip()!r} "
                                       f"opens a level under none")
                    self.path = (self.path + [""] * level)[:level - 1] + [mark]
                    sid = self.sid + "".join(
                        _mark_text(lv, mk) for lv, mk in enumerate(self.path, 1) if mk)
                    title = _lead_title(flow, k, len(m.group(0).replace(" ", "")))
                    self.close_para()
                    self.add(Block("sub", number=sid, title=title,
                                   untitled=not title, page=self.page))
                    text = text[m.end():].strip()
                    if text:
                        self.para = self.add(Block("para", [(self.page, text)],
                                                   page=self.page))
                        if ln.crowded:
                            self.para.crowded.append((self.page, ln.text))
                    return
                self.book.note(f"{self.sid}: a line opens with {m.group(0).strip()!r}, "
                               f"out of sequence after {self.path}; read as text")
                break
        # an appendix's list of its examples: "Example B–3" at the margin, its
        # description in a column set in from it, the description's further
        # lines and its parts ("a. Solution for ...") in that column
        examples = self.para is not None and self.para.kind == "list" \
            and bool(_EXAMPLE.match(self.para.pieces[0][1]))
        if row is not None and abs(ln.x0 - MARGIN) < 3 and _EXAMPLE.match(text):
            if not examples:
                self.para = self.add(Block("list", sep="\n", page=self.page))
            self.para.pieces.append((self.page, text))
            if ln.crowded:
                self.para.crowded.append((self.page, ln.text))
            return
        if examples and row is not None and ln.x0 > MARGIN + 40:
            if re.match(r"^[a-z]\.\s", text) or self.para.pieces[-1][0] != self.page:
                self.para.pieces.append((self.page, text))
            else:
                page, last = self.para.pieces[-1]
                self.para.pieces[-1] = (page, _join(last, text))
            if ln.crowded:
                self.para.crowded.append((self.page, ln.text))
            return
        # a list (of symbols under "where:", of items) is set in from the
        # margin: past the indent of a subparagraph's first line, or anywhere
        # in from the margin while a list is being read
        under_where = self.para is not None and (
            self.para.kind == "list" or self.para.text.strip().lower() == "where:")
        listed = row is not None and ln.x0 < 380 and (
            ln.x0 > 95 or (ln.x0 > MARGIN + 4 and under_where
                           and (abs(ln.x0 - INDENT) > 3 or bool(_ITEM.match(text)))))
        bullet = text.startswith("• ")
        prev = self.prev
        if listed or bullet:
            if self.para is not None and prev is not None \
                    and abs(ln.size - prev.size) > 1.2:
                self.close_para()        # a note in smaller type under the list
            in_list = self.para is not None and self.para.kind == "list" \
                and len(self.para.pieces) > (1 if self.para.text.lower().startswith("where") else 0)
            if not in_list:
                self.item_x = ln.x0
            # an item starts where the list's first item starts ("B′ = ...");
            # a line set further in runs on from the item before it
            item = bullet or (bool(_ITEM.match(text)) and ln.x0 <= self.item_x + 6)
            if self.para is not None and self.para.kind == "list" and prev is not None \
                    and not item and self.para.pieces[-1][0] == self.page:
                page, last = self.para.pieces[-1]
                self.para.pieces[-1] = (page, _join(last, text))
            elif self.para is not None and self.para.kind == "list":
                self.para.pieces.append((self.page, text))
            else:
                # "where:" over a list of symbols is the list's first line
                if self.para is not None and self.para.kind == "para" \
                        and self.para.text.strip().lower() == "where:":
                    self.para.kind, self.para.sep = "list", "\n"
                else:
                    self.para = self.add(Block("list", sep="\n", page=self.page))
                self.para.pieces.append((self.page, text))
            if ln.crowded:
                self.para.crowded.append((self.page, ln.text))
            return
        new = self.para is None or self.para.kind != "para"
        if not new and prev is not None:
            pitch = 1.15 * max(prev.size, ln.size)
            gap = ln.y - prev.y
            short = (self.right - prev.x1) >= _first_word_width(ln) + 0.25 * ln.size + 1
            if abs(ln.size - prev.size) > 1.2:
                new = True
            elif gap > 1.8 * pitch or (gap > 1.45 * pitch and short):
                new = True
            elif gap < 0:
                new = True
        if new:
            self.para = self.add(Block("para", [(self.page, text)], page=self.page))
        elif self.para.pieces[-1][0] == self.page:
            page, last = self.para.pieces[-1]
            self.para.pieces[-1] = (page, _join(last, text))
        else:
            self.para.pieces.append((self.page, text))
        if ln.crowded:
            self.para.crowded.append((self.page, ln.text))


# ---------------------------------------------------------------------------
# blocks as sections
# ---------------------------------------------------------------------------

#: Limits of one section as the reference tools fetch it (the same as
#: ``build_printed_text.MAX_BODY_CHARS`` / ``MAX_SECTION_JSON_CHARS``).
MAX_BODY_CHARS = 12000
MAX_SECTION_JSON_CHARS = 14000
#: A table longer than this is cut between rows before a section is split.
MAX_BLOCK_CHARS = 5000
_PAGE_MARK = re.compile(r"\[p\. ([^\]]+)\]")


def opening_words(text: str, limit: int = 80) -> str:
    """The title of a subparagraph printed without a heading: its opening
    words, to the end of its first sentence where that is short."""
    text = re.sub(r"\s+", " ", _PAGE_MARK.sub(" ", text)).strip()
    first = re.match(r"^(.{12,%d}?[.:;])(?:\s|$)" % limit, text)
    if first:
        return first.group(1).rstrip(".:;")
    if len(text) <= limit:
        return text.rstrip(".:;")
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:") + " …"


def render(blocks: list[Block], book) -> tuple[str, list[str], list[str]]:
    """A section's blocks as its body, with a page marker wherever the
    printed page changes, and the figures and tables captioned in it."""
    paras, figures, tables = [], [], []
    last = None
    for b in blocks:
        pieces, sep = b.pieces, b.sep
        if b.kind == "figure":
            pieces = [(b.page, f"Figure {b.number}. {b.title}")] if b.shown else []
            figures.append(f"Figure {b.number}: {b.title}")
        elif b.kind == "table":
            caption = f"Table {b.number} {b.title}".strip() if b.number else ""
            typed = book.tables.get(b.number)
            if typed is not None:
                book.used_tables.add(b.number)
                pieces = [(b.page, typed["note"])] + [(b.page, r) for r in typed["rows"]]
            if caption:
                pieces = [(b.page, caption)] + list(pieces)
                tables.append(f"Table {b.number}: {b.title}")
        text = ""
        for page, piece in pieces:
            if page != last:
                mark = f"[p. {page}]"
                text = (text + sep + mark + sep) if text else mark + " "
                last = page
            elif text:
                text += sep
            text += piece
        if text:
            paras.append(text)
    body = number_hyphens("\n\n".join(paras))
    return body, [number_hyphens(f) for f in figures], [number_hyphens(t) for t in tables]


def equations_of(body: str, book) -> list[dict]:
    """The numbered equations a body shows, in order, each with the formula
    and symbols typed in for it."""
    out = []
    for num in dict.fromkeys(re.findall(r"\[Eq\. ([^\]]+)\]", body)):
        entry = book.typed.get(num, {})
        k = body.index(f"[Eq. {num}]")
        words = re.sub(r"\[[^\]]*\]", " ", body[max(0, k - 600):k])
        # the words that lead to the equation: the sentence before its line
        lead = [p for p in words.split("\n\n")[:-1] if re.search(r"[A-Za-z]{4}", p)]
        tail = re.sub(r"\s+", " ", lead[-1]).strip()[-200:] if lead else ""
        tail = re.split(r"(?<=[.;])\s+", tail)[-1] if tail else ""
        page = entry.get("page") or next(iter(reversed(_PAGE_MARK.findall(body[:k]))), None)
        where = f" (p. {page})" if page else ""
        desc = entry.get("description") or (
            f"Equation {num}, introduced by: \"{tail}\"{where}." if len(tail) >= 12
            else f"Equation {num} as printed{where}.")
        eq = {"id": f"Eq. {num}", "description": desc}
        if entry.get("formula"):
            eq["formula"] = entry["formula"]
            eq["variables"] = entry.get("variables", {})
            if entry.get("notes"):
                eq["notes"] = entry["notes"]
            eq["source"] = f"Typed in from p. {entry['page']}."
        eq["implemented_in"] = entry.get("implemented_in")
        out.append(eq)
    return out


def _cut_tables(body: str) -> str:
    """A table longer than ``MAX_BLOCK_CHARS`` cut between its rows, each
    further piece opening with ``[Table B-3a, continued]``, so that a long
    section can be split inside it."""
    out = []
    for para in body.split("\n\n"):
        if len(para) <= MAX_BLOCK_CHARS or "\n" not in para:
            out.append(para)
            continue
        m = re.match(rf"^(?:\[p\. [^\]]+\] )?Table ({NUM.replace('–', '')})\s", para)
        again = f"[Table {m.group(1)}, continued]" if m else "[continued]"
        cur: list[str] = []
        for row in para.split("\n"):
            if cur and len("\n".join(cur)) + len(row) > MAX_BLOCK_CHARS:
                out.append("\n".join(cur))
                cur = [again]
            cur.append(row)
        out.append("\n".join(cur))
    return "\n\n".join(out)


def split_long(sec: dict, what: str) -> list[dict]:
    """A section over the size limits as the section (its first part) and
    parts lettered ``.a``, ``.b`` ... after it, cut between paragraphs or
    between a table's rows. The letters are not printed: each part's title
    and applicability say which printed pages it holds."""
    overhead = len(json.dumps(dict(sec, body="", equations=[])))

    def fits(text):
        eqs = [e for e in sec["equations"] if f"[{e['id']}]" in text]
        return (len(text) <= MAX_BODY_CHARS
                and len(json.dumps(text)) + len(json.dumps(eqs)) + overhead
                <= MAX_SECTION_JSON_CHARS)

    if fits(sec["body"]):
        return [sec]
    chunks, cur = [], []
    for p in _cut_tables(sec["body"]).split("\n\n"):
        if cur and not fits("\n\n".join(cur + [p])):
            chunks.append(cur)
            cur = []
        cur.append(p)
    if cur:
        chunks.append(cur)
    out, page = [], None
    for n, ch in enumerate(chunks):
        text = "\n\n".join(ch)
        start = page
        if text.startswith("[p."):
            start = _PAGE_MARK.match(text).group(1)
        for m in _PAGE_MARK.finditer(text):
            page = m.group(1)
        if start and not text.startswith("[p."):
            text = f"[p. {start}] " + text
        pages = f"p. {start}" if start == page else f"pp. {start} to {page}"
        part = dict(sec, body=text,
                    equations=[e for e in sec["equations"] if f"[{e['id']}]" in text],
                    figures=[f for f in sec["figures"]
                             if re.search(rf"(?:^|\n|\] |\| ){re.escape(f.split(':')[0])}\. ", text)],
                    tables=[t for t in sec["tables"]
                            if re.search(rf"(?:^|\n\n|\] ){re.escape(t.split(':')[0])} ", text)])
        if n:
            letter = chr(ord("a") + n - 1)
            part.update(
                section_id=f"{sec['section_id']}.{letter}",
                title=f"{sec['title']} (continued, {pages})",
                applicability=(f"Part {n + 1} of {what} {sec['section_id']} ({pages}); "
                               "the letter is not printed, the section is split here "
                               "to fit the reference tools."))
        out.append(part)
    return out


def sections_of(blocks: list[Block], ch: dict, vol: dict, book) -> list[dict]:
    """A chapter's blocks as its sections, one for every paragraph and
    subparagraph the manual prints."""
    label = ch.get("appendix")
    where = (f"Appendix {label} ({ch['title'].split(': ', 1)[-1]})" if label
             else f"Chapter {ch['number']} ({ch['title']})")
    groups: list[tuple[Block | None, list[Block]]] = []
    for b in blocks:
        if b.kind in ("head", "sub"):
            groups.append((b, []))
        else:
            if not groups:
                groups.append((None, []))
            groups[-1][1].append(b)
    out = []
    for head, content in groups:
        body, figures, tables = render(content, book)
        if head is None:
            if not label:
                book.note(f"chapter {ch['number']}: text before its first paragraph")
            sid, title, untitled, page = label or f"{ch['number']}-0", \
                ch["title"].split(": ", 1)[-1], False, content[0].page
            unit = "appendix" if label else "chapter"
        else:
            sid, untitled, page = head.number, head.untitled, head.page
            title = number_hyphens(head.title) if head.title else opening_words(body)
            unit = "paragraph"
        pages = [page] + _PAGE_MARK.findall(body)
        span = f"p. {pages[0]}" if pages[0] == pages[-1] else f"pp. {pages[0]} to {pages[-1]}"
        applicability = (f"{vol['volume_id']}, {where}, "
                         + (f"paragraph {sid}, " if head is not None else "")
                         + f"printed {span}.")
        if untitled:
            applicability += (" The manual prints this subparagraph without a "
                              "heading; the title is its opening words.")
        for b in content:
            for pg, text in b.crowded:
                book.crowded.append((pg, sid, text))
        sec = {"section_id": sid, "title": title, "body": body, "key_points": [],
               "equations": equations_of(body, book), "figures": figures,
               "tables": tables, "applicability": applicability}
        out.extend(split_long(sec, unit))
    return out


def _same(a: str, b: str) -> bool:
    norm = lambda s: re.sub(r"[^a-z0-9]", "", number_hyphens(s).lower())  # noqa: E731
    return norm(a) == norm(b)


def build_volume(vol: dict, manifest_dir, skip: set, draft: bool = False):
    """Every chapter of an Army-layout volume: ``{number: chapter dict}``
    (with ``_missing``: paragraphs of the printed contents not found) and
    the build's report. Stops (``ValueError``) on anything a reader has to
    settle first, unless ``draft``."""
    pdf = (manifest_dir / vol["pdf_path"]).resolve()
    book = Book(vol, draft)
    chapters = {}
    with fitz.open(str(pdf)) as doc:
        front = read_front(doc, vol["contents_pages"][0], vol["contents_pages"][1], book)
        book.front = front
        for ch in vol["chapters"]:
            n = ch["number"]
            if n in skip:
                continue
            label = ch.get("appendix") or str(n)
            flow = Flow(book, label, front)
            for i in range(ch["page_start"] - 1, ch["page_end"]):
                pd = read_page(doc[i], i, book)
                book.page_index[pd.label] = i
                if pd.lettering:
                    book.lettering[pd.label] = pd.lettering
                flow.read(pd)
            sections = sections_of(flow.blocks, ch, vol, book)
            printed_title = " ".join(flow.titles[1:])
            want = ch["title"].split(": ", 1)[-1]
            if not _same(printed_title, want):
                book.problems.append(f"chapter {n}: the manifest's title {want!r} is "
                                     f"printed {printed_title!r}")
            heads = {b.number: b for b in flow.blocks if b.kind == "head"}
            missing = []
            for sid, (title, page) in front["paragraphs"].items():
                if sid.split("-")[0] != label:
                    continue
                b = heads.get(sid)
                if b is None:
                    missing.append(sid)
                elif not _same(b.title, title) or str(page) != b.page:
                    book.problems.append(
                        f"paragraph {sid}: contents {title!r} p. {page}, "
                        f"printed {b.title!r} p. {b.page}")
            for kind, key in (("table", "tables"), ("figure", "figures")):
                seen = {}
                for b in flow.blocks:
                    if b.kind == kind and b.number:
                        seen.setdefault(b.number, b)
                for num, (cap, page) in front[key].items():
                    if num.split("-")[0] != label:
                        continue
                    b = seen.get(num)
                    if b is None:
                        book.problems.append(f"{kind} {num}: listed, no caption found")
                    elif not _same(b.title, cap):
                        book.notes.append(f"{kind} {num}: listed {cap!r}, captioned "
                                          f"{number_hyphens(b.title)!r} (p. {b.page})")
                    elif str(page) != b.page:
                        book.notes.append(f"{kind} {num}: listed on p. {page}, "
                                          f"captioned on p. {b.page}")
                for num in seen:
                    if num not in front[key]:
                        book.problems.append(f"{kind} {num}: captioned on p. "
                                             f"{seen[num].page}, not in the list")
            chapters[n] = {
                "reference_id": vol["volume_id"],
                "reference_title": vol.get("volume_title", ""),
                "volume": vol.get("volume"),
                "chapter": n,
                "chapter_title": ch["title"],
                "sections": sections,
                "_missing": missing,
            }
    book.finish(chapters)
    if book.problems and not draft:
        raise ValueError(f"{vol['volume_id']}: " + "; ".join(book.problems[:40])
                         + (f"; and {len(book.problems) - 40} more"
                            if len(book.problems) > 40 else ""))
    return chapters, book
