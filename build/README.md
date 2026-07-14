# Typesetting the book and the course

Pipeline: `Markdown → self-contained HTML → PDF`. No LaTeX, no pandoc — Node only.

## What it does
- `build.js` — renders an `.md` file into a single self-contained `.html`:
  - all `mermaid` blocks (including those inside blockquote pattern cards) are batch-rendered to inline SVG in one Chromium run;
  - terminology footnotes `[^t-slug]` stay **at the end of their chapter** (the "In the Margins" panel), with superscript anchors linking both ways;
  - PNGs from `images/` are embedded as base64 (the file ships as a single artifact);
  - book CSS (`book.css`): typography, sticky table of contents, pattern cards, print styles.
- `render-pdf.js` — prints the finished HTML to PDF via the same Chromium (A4, page-numbered footer, page break before each chapter).

## Setup (once)
```sh
cd build
npm install          # markdown-it + plugins + @mermaid-js/mermaid-cli (pulls Chromium, ~400 MB)
```

## Building

The book lives as one file per chapter in `book/`. Concatenate before building:

```sh
cat book/front-matter.md book/toc.md book/glossary.md book/[0-9]*.md book/appendix-*.md > book/.single.md
node build/build.js book/.single.md ai-agent-architecture-book.html "The Architecture of AI Agents and LLM Systems"
node build/render-pdf.js ai-agent-architecture-book.html ai-agent-architecture-book.pdf
rm book/.single.md
```

Two things about that first line are load-bearing:

- **Concatenate inside `book/`, not into `/tmp`.** `build.js` resolves `images/` *relative to the source file's directory* (`build.js:13`). A source file in `/tmp` makes it look for `/tmp/images/`, find nothing, and emit a book with **every figure silently missing** — the only symptom is `PNGs inlined: 0` in the log. `book/.single.md` sits next to `book/images/`, so the figures resolve.
- **The front matter is deliberately not numbered.** The `book/[0-9]*.md` glob must match chapters only; a `00-` prefix would make the glob re-match it and render the whole preface a second time, after the glossary.

Sanity-check the log before shipping: `mermaid SVGs rendered: 55`, `inline term-refs linked: 52`, `PNGs inlined: 19`. A zero in any of those means something silently dropped out.

The course is built the same way, from its own overview plus modules:

```sh
cat course/README.md course/module-*.md course/python-primer.md > /tmp/course-single.md
node build.js /tmp/course-single.md ../ai-agent-practice-course.html "Practicum: AI Agents by Hand"
node render-pdf.js ../ai-agent-practice-course.html ../ai-agent-practice-course.pdf
```

## Russian edition (`ru/`)

The Russian book and course live in `ru/`. Build them the same way, passing `ru` as the fourth
argument so the chrome (`<html lang>`, the "Contents" label) comes out Russian:

```sh
node build/build.js ru/ai-agent-architecture-book-v2.md ru/ai-agent-architecture-book-v2.html "Архитектура AI-агентов и LLM-систем" ru
node build/render-pdf.js ru/ai-agent-architecture-book-v2.html ru/ai-agent-architecture-book-v2.pdf
cat ru/ai-agent-practice-course.md ru/course/module-*.md ru/course/python-primer.md > /tmp/ru-course.md
node build/build.js /tmp/ru-course.md ru/ai-agent-practice-course.html "Практикум: AI-агенты руками" ru
node build/render-pdf.js ru/ai-agent-practice-course.html ru/ai-agent-practice-course.pdf
```

The RU book is a single Markdown file (not split per chapter); its figures resolve from `ru/images/`.

A PDF can also be produced without `render-pdf.js`: open the `.html` in a browser → Print → Save as PDF (print CSS is already set up — chapters start on a new page, the sticky TOC is hidden).

## Transient (not for VCS)
`node_modules/`, `mmd_batch/` — generated; safe to delete.
