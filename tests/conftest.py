def pytest_configure(config):
    # INF-55: build the shared search databases once per run, before any
    # pytest-xdist worker starts, so every test reads a database built by
    # this tree's code; module fixtures then only _ensure_db().
    if hasattr(config, "workerinput"):
        return
    from geotech_references import _figures_db, _retrieval_db
    _retrieval_db.rebuild_db()
    _figures_db.rebuild_db()
