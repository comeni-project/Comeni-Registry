"""Read length: the modal length, decided only when enough reads agree on it."""

from comeni_inspect.run import inspect
from support_pieces import request_for


def _fact(case):
    return inspect(*request_for(case, ["read_length"])).facts["read_length"]


def test_uniform_150_is_decided():
    fact = _fact("single_150")
    assert fact.value == 150 and fact.evidence["share"] == 1.0
    assert fact.evidence["records"] == 2000


def test_a_pair_counts_the_reads_of_both_files():
    assert _fact("pair_150").evidence["records"] == 4000


def test_trimmed_is_undetermined_with_the_range():
    assert _fact("trimmed").undetermined.startswith("lengths vary: 100–151")


def test_twelve_reads_are_not_enough():
    assert _fact("few").undetermined == "only 12 reads"
