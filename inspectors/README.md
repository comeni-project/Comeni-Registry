# Inspectors

Measure an uploaded sample's head on the server, so a person who is not sure of a fact can
answer with a file. An inspection is built from small pieces, each written once:

- **codecs** unwrap bytes (`gzip`);
- **formats** turn bytes into records and confirm the file is what its name says (`fastq`);
- **measures** read records of one shape and produce one measurement (`read_length`).

A format and every measure that reads its record shape make an inspection. Add a format, and every
measure of its shape works on it; add a measure, and it works on every format of its shape.

Each piece is a folder: its declaration (`measure.yml`, `format.yml` or `codec.yml`) and, beside
it, `piece/` with its code, its tests and, for a format, its fixtures.

## Add a measure

1. Make sure the measurement exists in `vocabulary/measurements/` (`declares: measurement`, an
   `id`, a `kind`, a `description` and a `cite`). If you are declaring it now, leave out
   `assertion_only`: your measure is what measures it.
2. Create `measures/<id>/measure.yml`:

   ```yaml
   declares: measure
   id: gc_content            # the folder's name
   version: 1.0.0
   measures: gc_content      # the measurement it produces
   record: sequence          # the record shape it reads
   decided: {min_records: 1000}   # the thresholds below which it says "undetermined"
   entry: piece/gc_content.py
   ```

3. Write `piece/<id>.py` with a class `Accumulator`: `__init__(self, decided, files)`, then
   `add(row)` for each row (one record per file, side by side), then `result()` returning
   `Value(value=..., evidence={...})` or `Undetermined(reason=..., evidence={...})` from
   `comeni_inspect.outcome`. Below a threshold in `decided`, it is undetermined, with why. The
   file names in `files` may word a reason; they never decide.
4. Write `piece/test_<id>.py` against the FASTQ fixtures, including a case that is undetermined:

   ```python
   from comeni_inspect.run import inspect
   from support_pieces import request_for

   def test_it_is_measured():
       fact = inspect(*request_for("single_150", ["gc_content"])).facts["gc_content"]
       assert fact.value is not None
   ```

5. From a Comeni Labs checkout with this registry at `registry/`, run the pieces' tests and the
   guards, regenerate the golden reports (every case now carries your measure too), read the
   ones that changed, and run them again:

   ```bash
   uv run pytest registry/inspectors tests/guards/test_inspector_pieces.py
   uv run python -c "from comeni_inspect import harness; from pathlib import Path; [(c.folder / 'expected.json').write_text(harness.run_case(c) + '\n') for c in harness.cases(Path('registry'))]"
   uv run pytest tests/registry/test_inspection_conformance.py
   ```

A **new measurement** (step 1) is also a new type, `measurement.<id>`, so when Comeni Labs moves
to this registry a few derived files move with it: the generated `profile.pyi`
(`uv run python tools/generate_types.py`), the golden prompts and scaffolds under
`packages/mendel-forge/tests` (`uv run pytest packages/mendel-forge --regenerate`, and
`FORGE_GOLDEN=update` for `test_golden.py`), and the test that lists every measurement. `make check` there names each one.

## Add a format

The same five steps with `formats/<id>/format.yml` (`declares: format`, `id`, `version`, `reads`:
the types it confirms, `extensions`, `record`, `runs: server`, `entry`) and a module with
`confirms(first)`, given the first 4 KiB, and `records(stream)`, yielding records. Its fixtures
go in `piece/fixtures/<case>/`, one folder per case, written by a `make.py` beside them so they
can be regenerated and reviewed.

## The rules every piece keeps

- **It imports only** from the allowlist in Comeni Labs' `tests/guards/test_inspector_pieces.py`:
  no network, no files, no processes. It reads only the stream it is handed.
- **It never raises**: a piece that fails is that one inspection's answer.
- **It never guesses**: below its threshold, a measure says *undetermined* and why.
- **It never decides on a file's name.**

A faster implementation in another language is welcome if it reproduces every golden report
byte for byte (`comeni-inspect`'s `PROTOCOL.md`).
