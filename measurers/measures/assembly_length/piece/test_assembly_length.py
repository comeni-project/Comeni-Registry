"""Assembly length: every contig's bases, summed."""

from comeni_inspect.run import inspect
from support_pieces import request_for


def _fact(case):
    return inspect(*request_for(case, ["assembly_length"], format="fasta")).facts[
        "assembly_length"]


def test_the_bases_of_every_contig_are_summed():
    assert _fact("multiline").value == 51
    assert _fact("gzipped").value == 40

