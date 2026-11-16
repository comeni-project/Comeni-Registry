"""N50: the length at which the longest contigs hold half the assembly."""

from comeni_inspect.run import inspect
from support_pieces import request_for

import n50


def _fact(case):
    return inspect(*request_for(case, ["n50"], format="fasta")).facts["n50"]


def test_the_longest_contig_holding_half_is_the_n50():
    assert _fact("multiline").value == 30  # 30 of 51 bases is past half
    assert _fact("one_line").value == 20


def test_a_contig_that_reaches_half_exactly_is_the_n50():
    folded = n50.Accumulator({"min_records": 1}, ["a.fna"])
    for length in (10, 6, 4):
        folded.add([type("R", (), {"sequence": b"A" * length})()])
    assert folded.result().value == 10  # 10 of 20 bases is half

