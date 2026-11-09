"""The chapter-text schema check, shared by the audit script and the
local-pack checker (REF-64).

Moved here from ``scripts/audit_chapter_text.py`` (which imports it back),
so the built-in references and a deployment's local packs
(``python -m geotech_references.packs check``) are held to one validator.
:func:`validate_schema` checks one chapter file's structure against
``chapter_schema.json``'s rules (beside this module, shipped in the wheel);
the audit script's other checks
(equation coverage, ``implemented_in`` paths) import a reference's Python
modules and stay in the script.
"""

from __future__ import annotations

import re
from collections import defaultdict


def _is_container(sid: str, sections: list, index: int) -> bool:
    """A container section has child subsections later in document order;
    its body may legitimately be empty."""
    if not sid:
        return False
    for j in range(index + 1, len(sections)):
        other = sections[j]
        if not isinstance(other, dict):
            continue
        other_id = other.get("section_id", "")
        if other_id.startswith(sid + ".") or other_id.startswith(sid + "-"):
            return True
    return False


#: A section number: FHWA/GEC dot form ('5.7.2'), UFC hyphen-then-dot form
#: ('4-2.1'), prologue ('P-1'), a combined section ('5.15-5.16'), the
#: lettered level GEC-11 prints ('3.5.2.a', '4.4.7.k'), and a Eurocode
#: annex or appendix as printed: its letter alone for its own text ('A'), with
#: its clause numbers ('D.3', 'X.4.11.2'), or in the UFC hyphen form
#: ('B-3.4', UFC 3-220-20 Appendix B); a lettered part of a section split
#: to fit the reference tools ('D.15.a', GEC-12 Appendix D).
SECTION_ID = re.compile(r"^([0-9P]+([-.][0-9]+)*(\.[a-z])?|[A-Z]([-.][0-9]+)*(\.[a-z])?)$")

#: Fields every section carries. ``summary`` is not among them: it is the
#: short text a ``reference_search`` hit shows, written for DM7 and some
#: other references, and a reference without it is searched on its title
#: and body (BACKLOG REF-05, REF-06).
REQUIRED_FIELDS = ("section_id", "title", "body", "key_points", "equations",
                   "figures", "tables", "applicability")
#: A subsection a file nests inside its section (GEC-12's ``subsections``)
#: carries its own number, title and text and shares the rest with the
#: section it sits in.
REQUIRED_NESTED_FIELDS = ("section_id", "title", "body")

#: A body shorter than this, in a section with no subsections, is a stub.
#: Codes print one-sentence sections ("This section is removed in its
#: entirety.", GSA 2016 Section 4.3), so the floor is a sentence, not a
#: paragraph.
BODY_MIN_CHARS = 20
SUMMARY_MIN_CHARS = 50
SUMMARY_MAX_CHARS = 700
#: A summary shorter than SUMMARY_MIN_CHARS is a stub only where the body
#: it summarises is longer than this.
SUMMARY_STUB_BODY_CHARS = 200


def _flat_sections(sections: list) -> list[tuple[str, dict, bool, bool]]:
    """Every section at every level, in file order, as ``(location, section,
    is_container, is_nested)``. A section is a container when the file nests
    subsections in it or lists sections numbered under it after it."""
    out: list[tuple[str, dict, bool, bool]] = []

    def walk(secs, where, nested):
        for i, sec in enumerate(secs or []):
            loc = f"{where}[{i}]"
            if not isinstance(sec, dict):
                out.append((loc, sec, False, nested))
                continue
            sid = sec.get("section_id", "")
            holds = bool(sec.get("subsections"))
            out.append((loc, sec, holds or _is_container(sid, secs, i), nested))
            walk(sec.get("subsections"), f"{loc}.subsections", True)

    walk(sections, "sections", False)
    return out


def validate_schema(chapter_json: dict) -> list[str]:
    errors: list[str] = []
    required_top = [
        "reference_id",
        "reference_title",
        "chapter",
        "chapter_title",
        "sections",
    ]
    for k in required_top:
        if k not in chapter_json:
            errors.append(f"missing top-level key: {k}")
    sections = chapter_json.get("sections", [])
    if not isinstance(sections, list) or not sections:
        errors.append("sections must be a non-empty array")
        return errors

    seen_ids: dict[str, int] = defaultdict(int)
    for loc, sec, container, nested in _flat_sections(sections):
        if not isinstance(sec, dict):
            errors.append(f"{loc}: not an object")
            continue
        sid = sec.get("section_id", "")
        where = f"{loc} ({sid})" if sid else loc
        for k in REQUIRED_NESTED_FIELDS if nested else REQUIRED_FIELDS:
            if k not in sec:
                errors.append(f"{where}: missing key '{k}'")
        body = sec.get("body", "")
        summary = sec.get("summary", "")
        if summary is not None and not isinstance(summary, str):
            errors.append(f"{where}: summary is not a string")
        elif summary:
            if len(summary) > SUMMARY_MAX_CHARS:
                errors.append(f"{where}: summary > {SUMMARY_MAX_CHARS} chars")
            elif (len(summary) < SUMMARY_MIN_CHARS and isinstance(body, str)
                  and len(body) > SUMMARY_STUB_BODY_CHARS):
                errors.append(f"{where}: summary < {SUMMARY_MIN_CHARS} chars "
                              f"for a {len(body)}-char body")
        if sid:
            seen_ids[sid] += 1
            if not SECTION_ID.match(sid):
                errors.append(f"{loc}: section_id '{sid}' has invalid format")
        if not isinstance(body, str):
            errors.append(f"{where}: body is not a string")
        elif len(body.strip()) < BODY_MIN_CHARS and not container and not (
                len(summary or "") >= SUMMARY_MIN_CHARS or sec.get("key_points")):
            # a code may print a pointer ("See UFC 3-250-07.") as the whole
            # section; its summary or key points then say what it covers
            errors.append(f"{where}: body is shorter than {BODY_MIN_CHARS} "
                          "chars with no subsections, summary or key points")
        kp = sec.get("key_points")
        if kp is not None and not isinstance(kp, list):
            errors.append(f"{where}: key_points is not a list")
        elif isinstance(kp, list):
            if len(kp) > 12:
                errors.append(f"{where}: key_points has {len(kp)} items (at most 12)")
            for j, p in enumerate(kp):
                if not isinstance(p, str):
                    errors.append(f"{loc}.key_points[{j}]: not a string")
                elif len(p) > 300:
                    errors.append(f"{loc}.key_points[{j}]: exceeds 300 chars")
        ap = sec.get("applicability", "")
        if (not nested or "applicability" in sec) and isinstance(ap, str) \
                and len(ap) < 10:
            errors.append(f"{where}: applicability is too short")

    duplicates = [sid for sid, count in seen_ids.items() if count > 1]
    if duplicates:
        errors.append(f"duplicate section_ids: {duplicates}")

    return errors
