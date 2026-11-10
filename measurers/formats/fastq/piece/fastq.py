"""FASTQ: four lines a record, confirmed by its content rather than its name."""

import re
from collections.abc import Iterator
from typing import BinaryIO

from comeni_inspect.records import Malformed, SequenceRecord

_SEQUENCE = re.compile(rb"[A-Za-z.*-]+")
_NAME_ENDS = re.compile(rb"[ \t]")


def confirms(first: bytes) -> bool:
    """`@name`, a sequence line of letters, a `+` line, and a quality line the sequence's length.

    **The window may end inside the first record**: a 10 kb long read does not fit four lines
    in 4 KiB. What the window shows is checked; what it cut off is not held against the file.
    """
    *lines, partial = first.replace(b"\r\n", b"\n").split(b"\n")
    if not lines or not lines[0].startswith(b"@"):
        return False
    if len(lines) == 1:
        return bool(_SEQUENCE.fullmatch(partial))
    sequence = lines[1]
    if not _SEQUENCE.fullmatch(sequence):
        return False
    if len(lines) == 2:
        return partial == b"" or partial.startswith(b"+")
    if not lines[2].startswith(b"+"):
        return False
    quality = lines[3] if len(lines) >= 4 else partial
    complete = len(lines) >= 4
    return len(quality) == len(sequence) if complete else len(quality) <= len(sequence)


def records(stream: BinaryIO) -> Iterator[SequenceRecord]:
    """Four lines at a time. A record cut by the head (its fourth line unfinished) ends the
    stream quietly: a head is always cut somewhere. **A whole record that is wrong is not a
    cut**, and raises `Malformed` with its number, so the facts say where reading stopped
    (issue 224). The name stops at the first space or tab."""
    number = 0
    while True:
        lines = [stream.readline() for _ in range(4)]
        if not lines[3].endswith(b"\n"):
            return
        number += 1
        head, sequence, _, quality = (line.rstrip(b"\r\n") for line in lines)
        if not head.startswith(b"@"):
            raise Malformed(f"record {number}: it does not start with @")
        if len(quality) != len(sequence):
            raise Malformed(f"record {number}: its quality is not its sequence's length")
        name = _NAME_ENDS.split(head[1:], maxsplit=1)[0].decode(errors="replace")
        yield SequenceRecord(name=name, sequence=sequence, quality=quality)
