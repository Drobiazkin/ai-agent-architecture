// Book/course typesetter: Markdown -> self-contained book-styled HTML.
// Pipeline: extract mermaid (batch-render via mermaid-cli, one Chromium) ->
// custom footnote handling (term-notes stay at chapter end) -> markdown-it ->
// inline PNG as base64 -> book CSS + sticky TOC + print-to-PDF styles.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import MarkdownIt from 'markdown-it';
import anchor from 'markdown-it-anchor';
import katexPlugin from '@vscode/markdown-it-katex';

const [, , SRC, OUT, TITLE, LANG] = process.argv;
if (!SRC || !OUT) { console.error('usage: build.js <src.md> <out.html> [title]'); process.exit(1); }
const FILES_DIR = path.dirname(path.resolve(SRC)); // manuscript dir (images/ resolved relative to it)
const IMG_DIR = path.join(FILES_DIR, 'images');
const TMP = path.dirname(new URL(import.meta.url).pathname);

let md_src = fs.readFileSync(SRC, 'utf8');

// ---------- 1. Extract mermaid blocks (plain + blockquoted) ----------
const lines = md_src.split('\n');
const figs = []; // {body}
const outLines = [];
let i = 0;
while (i < lines.length) {
  const l = lines[i];
  const bq = /^>\s?/.test(l);
  const stripped = l.replace(/^>\s?/, '');
  if (stripped.trim() === '```mermaid') {
    const body = [];
    i++;
    while (i < lines.length) {
      const s = lines[i].replace(/^>\s?/, '');
      if (s.trim() === '```') { i++; break; }
      body.push(s);
      i++;
    }
    const id = figs.length;
    figs.push(body.join('\n'));
    // placeholder on its own line, outside any blockquote
    outLines.push('');
    outLines.push(`@@FIG:${id}@@`);
    outLines.push('');
    continue;
  }
  outLines.push(l);
  i++;
}
md_src = outLines.join('\n');
console.error(`mermaid blocks extracted: ${figs.length}`);

// ---------- 2. Batch-render mermaid to SVG (single mermaid-cli run) ----------
const svgs = [];
if (figs.length) {
  const batchDir = path.join(TMP, 'mmd_batch');
  fs.rmSync(batchDir, { recursive: true, force: true });
  fs.mkdirSync(batchDir, { recursive: true });
  // one markdown file with all diagrams -> mermaid-cli emits <out>-1.svg ...
  const batchMd = figs.map(b => '```mermaid\n' + b + '\n```').join('\n\n---\n\n');
  const inMd = path.join(batchDir, 'in.md');
  const outMd = path.join(batchDir, 'out.md');
  fs.writeFileSync(inMd, batchMd);
  const cfg = path.join(batchDir, 'cfg.json');
  fs.writeFileSync(cfg, JSON.stringify({ theme: 'neutral', flowchart: { htmlLabels: true }, fontFamily: 'ui-sans-serif, system-ui, sans-serif' }));
  const cli = path.join(TMP, 'node_modules/@mermaid-js/mermaid-cli/src/cli.js');
  execFileSync('node', [cli, '-i', inMd, '-o', outMd, '-e', 'svg', '-c', cfg, '-b', 'transparent'], { stdio: 'inherit' });
  for (let k = 0; k < figs.length; k++) {
    const p = path.join(batchDir, `out-${k + 1}.svg`);
    let svg = fs.readFileSync(p, 'utf8');
    svg = svg.replace(/<\?xml[^>]*\?>/, '').replace(/<!DOCTYPE[^>]*>/i, '').trim();
    svgs.push(svg);
  }
  console.error(`mermaid SVGs rendered: ${svgs.length}`);
}

// ---------- 3. Custom footnotes: term-notes stay in place ----------
const mdInline = new MarkdownIt({ html: true, typographer: true });
// definitions: consecutive lines "[^t-slug]: body" -> term-note panel
const flines = md_src.split('\n');
const res = [];
let j = 0;
while (j < flines.length) {
  const m = /^\[\^(t-[\w-]+)\]:\s*(.*)$/.exec(flines[j]);
  if (m) {
    const items = [];
    while (j < flines.length) {
      const mm = /^\[\^(t-[\w-]+)\]:\s*(.*)$/.exec(flines[j]);
      if (!mm) break;
      const slug = mm[1], body = mm[2];
      const html = mdInline.renderInline(body);
      items.push(`<p class="termnote" id="def-${slug}"><a class="fnback" href="#ref-${slug}" title="к месту в тексте">↩</a> ${html}</p>`);
      j++;
    }
    res.push('<div class="termnotes">' + items.join('\n') + '</div>');
    continue;
  }
  res.push(flines[j]);
  j++;
}
md_src = res.join('\n');
// inline refs: [^t-slug]  ->  superscript anchor
let refN = 0;
md_src = md_src.replace(/\[\^(t-[\w-]+)\](?!:)/g, (_, slug) => {
  refN++;
  return `<sup class="fnref" id="ref-${slug}"><a href="#def-${slug}" title="определение в конце главы">°</a></sup>`;
});
console.error(`inline term-refs linked: ${refN}`);

