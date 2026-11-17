"""FASTA: a `>name` line, then the sequence over one or more lines, confirmed by its content."""

import re
from collections.abc import Iterator
from typing import BinaryIO

from comeni_inspect.records import Malformed, SequenceRecord

_SEQUENCE = re.compile(rb"[A-Za-z*-]+")
_NAME_ENDS = re.compile(rb"[ \t]")


def confirms(first: bytes) -> bool:
    """`>name`, then a line of sequence letters. **The window may end inside the first line of
    sequence**: what it shows is checked, what it cut off is not held against the file. A FASTQ
    starts with `@` and is refused."""
    *lines, partial = first.replace(b"\r\n", b"\n").split(b"\n")
    lines = [line for line in lines if line]
    if not lines or not lines[0].startswith(b">"):
        return False
    shown = lines[1] if len(lines) > 1 else partial
    return bool(_SEQUENCE.fullmatch(shown)) if shown else len(lines) == 1


def records(stream: BinaryIO) -> Iterator[SequenceRecord]:
    """One record per `>` line, its sequence lines joined. A line of sequence before any `>`, or
    with other than letters, is **not a cut**: it raises `Malformed` with the record's number.
    The name stops at the first space or tab. A contig has no quality."""
    number, name, parts = 0, None, []
    for raw in stream:
        line = raw.rstrip(b"\r\n")
        if line.startswith(b">"):
            if name is not None:
                yield SequenceRecord(name=name, sequence=b"".join(parts), quality=None)
            number += 1
            name = _NAME_ENDS.split(line[1:], maxsplit=1)[0].decode(errors="replace")
            parts = []
        elif line:
            if name is None or not _SEQUENCE.fullmatch(line):
                raise Malformed(f"record {max(number, 1)}: a sequence line holds other than letters"
                                if name is not None else "record 1: sequence before any > line")
            parts.append(line)
    if name is not None:
        yield SequenceRecord(name=name, sequence=b"".join(parts), quality=None)
