"""Genome length: the sum of a FASTA index's second column (`samtools faidx`)."""

from comeni_inspect.outcome import Undetermined, Value


def parse(stream, decided):
    total = sequences = 0
    for number, line in enumerate(stream, start=1):
        fields = line.rstrip(b"\r\n").split(b"\t")
        if not line.strip():
            continue
        if len(fields) < 2 or not fields[1].isdigit():
            return Undetermined(reason=f"line {number} is not a .fai line",
                                evidence={"sequences": sequences})
        total += int(fields[1])
        sequences += 1
    if not sequences:
        return Undetermined(reason="the index lists no sequences", evidence={"sequences": 0})
    return Value(value=total, evidence={"sequences": sequences})
