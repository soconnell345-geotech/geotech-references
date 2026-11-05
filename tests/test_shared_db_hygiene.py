"""INF-55: test modules do not force-rebuild the shared search databases.

The text and figure databases live in the temp folder, one file per copy
of the package, shared by every pytest-xdist worker. Module fixtures used
to call ``rebuild_db()``, so each worker rewrote that file in every module;
before REF-56 the rebuild deleted it under the other workers, which gave
sqlite 'readonly database', 'disk I/O error' and 'table sections already
exists' errors on four workers. Fixtures call ``_ensure_db()`` (build only
when missing or stale); a forced rebuild belongs in a test that first points
the database at its own folder (``test_atomic_db_build.py``).
"""

import re
from pathlib import Path

TESTS = Path(__file__).resolve().parent
ALLOWED = {"test_atomic_db_build.py", Path(__file__).name}


def test_no_test_module_force_rebuilds_the_shared_database():
    offenders = []
    for f in sorted(TESTS.glob("test_*.py")):
        if f.name in ALLOWED:
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            code = line.split("#", 1)[0]
            if re.search(r"\b_(retrieval|figures)_db\.(rebuild_db|_build_db)\(",
                         code):
                offenders.append(f"{f.name}:{n}: {line.strip()}")
    assert not offenders, offenders
