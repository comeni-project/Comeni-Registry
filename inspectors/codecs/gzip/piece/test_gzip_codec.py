"""The gzip codec opens what gzip wrote."""

import gzip

import gzip_codec


def test_it_opens_a_gzip_stream():
    assert gzip_codec.open(gzip.compress(b"@r\nA\n+\nI\n")).read() == b"@r\nA\n+\nI\n"
