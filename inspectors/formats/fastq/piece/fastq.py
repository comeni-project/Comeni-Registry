"""FASTQ: four lines a record, confirmed by its content rather than its name."""

import re
from collections.abc import Iterator
from typing import BinaryIO

from comeni_inspect.records import SequenceRecord

_SEQUENCE = re.compile(rb"[A-Za-z.*-]+")


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
    """Four lines at a time. A record cut by the head (fewer than four lines, or a quality line
    shorter than its sequence) ends the stream quietly: a head is always cut somewhere."""
    while True:
        lines = [stream.readline() for _ in range(4)]
        if not lines[3].endswith(b"\n"):
            return
        head, sequence, _, quality = (line.rstrip(b"\r\n") for line in lines)
        if not head.startswith(b"@") or len(quality) != len(sequence):
            return
        name = head[1:].split(b" ", 1)[0].decode(errors="replace")
        yield SequenceRecord(name=name, sequence=sequence, quality=quality)
