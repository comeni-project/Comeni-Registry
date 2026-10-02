"""Quality encoding: Phred+33 or Phred+64, decided only by a character only one allows."""

from comeni_inspect.run import inspect
from support_pieces import request_for


def _enc(case):
    return inspect(*request_for(case, ["quality_encoding"])).facts["quality_encoding"]


def test_modern_is_phred33():
    assert _enc("single_150").value == "phred33"


def test_old_illumina_is_phred64():
    assert _enc("phred64").value == "phred64"


def test_overlap_is_undetermined():
    assert _enc("ambiguous_quality").undetermined == "characters fit both Phred+33 and Phred+64"


def test_twelve_reads_are_not_enough():
    assert _enc("few").undetermined == "only 12 reads"
