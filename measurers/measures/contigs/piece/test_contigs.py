"""Contigs: counted over the assembly; none is undetermined."""

from comeni_inspect.run import inspect
from support_pieces import request_for


def _fact(case):
    return inspect(*request_for(case, ["contigs"], format="fasta")).facts["contigs"]


def test_every_record_is_counted():
    assert _fact("multiline").value == 3

