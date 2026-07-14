# Contributing

Corrections are the most valuable thing you can send. An error found here is an error a thousand readers never hit.

## The bar: the source is the only oracle

This book's central discipline applies to its own text. A claim about how something *behaves* — a mechanism, a condition, a number, an API's semantics — outranks any intuition about how it *should* behave, including the author's.

So, concretely:

- **A claim about mechanism** needs a primary reference: the paper, the specification, the vendor's own documentation, or the source code. A blog post restating a paper is not the paper.
- **A number** needs somewhere it can be checked. If a figure is a genuine estimate with no traceable origin, the book says so out loud and hedges it — that is a legitimate move, and "this number is unsourced" is itself a valid issue to open.
- **Naming a source is not the same as verifying it.** If you report that a cited paper does not actually contain the claim attributed to it, that is a top-priority issue.
- **Disagreement is welcome; assertion is not.** "This is wrong" plus a primary source beats a long argument from first principles every time.

## What is especially welcome

| | |
|---|---|
| **Factual errors** | A formula with a missing term, a misattributed result, a number that drifted from its source. The highest-value reports. |
| **Rot** | The field moves. A section that was true in 2025 and is now false is a defect — say which part and since when. |
| **Broken cross-references** | A `§N.M` pointing at the wrong place, or sending the reader somewhere that does not contain what was promised. Topical adjacency does not count as a valid reference. |
| **Translation issues** | Passages that read as translated rather than written, or where the English lost a distinction the original made. |
| **Course defects** | A module whose instructions cannot be followed literally, or a Definition of Done that cannot be met with what the module teaches. |

## What is out of scope

- Rewrites that trade mechanism for accessibility. The book is deliberately dense and assumes a working distributed-systems engineer.
- Vendor or product promotion.
- Style preferences without a correctness argument.
- New chapters proposed without discussion — open an issue first.

## How

1. **Open an issue** describing the defect, with `file:line` and your source. For anything larger than a typo, do this before writing a patch — it saves your time more than the author's.
2. **Pull requests** should be one logical fix each. Keep the prose in the book's voice; match the surrounding text's density and conventions.
3. **Build before submitting**, if your change touches structure — see [`build/README.md`](build/README.md).

## Licensing of contributions

By contributing you agree that your contribution is licensed under the same terms as the material it modifies: [CC BY-SA 4.0](LICENSE) for prose, figures, and diagrams; [MIT](LICENSE-CODE) for code samples and `tools/`. You keep the copyright on what you wrote.

Substantive contributions are credited by name unless you ask otherwise.
