STAR's index build asks for memory from the genome's length (about 10 bytes a base, at least 2 GB), by a rule in `rules/star_index.yml`, instead of the 72 GB its `process_high` label asks for. Needs the engine that lets `memory` name its unit (comeni-labs#509).
STAR's alignment asks for memory from the same rule, reading the genome's length on the index's `meta2` (comeni-labs#601).
