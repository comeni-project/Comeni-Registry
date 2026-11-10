# Measurers

Everything that measures data (comeni-labs#465). A measurer produces one measurement, and runs
where it says:

- on the **server**, over the first 4 MB of an upload, so a person who is not sure of a fact can
  answer with a file. Its facts are an estimate (`coverage: head`) unless the whole file fitted;
- in the **pipeline**, as a step over all the data during the run (`coverage: all`). A decision
  that needs a fact nobody knew before the build is made there, and an estimate a build used is
  confirmed there.

It measures in one of two ways:

- **`by: code`**, our own code: **codecs** unwrap bytes (`gzip`), **formats** turn bytes into
  records and confirm the file is what its name says (`fastq`), and the measurer reads records of
  one shape (`read_length`). The same code runs in both places.
- **`by: tool`**, a tool in the registry plus a parser for one of its outputs: `samtools faidx`
  and a parser that sums its `.fai`. A tool runs only in the pipeline.

A format and every `by: code` measurer that reads its record shape make an inspection. Add a
format, and every measurer of its shape works on it; add a measurer, and it works on every format
of its shape.

Each piece is a folder: its declaration (`measurer.yml`, `format.yml` or `codec.yml`) and, beside
it, `piece/` with its code, its tests and, for a format, its fixtures.

## Add a measurer of our own code

1. Make sure the measurement exists in `vocabulary/measurements/` (`declares: measurement`, an
   `id`, a `kind`, a `description` and a `cite`). If you are declaring it now, leave out
   `assertion_only`: your measurer is what measures it.
2. Create `measures/<id>/measurer.yml`:

   ```yaml
   declares: measurer
   id: gc_content            # the folder's name
   version: 1.0.0
   measures: gc_content      # the measurement it produces
   by: code
   record: sequence          # the record shape it reads
   runs: [server, pipeline]  # where it may run
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
   uv run pytest registry/measurers tests/guards/test_inspector_pieces.py
   uv run python -c "from comeni_inspect import harness; from pathlib import Path; [(c.folder / 'expected.json').write_text(harness.run_case(c) + '\n') for c in harness.cases(Path('registry'))]"
   uv run pytest tests/registry/test_inspection_conformance.py
   ```

A **new measurement** (step 1) also derives a `measurement.<id>` type. From the Comeni Labs
checkout, regenerate the profile type stub and run the ordinary checks:

```bash
uv run python tools/generate_types.py
make check
```

The generated stub is committed with the engine; runtime vocabulary validation remains derived
from the registry declarations.

## Add a format

The same five steps with `formats/<id>/format.yml` (`declares: format`, `id`, `version`, `reads`:
the types it confirms, `extensions`, `record`, `runs: server`, `entry`) and a module with
`confirms(first)`, given the first 4 KiB, and `records(stream)`, yielding records. Its fixtures
go in `piece/fixtures/<case>/`, one folder per case, written by a `make.py` beside them so they
can be regenerated and reviewed.

In its tests, **name the format**, or the helper reads FASTQ's fixtures:

```python
fact = inspect(*request_for("my_case", ["read_length"], format="<id>")).facts["read_length"]
```

## Add a measurer of a tool's output

When a tool in `tools/` already measures something, parse its output:

```yaml
declares: measurer
id: genome_length_fai
version: 1.0.0
measures: genome_length
by: tool
uses: nf-core/samtools/faidx@1.21   # the tool's contract id
output: fai                         # the output port the parser reads
entry: piece/fai.py
runs: [pipeline]                    # a tool never runs on the server
```

`piece/fai.py` defines `parse(stream, decided)`, given the output file as a byte stream, and
returns `Value(...)` or `Undetermined(...)` as a measurer's `result()` does. The pipeline runs the
tool as an ordinary step and the parser after it. Test the parser against a recorded output.

## The rules every piece keeps

- **It imports only** from the allowlist in Comeni Labs' `tests/guards/test_inspector_pieces.py`:
  no network, no files, no processes. It reads only the stream it is handed.
- **It never raises**: a piece that fails is that one inspection's answer.
- **It never guesses**: below its threshold, a measure says *undetermined* and why.
- **It never decides on a file's name.**

A faster implementation in another language is welcome if it reproduces every golden report
byte for byte (`comeni-inspect`'s `PROTOCOL.md`).
