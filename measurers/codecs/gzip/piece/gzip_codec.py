"""gzip: open a byte stream as a gzip stream. The runner caps what comes out and treats a stream
cut mid-way (every head is) as its end. The stream is the upload's head on the server and the
whole file in the pipeline, so nothing here reads it all into memory."""

import gzip
from typing import BinaryIO


def open(stream: BinaryIO) -> gzip.GzipFile:
    return gzip.GzipFile(fileobj=stream)
