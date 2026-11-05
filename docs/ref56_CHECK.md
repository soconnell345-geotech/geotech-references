# REF-56: the search databases are built atomically

Branch `claude/ref-56-atomic-db-build`, from main `1427409`.

## The defect, reproduced on main

`_retrieval_db._build_db` (and `_figures_db._build_db`, the same code) deleted
the database and rebuilt it in place. The refs suite itself shows it: on main,
`pytest tests -n 4` with an empty temp folder gives **6,337 passed, 87 errors**
(`sqlite3.OperationalError: disk I/O error`), and a second run on the warm
folder **6,319 passed, 105 errors** (all `disk I/O error`, in
`test_result_size.py` and `test_query_expansion.py`). An earlier run on a fresh
container also gave 14 `table sections already exists`. Warm runs fail too
because `test_query_expansion.py` and `test_figures_db.py` call `rebuild_db()`
in a fixture: one xdist worker unlinks the file while another is reading it.

## What changed

- **`geotech_references/_atomic_db.py` (new).**
  - `build_atomically` (line 130): builds into `tempfile.mkstemp(dir=<db folder>,
    prefix=".<db name>.", suffix=".building")`, commits, closes, then
    `os.replace`s it over the real name. If the fill raises (any exception,
    `KeyboardInterrupt` included) the temporary file and its `-journal` are
    removed and the old database is untouched.
  - `ensure_built` (line 184): what `_ensure_db` now calls.
  - `_replace` (line 96): retries a `PermissionError` (Windows refuses to
    replace a file another process has open) for up to 2 s with a growing pause.
  - **Windows, file still held after the retries:** if the database at the real
    name is now current (another process put it there), it is used and this
    process's copy is removed. Otherwise this process reads its own complete
    copy (kept in `_PENDING`), tries the move once on each later call, and an
    `atexit` hook (line 127) removes the copy if it was never moved. Never
    raises for a held file; never leaves a partial file at the real name.
  - `_sweep_stale` (line 82): a process killed mid-build cannot clean up, so each
    build first removes this database's `.building` files older than 15 minutes
    (`STALE_SECONDS`); younger ones may be a live build in another process and
    are left.
- **`_retrieval_db.py`:** `_build_db` (line 185) calls `build_atomically` and
  returns the path to read; the table creation and indexing moved unchanged
  into `_fill_db` (line 196; the diff is mostly that dedent, `git diff -w`
  shows the real change); `_ensure_db` (line 314) calls `ensure_built`.
- **`_figures_db.py`:** the same (lines 79, 90, 168). The task named only the
  text database, but the figure database had the identical delete-and-rebuild
  and the same race in the suite, so it uses the same helper.
- `CLAUDE.md`: one architecture line for `_atomic_db.py`.

### Concurrent builders: each builds its own copy (no waiting)

Two processes that start at once each build a temporary copy and the last
`os.replace` wins; both copies are identical (same sources, same code), and a
reader only ever opens a complete file (on Linux a reader holding the old
inode keeps reading it). Waiting for the first builder would need a lock
file, which differs between Linux (`fcntl`) and Windows (`msvcrt`), and a
builder that dies leaves a stale lock the others must detect and break, which
is another race. A build takes a few seconds and happens only on first use
after an install or a source edit, so building twice now and then is cheaper
than getting a lock wrong.

## Tests: `tests/test_atomic_db_build.py` (9)

| Test | On main |
|---|---|
| `test_processes_started_at_once_on_an_empty_temp_folder_agree[4]`: 4 fresh interpreters, temp folder = an empty dir, one shared start time, source reads slowed 3 ms each so builds overlap; all four return the same references, search hits and figure count as this process, one database of each kind, no build file left | fails (`disk I/O error`, empty results) |
| `test_an_interrupted_build_leaves_the_old_database_usable` (a `KeyboardInterrupt` part way through `rebuild_db`) | fails |
| `test_a_killed_build_leaves_the_old_database_and_its_file_is_swept` | fails |
| `test_a_held_file_on_windows_never_raises_and_is_moved_in_later` (`os.replace` mocked to raise `PermissionError`) | fails |
| `test_a_held_file_that_is_now_current_is_used_and_the_copy_removed` | fails |
| `test_a_held_file_is_retried_until_the_reader_lets_go` | fails |
| `test_the_figure_database_is_built_the_same_way` | fails |
| `test_a_fresh_build_file_of_another_process_is_not_swept` | passes (guards the sweep, which main does not have) |
| `test_pending_copies_are_removed_when_the_process_ends` | passes (a unit test of the new helper's exit hook) |

(On main the file was run with `_atomic_db.py` present so it imports; main's
`_build_db` does not use it.) The new file passed 5 runs out of 5.

## Suite

`python3.12` venv, `pip install -e . pytest pytest-xdist` plus numpy, scipy and
matplotlib (without matplotlib 4 test modules fail to import on main and
branch alike). `pytest tests -q -n 4`, judged on the exit code, each with its
own empty `TMPDIR`:

| | cold temp folder | warm |
|---|---|---|
| main | 6,337 passed, 37 skipped, **87 errors** (exit 1) | 6,319 passed, 37 skipped, **105 errors** (exit 1) |
| branch | **6,433 passed, 37 skipped, 0 failed** (exit 0) | 6,433 passed, 37 skipped (exit 0) |

6,433 = main's 6,424 tests + the 9 new ones. Both runs left exactly the two
databases in the temp folder and no `.building` file.

## The 2026-10-31 `did_you_mean` failure

Likely explained by this. The app's
`test_reference_filter_unknown_name_gets_did_you_mean` asserts `gec_9` is in
the suggestions, and those come from `list_indexed_references()`, which reads
the database. The app suite runs under pytest-xdist (since 2026-10-19); a
worker reading while another deleted and refilled the database sees no rows or
only some references (the indexing runs in one transaction, so an uncommitted
rebuild reads as empty), giving a suggestion list without `gec_9`. Not chased
further.

## Noted, not fixed

- If a source JSON is edited *during* a build, the built file's mtime is later
  than the edit and the edit is not picked up until the next edit (as before).
- Another process's stale sweep could delete a Windows pending copy that is
  older than 15 minutes and not open at that moment; `ensure_built` checks the
  copy still exists and builds again if not.
- The Windows paths are tested on Linux with `os.replace` mocked; no Windows
  run was made here.
