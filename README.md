# comeni-registry

The declared data [Mendel](https://github.com/comeni-project/Comeni-Labs) resolves against:
module contracts, decision rules, state vocabularies and measurement declarations.

This repository **is** a registry layer. Its root is the layer, so it can be pointed at
directly:

```bash
git clone https://github.com/comeni-project/comeni-registry
uv run mendel build --goal my-goal.yml --registry ./comeni-registry --out build/
```

Layers stack, and later ones win. A laboratory keeps its own overlay private and puts it
after this one:

```bash
uv run mendel build --goal my-goal.yml \
  --registry ./comeni-registry --registry ./lab-registry --out build/
```

## What is not true about this yet

**This is not a curated registry.** Every contract here is a test fixture that happens to be
true — enough to build and run the RNA-seq spine, hand-written, and checked against the
vendored nf-core modules by `mendel build`'s conformance stage. Nothing in it has been
validated by a laboratory for clinical use, and "curated" in Mendel means *a named human
signed off*, which has not happened for anything here.

It is published now because a registry that lives inside the tool's repository is not a
registry — it is a fixture directory with ambitions. Splitting it is what makes the
distribution model real, and doing that before there is much data is cheaper than after.

## What is in it

Every file says what it is in a `declares:` line, so **the kind is in the file and not in the
path**:

| `declares:` | What it declares |
|---|---|
| `contract` | what a module consumes, produces and is called with |
| `module` | where a tool's own source came from, at which commit, under which licence |
| `rule` | decision tables: measured data → a value or a module |
| `vocabulary` | the states each type may carry, and how it enters a pipeline |
| `measurement` | what can be measured, its kind, bounds and citation |
| `role` | the jobs a contract can do — the only thing a tier-3 rule may target |

`registry.yml` names the layer and declares nothing. It sits at the root.

## Contributing

Contracts arrive through review, not directly. A contract is a hand-written binding to a
module, and the failure mode is that it drifts from the module it describes without anything
noticing — so `mendel build` refuses to emit when a contract disagrees with its module, and
`mendel explain M0104` says why. Run it before opening a pull request.

Vocabularies are **closed**: a contract naming an undeclared state fails to load. New states
are a reviewed data change, never a code change.

See [CONTRIBUTING.md](https://github.com/comeni-project/Comeni-Labs/blob/main/CONTRIBUTING.md)
in the main repository.

## Licence

The **declarations** are [CC-BY-4.0](LICENSE). Contracts cite papers, so attribution matters.

The **tool source** under `tools/**/module/` is not ours. Each `module.yml` names the SPDX
identifier its code arrives under, and the text of each is in `LICENSES/<identifier>.txt` — one
file per licence, which is the REUSE convention, and never one notice per module. At 1,600 tools
a notice per tool is that many near-identical copies of the MIT text, in every diff, that nobody
reads.

Mendel's own source code is Apache-2.0 and lives in
[Comeni-Labs](https://github.com/comeni-project/Comeni-Labs).

## How this layer is arranged

**Every file says what it is**, in a `declares:` line — `contract`, `rule`, `vocabulary`,
`measurement` or `role` — and vocabularies and measurements carry an explicit `id:`. Nothing
reads the directory, so **the layout is free**: Mendel will load this layer however you arrange
it, including as one flat folder.

What follows is this layer's own rule, written in `registry.yml`'s `layout:` and enforced by
`mendel lint` in CI. A private layer that declares no `layout:` is held to nothing.

> **A file lives with the narrowest thing it is about.**

```
registry.yml                       this layer's account of itself
LICENSES/                          one file per licence the vendored code arrives under
tools/nf-core/star/                everything STAR, in one place
    tool.yml                       what STAR is, in words an explanation may quote
    README.md                      its page, generated from the files beside it
    types/genome.index.star.yml    shared by the subtools, so it sits at the TOOL level
    align/
        contract.yml               the binding: ports, states, roles, params
        module.yml                 where module/ came from, and under what terms
        module/                    upstream's tree, verbatim. NEVER hand-edited
    genomegenerate/
        contract.yml  module.yml  module/
profilers/comeni/profile/fastqc/   a use of a tool to measure the data; the path is the id
inspectors/                        code that measures an uploaded sample on the server
vocabulary/
    types/                         types many tools touch — fastq.reads, alignment.bam
    measurements/                  facts about data, true regardless of tool
    roles/  families/              the jobs a contract can do; the kinds of data that exist
rules/                             decisions *between* tools, belonging to neither
```

**A thing belongs at the shallowest level that owns it.** `genome.index.star` is produced by
`star/genomegenerate` and consumed by `star/align`, so it is the *tool's* and sits one level up.
A contract binds to exactly one module, so it sits in that module's directory.

**Subtool directories are required, not stylistic.** nf-core ships `star/align` and
`star/genomegenerate` as separate modules, each with its own source and its own pin, so each
needs a `module/` of its own.

**`tools/`, not `modules/`**, because `genome.index.star` is produced by one STAR module and
consumed by another — grouping per module would split it again, which is the problem this
layout was made to fix.

**`module/` is the one directory name that is not free.** Everywhere else the loader reads
`declares:` and ignores the path; a tool's source is found by the directory it sits in, because
upstream ships whatever it ships — `main.nf`, `environment.yml`, `.conda-lock/`, helper scripts
— and none of that carries a `declares:` line. Everything under a `module/` is upstream's, is
covered by the layer digest, and is never hand-edited.

**`rules/` is separate** because a rule choosing STAR over HISAT2 is about neither of them.
Filing it under `star/` would be a lie about what it decides, and this registry's whole claim is
that a decision states its own reason.

**The filename is for people.** The loader reads `declares:` and ignores it. Rename anything
you dislike; nothing breaks — except `module/`, which is read by directory (above).

## Vendoring a tool

`module/` is written by `comeni-vendor`, never by hand:

```bash
comeni-vendor add nf-core:star/align \
  --sha 6d46786420b4d7bc88eba026eb389c0c5535d120 \
  --licence MIT --registry .

comeni-vendor check --registry .              # offline: has anything been hand-edited?
comeni-vendor check --registry . --upstream   # online: does it still match the pin?
```

It pins a **commit**, never a branch: a branch moves, so a check against it answers *does this
match whatever upstream looks like today*, which is a different question from *is this still the
code we reviewed*. `excluded:` records what was deliberately not copied — nf-core ships a
`tests/` directory we do not take — so a drift check compares upstream minus what we said we
would skip, rather than reporting every module as different forever.

A module declaring `upstream: null` is a laboratory's own process, written here rather than
copied. `check` reports it `unpinned` rather than `ok`, because there is nothing to compare it
against and reporting a pass would claim a check that never ran.
