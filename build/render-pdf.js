// HTML -> PDF via the Chromium that mermaid-cli already installed (puppeteer).
import puppeteer from 'puppeteer';
import path from 'node:path';
const [, , IN, OUT] = process.argv;
const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
const page = await browser.newPage();
await page.goto('file://' + path.resolve(IN), { waitUntil: 'networkidle0', timeout: 120000 });
await page.pdf({
  path: OUT, format: 'A4', printBackground: true, preferCSSPageSize: false,
  outline: true, tagged: true,   // дерево закладок в PDF-ридере из h1/h2 (главы и разделы с их номерами)
  margin: { top: '18mm', bottom: '20mm', left: '16mm', right: '16mm' },
  displayHeaderFooter: true,
  headerTemplate: '<span></span>',
  footerTemplate: '<div style="width:100%;font:9px ui-sans-serif,system-ui;color:#999;text-align:center;padding-top:2px"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
});
await browser.close();
console.error('PDF written: ' + OUT);
