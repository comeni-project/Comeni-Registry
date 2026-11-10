"""The pieces' test helper reads the fixtures of the format it is given, not always FASTQ's."""

import pytest
from support_pieces import request_for


def test_a_request_names_the_format_whose_fixtures_it_reads():
    request = request_for("single_150", ["read_length"], format="fastq")
    assert request is not None


def test_a_format_with_no_such_fixture_is_said_not_read_as_fastq():
    with pytest.raises(FileNotFoundError, match="nosuchformat"):
        request_for("single_150", ["read_length"], format="nosuchformat")