// ---------- 4. markdown-it main render ----------
const md = new MarkdownIt({ html: true, linkify: true, typographer: true, breaks: false });
const toc = [];
md.use(anchor, {
  level: [1, 2],
  slugify: s => 'h-' + Buffer.from(s).toString('hex').slice(0, 16) + '-' + (toc.length),
  callback: (token, info) => { toc.push({ level: token.tag === 'h1' ? 1 : 2, text: info.title, id: info.slug }); },
  // Значок-якорь ПОСЛЕ текста заголовка. Прежний headerLink оборачивал весь текст в .header-anchor,
  // который book.css прячет (opacity:0 до ховера — правило писалось под значок) -> заголовки
  // пропадали из вёрстки и из PDF-outline (Chrome не включает невидимые заголовки в закладки).
  permalink: anchor.permalink.ariaHidden({ placement: 'after', symbol: '°' }),
});
// Math: $inline$ and $$display$$ via KaTeX. The plugin follows the CommonMark
// math rule ($ immediately before a digit does NOT open math), so prose money
// like "$3000/mo" and "$2 per million" is left untouched — only real formulas
// (α/r, E_seq, 10^9 written as $10^9$) render. throwOnError:false keeps a bad
// formula visible as source instead of aborting the whole build.
md.use(katexPlugin.default || katexPlugin, { throwOnError: false, strict: false });
let html = md.render(md_src);

// ---------- 4b. Классификация заголовков частей/глав для печати ----------
// Разделитель части (Часть/Part/Приложения/Appendices) открывает новую страницу;
// первая глава сразу за ним делит эту же страницу (chapter-after-part => без форс-разрыва),
// чтобы страница-открывашка части не оставалась почти пустой.
{
  let partSeen = false;
  html = html.replace(/<h1 ([^>]*)>([\s\S]*?)<\/h1>/g, (m, attrs, inner) => {
    const text = inner.replace(/<[^>]*>/g, '').trim();
    let cls = '';
    if (/^(Часть|Part|Приложения|Appendices)(?=\s|$)/.test(text)) { cls = 'part-divider'; partSeen = true; }
    else if (/^(Глава|Chapter|Приложение|Appendix)\s/.test(text)) { cls = partSeen ? 'chapter chapter-after-part' : 'chapter'; partSeen = false; }
    return cls ? `<h1 class="${cls}" ${attrs}>${inner}</h1>` : m;
  });
}

// ---------- 5. Re-insert mermaid figures ----------
html = html.replace(/<p>@@FIG:(\d+)@@<\/p>/g, (_, n) => `<figure class="mermaid">${svgs[+n] || '[diagram]'}</figure>`);
html = html.replace(/@@FIG:(\d+)@@/g, (_, n) => `<figure class="mermaid">${svgs[+n] || '[diagram]'}</figure>`);

// ---------- 6. Inline PNGs as base64 ----------
let imgN = 0;
html = html.replace(/src="images\/([^"]+)"/g, (m, fn) => {
  const p = path.join(IMG_DIR, fn);
  if (!fs.existsSync(p)) return m;
  const b64 = fs.readFileSync(p).toString('base64');
  imgN++;
  return `src="data:image/png;base64,${b64}"`;
});
console.error(`PNGs inlined: ${imgN}`);

// ---------- 7. Build sticky TOC ----------
const tocHtml = toc.map(t =>
  `<a class="toc-l${t.level}" href="#${t.id}">${md.utils.escapeHtml(t.text)}</a>`).join('\n');

// ---------- 8. Assemble ----------
const title = TITLE || 'Book';
const lang = (LANG || 'en').toLowerCase();
const tocLabel = lang === 'ru' ? 'Содержание' : 'Contents';
const css = fs.readFileSync(path.join(TMP, 'book.css'), 'utf8');

