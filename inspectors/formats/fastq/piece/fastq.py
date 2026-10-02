"""FASTQ: four lines a record, confirmed by its content rather than its name."""

from collections.abc import Iterator
from typing import BinaryIO

from comeni_inspect.records import SequenceRecord


def confirms(first: bytes) -> bool:
    """`@name`, a sequence line, a `+` line, and a quality line the sequence's length."""
    lines = first.replace(b"\r\n", b"\n").split(b"\n")
    return (
        len(lines) >= 4
        and lines[0].startswith(b"@")
        and lines[2].startswith(b"+")
        and len(lines[1]) == len(lines[3]) > 0
    )


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
