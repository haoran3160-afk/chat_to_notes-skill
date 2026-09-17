"""Print a user-approved, self-contained notes HTML with local Chrome/Edge."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import base64
import json
import re
from artifact_contract import STYLES, inspect_html, manifest_from, sha
from browser_session import BrowserSession


READY = r'''(async()=>{
  await Promise.race([Promise.all([document.fonts.ready,...[...document.images].map(i=>i.decode())]),
    new Promise((_,reject)=>setTimeout(()=>reject(Error('Fonts/images did not load')),20000))]);
  if(document.querySelector('merror'))throw Error('MathML merror');
  const counts={math:document.querySelectorAll('math').length,images:document.images.length,
    svg:document.querySelectorAll('svg').length,answers:document.querySelectorAll('details.answer').length};
  const headings=[...document.querySelectorAll('h2[id],h3[id]')].map(h=>({id:h.id,title:h.textContent.trim()}));
  const aliases=Object.fromEntries([...document.querySelectorAll('[id]')].map(e=>{
    const h=e.matches('h2,h3')?e:e.querySelector('h2[id],h3[id]');return [e.id,h?h.id:null];
  }).filter(([_,id])=>id));
  return {style:document.documentElement.dataset.style,counts,headings,aliases};
})()'''

PRINT_CHECK = r'''(async()=>{
  dispatchEvent(new Event('beforeprint'));
  document.querySelectorAll('details.answer').forEach(e=>e.open=true);
  const sheet=document.querySelector('.sheet');
  const old=sheet.style.width;sheet.style.width='612px';
  await document.fonts.ready;
  await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
  const bad=[...document.querySelectorAll('.formula,.inline-math,pre,figure,td,th,.note-main,.example-steps')]
    .filter(e=>e.getBoundingClientRect().height>0 && e.scrollWidth>e.clientWidth+2)
    .map(e=>e.tagName+'.'+e.className+': '+e.textContent.slice(0,60));
  const tall=[...document.querySelectorAll('.formula,figure,tr')]
    .filter(e=>e.getBoundingClientRect().height>986).map(e=>e.tagName);
  const answers=[...document.querySelectorAll('details.answer .answer-body')].every(e=>e.getBoundingClientRect().height>0);
  sheet.style.width=old;
  return {overflow:bad,oversizedUnbreakable:tall,answersVisible:answers};
})()'''


def browser_path(explicit):
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"Browser not found: {path}")
        return str(path)
    candidates = []
    for name in ("google-chrome", "chromium", "chromium-browser", "msedge"):
        resolved = shutil.which(name)
        if resolved:
            candidates.append(resolved)
    for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        root = os.environ.get(variable)
        if root:
            for relative in ("Google/Chrome/Application/chrome.exe", "Microsoft/Edge/Application/msedge.exe"):
                candidates.append(str(Path(root) / relative))
    candidates += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate
    raise ValueError("No Chrome/Edge/Chromium found. Pass --browser with its executable path.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--style", choices=STYLES,
                        help="Optional assertion for locked HTML; cannot override its style. Required for legacy HTML.")
    parser.add_argument("--approved-sha256", required=True, help="Hash of the exact HTML the user approved")
    parser.add_argument("--browser")
    parser.add_argument("--work-dir", type=Path, default=Path.cwd() / "work")
    args = parser.parse_args()
    source = args.html.expanduser().resolve()
    target = args.output.expanduser().resolve()
    try:
        if source.suffix.lower() not in (".html", ".htm") or not source.is_file():
            raise ValueError("Input must be an existing local HTML file.")
        if target.suffix.lower() != ".pdf":
            raise ValueError("Output must have a .pdf extension.")
        if target.exists():
            raise ValueError(f"Output already exists; choose a new filename: {target}")
        source_bytes = source.read_bytes()
        digest = hashlib.sha256(source_bytes).hexdigest()
        if digest != args.approved_sha256.lower():
            raise ValueError("HTML differs from the approved SHA256; return to content review.")
        source_text = source_bytes.decode('utf-8')
        assets = inspect_html(source_text)
        manifest = manifest_from(source_text)
        if manifest:
            style = manifest['style']
            if style not in STYLES: raise ValueError('Unknown locked style.')
            if args.style and args.style != style:
                raise ValueError('Requested style conflicts with the approved HTML; render and review a new version.')
            if manifest['counts'] != assets.counts:
                raise ValueError('Formula/image/answer counts differ from the frozen manifest.')
            for file, fingerprint in manifest.get('fonts',{}).items():
                if not Path(file).is_file() or sha(Path(file).read_bytes()) != fingerprint:
                    raise ValueError('Font environment changed; rerender and review HTML before PDF export: '+file)
        else:
            if args.style not in ('handwritten','electronic'):
                raise ValueError('Legacy HTML needs its explicit reviewed --style handwritten/electronic.')
            style = args.style
        try:
            import fitz
        except ImportError as exc:
            raise ValueError('PDF verification needs PyMuPDF in this Python environment.') from exc
        browser = browser_path(args.browser)
        scratch = args.work_dir.expanduser().resolve()
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="notes-export-", dir=scratch, ignore_cleanup_errors=True) as temporary:
            staging = Path(temporary)
            frozen_html = staging / "approved.html"
            frozen_html.write_bytes(source_bytes)
            with BrowserSession(browser,staging/'profile') as session:
                session.call('Emulation.setDeviceMetricsOverride',{'width':794,'height':1123,'deviceScaleFactor':1,'mobile':False})
                session.navigate(frozen_html.as_uri()+('' if manifest else '?style='+style))
                ready = session.evaluate(READY)
                if ready['style'] != style or ready['counts'] != assets.counts:
                    raise ValueError('Rendered style or resource counts differ from the approved document.')
                session.call('Emulation.setEmulatedMedia',{'media':'print'})
                layout = session.evaluate(PRINT_CHECK)
                if layout['overflow'] or layout['oversizedUnbreakable'] or not layout['answersVisible']:
                    raise ValueError('Print layout needs repair: '+json.dumps(layout,ensure_ascii=False))
                version = session.call('Browser.getVersion')['product']
                result = session.call('Page.printToPDF',{'printBackground':True,'preferCSSPageSize':True,
                    'displayHeaderFooter':False,'generateTaggedPDF':True,'generateDocumentOutline':True})
                payload = base64.b64decode(result['data'])
            if not payload.startswith(b"%PDF-") or not payload.rstrip().endswith(b"%%EOF"):
                raise ValueError("Browser produced an incomplete or invalid PDF.")
            with fitz.open(stream=payload,filetype='pdf') as pdf:
                toc = pdf.get_toc()
                normalize = lambda s: re.sub(r'\s+','',s)
                titles = {normalize(row[1]) for row in toc}
                missing = [h['title'] for h in ready['headings'] if normalize(h['title']) not in titles]
                if missing: raise ValueError('Missing PDF bookmarks: '+str(missing))
                if any(row[2]<1 or row[2]>len(pdf) for row in toc): raise ValueError('Invalid bookmark destination.')
                # Chromium named targets can omit print margins. Use its correctly
                # positioned native heading bookmarks to make portable direct links.
                detailed = pdf.get_toc(simple=False)
                destinations = {}
                cursor = 0
                for heading in ready['headings']:
                    while cursor < len(detailed) and normalize(detailed[cursor][1]) != normalize(heading['title']):
                        cursor += 1
                    if cursor == len(detailed): raise ValueError('PDF heading order differs from HTML.')
                    destinations[heading['id']] = detailed[cursor][3]
                    cursor += 1
                repaired = 0
                for page in pdf:
                    for link in page.get_links():
                        if link['kind'] != fitz.LINK_NAMED: continue
                        anchor = ready['aliases'].get(link.get('nameddest'))
                        if anchor not in destinations:
                            raise ValueError('Internal link target needs a heading anchor: '+str(link.get('nameddest')))
                        dest = destinations[anchor]
                        page.delete_link(link)
                        page.insert_link({'kind':fitz.LINK_GOTO,'from':link['from'],
                                          'page':dest['page'],'to':dest['to']})
                        repaired += 1
                payload = pdf.tobytes(garbage=3,deflate=True)
            with fitz.open(stream=payload,filetype='pdf') as pdf:
                links = [link for page in pdf for link in page.get_links()
                         if link['kind'] in (fitz.LINK_GOTO,fitz.LINK_NAMED)]
                if ready['headings'] and not links: raise ValueError('No internal PDF navigation survived printing.')
                if any(link.get('page',-1)<0 or link['page']>=len(pdf) for link in links):
                    raise ValueError('Invalid internal PDF link destination.')
                report = {'html_sha256':digest,'pdf_sha256':sha(payload),'style':style,'browser':version,
                    'resources':ready['counts'],'print_layout':layout,'pages':len(pdf),
                    'bookmarks':len(toc),'internal_links':len(links),
                    'named_links_normalized':repaired,
                    'scope':'Mechanical checks only; semantic review and page-by-page visual review still required.'}
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as output:
                output.write(payload)
            target.with_suffix('.verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f"PDF: {target}\nStyle: {style}\nApproved HTML SHA256: {digest}")
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"Export failed: {exc}\n")


if __name__ == "__main__":
    main()
