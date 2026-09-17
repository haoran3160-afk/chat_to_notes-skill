"""Mechanical artifact checks; does not assess mathematical or teaching correctness."""
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
STYLES = json.loads((ASSETS / 'styles.json').read_text(encoding='utf-8'))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def font_fingerprints():
    root = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
    return {str(p): sha(p.read_bytes()) for name in ('simkai.ttf','STKAITI.TTF','simsun.ttc','msyh.ttc','cambria.ttc','consola.ttf')
            if (p := root / name).is_file()}

class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.counts = dict(math=0, images=0, svg=0, answers=0)
        self.classes = set()
        self.errors = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.classes.update(a.get('class','').split())
        if tag == 'math': self.counts['math'] += 1
        if tag == 'svg': self.counts['svg'] += 1
        if tag == 'img':
            self.counts['images'] += 1
            if not a.get('src','').startswith('data:image/'):
                self.errors.append('Images must be embedded data:image resources.')
            if not a.get('alt','').strip(): self.errors.append('Image lacks an explanatory alt attribute.')
        if tag == 'details' and 'answer' in a.get('class','').split(): self.counts['answers'] += 1
        if tag in ('merror','tex','m'):
            self.errors.append(f'Unrendered or invalid math element: {tag}')
        if tag in ('iframe','object','embed','video','audio','canvas'):
            self.errors.append(f'Freeze dynamic resources as an image or SVG before delivery: {tag}')
        if tag == 'link' and a.get('rel','').lower() == 'stylesheet':
            self.errors.append('Stylesheets must be inlined.')
        for key in ('src','srcset','poster'):
            if key in a and not a[key].startswith('data:'):
                self.errors.append(f'Unfrozen {tag} {key}.')
        if tag in ('image','use'):
            for key in ('href','xlink:href'):
                if key in a and not a[key].startswith(('#','data:')):
                    self.errors.append('External SVG dependency.')

def inspect_html(text):
    p = Assets(); p.feed(text)
    # CSS URLs must be embedded; ordinary source citations remain clickable URLs.
    for url in re.findall(r'url\(\s*[\"\']?([^\)\"\']+)', text, re.I):
        if not url.startswith(('data:','#')): p.errors.append('Unfrozen CSS resource: '+url)
    if p.errors: raise ValueError('; '.join(sorted(set(p.errors))))
    return p

def manifest_from(text):
    m = re.search(r'<script id="notes-manifest" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(m.group(1)) if m else None