// KaTeX stylesheet, made self-contained: its @font-face rules point at
// fonts/KaTeX_*.woff2 by relative URL, which cannot resolve inside a single
// inlined HTML file. Rewrite each woff2 reference to a base64 data: URI (woff2
// alone covers every target browser and the Chromium used for PDF), and drop
// the woff/ttf fallbacks so we embed one format, not three.
let katexCss = '';
{
  const kdir = path.join(TMP, 'node_modules', 'katex', 'dist');
  const raw = fs.readFileSync(path.join(kdir, 'katex.min.css'), 'utf8');
  const cache = new Map();
  katexCss = raw.replace(/src:[^;]+;/g, (decl) => {
    const m = decl.match(/url\(([^)]*?\.woff2)\)/);
    if (!m) return decl; // no woff2 in this @font-face -> leave as is
    const rel = m[1].replace(/^["']|["']$/g, '');
    const fp = path.join(kdir, rel);
    if (!fs.existsSync(fp)) return decl;
    let b64 = cache.get(fp);
    if (!b64) { b64 = fs.readFileSync(fp).toString('base64'); cache.set(fp, b64); }
    return `src:url(data:font/woff2;base64,${b64}) format("woff2");`;
  });
  console.error(`KaTeX fonts embedded: ${new Set([...raw.matchAll(/[\w-]+\.woff2/g)].map(x => x[0])).size}`);
}
// Third-party notice for the assets inlined above. MIT requires the copyright and
// permission notice to travel with every copy, and katex.min.css carries no banner of
// its own. It has to be a visible colophon rather than an HTML comment: Chromium drops
// comments when printing, and the PDF embeds the fonts, so a comment would leave the
// PDF shipping MIT-licensed font data with no attribution at all.
const katexNotice = fs.readFileSync(path.join(TMP, 'third_party', 'KATEX-LICENSE'), 'utf8').trim();
const escHtml = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const colophon = (() => {
  const ru = lang === 'ru';
  const head = ru ? 'Выходные сведения' : 'Colophon';
  const intro = ru
    ? 'Свёрстано с KaTeX (https://katex.org): его таблица стилей и веб-шрифты встроены в этот файл. Они остаются под собственной лицензией и не перелицензируются.'
    : 'Typeset with KaTeX (https://katex.org): its stylesheet and web fonts are embedded in this file. They remain under their own license and are not relicensed.';
  const own = ru
    ? 'Само произведение — проза, рисунки и диаграммы — лицензировано под CC BY-SA 4.0; примеры кода — под MIT. См. NOTICE в репозитории.'
    : "This work itself — prose, figures, and diagrams — is licensed under CC BY-SA 4.0; its code samples under the MIT License. See the NOTICE file at https://github.com/Drobiazkin/ai-agent-architecture.";
  return `<footer id="colophon"><h2>${head}</h2><p>${intro}</p><pre>${escHtml(katexNotice)}</pre><p>${own}</p></footer>`;
})();

const doc = `<!doctype html>
<html lang="${lang}"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<style>${katexCss}</style>
<style>${css}</style>
<style>#colophon{margin:5rem 0 0;padding:1.5rem 0 0;border-top:1px solid rgba(128,128,128,.35);font-size:.75rem;line-height:1.55;opacity:.72}#colophon h2{font-size:.9rem;margin:0 0 .6rem;border:0;padding:0}#colophon pre{white-space:pre-wrap;font-size:.68rem;line-height:1.45;margin:.7rem 0;background:none;border:0;padding:0}@media print{#colophon{page-break-before:always}}</style>
</head><body>
<button id="toc-toggle" aria-label="Table of contents">☰</button>
<nav id="toc"><div class="toc-head">${tocLabel}</div>${tocHtml}</nav>
<main id="content">${html}${colophon}</main>
<script>
const tg=document.getElementById('toc-toggle'),nv=document.getElementById('toc');
tg.addEventListener('click',()=>document.body.classList.toggle('toc-open'));
nv.addEventListener('click',e=>{if(e.target.tagName==='A')document.body.classList.remove('toc-open');});
</script>
</body></html>`;
fs.writeFileSync(OUT, doc);
const kb = (Buffer.byteLength(doc) / 1024).toFixed(0);
console.error(`WROTE ${OUT} (${kb} KB, ${toc.length} TOC entries)`);
