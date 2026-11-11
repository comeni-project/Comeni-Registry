"""The genome_length parser over a FASTA index."""

import io

import fai


def test_it_sums_the_lengths():
    stream = io.BytesIO(b"chr1\t1000\t6\t60\t61\nchr2\t29903\t1030\t60\t61\n")
    outcome = fai.parse(stream, {})
    assert outcome.value == 30903 and outcome.evidence == {"sequences": 2}


def test_sars_cov_2():
    outcome = fai.parse(io.BytesIO(b"MN908947.3\t29903\t12\t70\t71\n"), {})
    assert outcome.value == 29903


def test_an_empty_index_is_undetermined():
    outcome = fai.parse(io.BytesIO(b""), {})
    assert outcome.reason == "the index lists no sequences"


def test_a_malformed_line_is_undetermined_and_says_which():
    outcome = fai.parse(io.BytesIO(b"chr1\t1000\t6\t60\t61\nnot a fai line\n"), {})
    assert outcome.reason == "line 2 is not a .fai line"
