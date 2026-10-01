# Contributing to the Comeni registry

This repository is **data**. A contract, a rule, a measurement, a type — each is a YAML file
with a citation, and adding one needs no Python.

The engine that reads this data lives in
[`comeni-project/Comeni-Labs`](https://github.com/comeni-project/Comeni-Labs), which mounts this
repository as a git submodule.

## Where a new file goes

**Wherever it reads best.** Every declared file opens with a `declares:` line naming what it is,
and the loader reads that line rather than the path — so there is no directory you have to find.

```yaml
declares: contract
id: nf-core/salmon/quant@1.10.3
```

The convention this layer uses, and a good default to copy:

| | |
|---|---|
| `tools/<namespace>/<tool>/` | what the tool is (`tool.yml`), its page, and one folder per subtool |
| `tools/<namespace>/<tool>/types/` | a type only that tool produces |
| `profilers/<id>/` | a use of a tool to measure the data |
| `vocabulary/types/` | types more than one tool touches |
| `vocabulary/measurements/` | measurements — `declares: measurement` **and** an `id:` |
| `vocabulary/roles/`, `vocabulary/families/` | the roles a contract may fill; the families of types |
| `rules/<name>.rule.yml` | tier-3 decision tables |

**The path is the id**: the contract `nf-core/samtools/sort@1.21.0` lives in
`tools/nf-core/samtools/sort/`. `mendel lint` refuses a file that is not where its id says.

Copy the nearest existing file. If you forget the `declares:` line the loader says `MD0010`; if a
type or measurement forgets its `id:`, `MD0012`. Run `mendel explain MD0010` for the long form.

## Each tool's `README.md` is generated — do not edit it

One page per tool, written into that tool's own folder, rendered from the files above. CI fails if a page disagrees with the data, so
a hand edit is refused rather than silently overwritten.

Regenerating needs the engine installed:

```bash
uv tool install "mendel-compiler @ git+https://github.com/comeni-project/Comeni-Labs@main#subdirectory=packages/mendel-compiler"
mendel docs --registry . --in-place
```

**Stated plainly: authoring registry data needs no Python, but regenerating a page does.** CI
regenerating on your behalf was considered and rejected — a bot commit pushed into a pull request
means the diff a reviewer approved is not the diff that merges, and the reviewability of the
generated page is the entire argument for committing it.

## What CI checks, and what it does not

**Checked:** the layer loads. That is every `MD0001`–`MD0012` refusal, closed vocabularies (a
contract naming an undeclared state fails), rule validation against the parameters contracts
actually declare, and role coverage. Plus every tool's page matching the data.

**Also checked, and it was not before Plan 5A:** whether a contract agrees with its module.
`MD0104`, `MD0105` and container drift compare a contract against a `main.nf`, and that file now
lives in this repository — under `tools/<org>/<tool>/module/`, beside the contract that is a
binding for it.

That is the whole point of the move. The two used to be in different repositories on different
release cadences, so **a contract naming a process no module defines would merge here** and be
caught, if at all, in the Comeni-Labs pull request that bumped the submodule pointer. The check
that exists to catch a contract drifting from its module was comparing two things nothing kept
in step.

**`comeni-vendor check` also runs**, so a hand-edited `module/` fails CI. That directory is a
verbatim copy of somebody else's work and is replaced wholesale by `comeni-vendor add`; anything
you write into it is lost on the next re-vendor and is a false statement about upstream until
then.

## Versions and tags

This layer versions independently of the engine and is tagged `vX.Y.Z`. A `pipeline.yml` pins a
layer by content digest, so **moving a file moves the digest** — a rename is a real change to
every artifact built against it, not a tidy-up.

## Threat model — read this before adding a `--registry`

**`--registry X` used to mean *parse this person's YAML*. It now means *execute this person's
Groovy*.** A layer carries `main.nf`, and Nextflow runs it.

That is not a reason to reverse the decision — it is exactly nf-core's property, and a pipeline
is code. What it changes is that **signed tags stop being a nicety**. `docs/design/federation.md`
§3.4 already specifies tag signature plus a content digest, and that verification is now the only
thing standing between a third-party overlay and arbitrary execution on your cluster. It is a
prerequisite for publishing an overlay, not a later refinement.

**No sandbox is invented, and none is claimed.** Nextflow runs containers; the trust boundary is
the container runtime. A half-measure that looked like isolation would be worse than a sentence
that tells the truth.

## Licence

The **declarations** are **CC-BY-4.0** (`LICENSE`). Contracts and rules cite papers, and
attribution is the currency of the field.

The **tool source** under `tools/**/module/` is not ours. Each `module.yml` names the SPDX
identifier its code arrives under and `LICENSES/<identifier>.txt` carries the text — one file per
licence, the REUSE convention, never one notice per module.
