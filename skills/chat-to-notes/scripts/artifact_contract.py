"""Mechanical artifact checks; does not assess mathematical or teaching correctness."""
import base64
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
STYLES = json.loads((ASSETS / 'styles.json').read_text(encoding='utf-8'))

# Static note vocabulary, not a general-purpose HTML sanitizer. Unknown markup
# fails closed instead of being silently rewritten into different content.
AUTHOR_TAGS = set('''a abbr article aside b bdi bdo blockquote br caption cite code col
colgroup dd del details dfn div dl dt em figcaption figure footer h1 h2 h3 h4 h5 h6
header hr i img kbd li main mark nav ol p pre q rp rt ruby s samp section small span
strong sub summary sup table tbody td th thead time tr u ul var wbr
svg g defs symbol use image path rect circle ellipse line polyline polygon text tspan
title desc clippath mask marker lineargradient radialgradient stop pattern
math maction menclose merror mfenced mfrac mi mmultiscripts mn mo mover mpadded mphantom
mprescripts mroot mrow ms mspace msqrt mstyle msub msubsup msup mtable mtd mtext mtr
munder munderover none semantics annotation'''.split())
AUTHOR_ATTRS = set('''id class title lang dir role style hidden href src alt width height
colspan rowspan scope headers span start reversed type value datetime cite open
xmlns xmlns:xlink xlink:href viewbox preserveaspectratio x y x1 y1 x2 y2 cx cy r rx ry
d points transform fill fill-rule fill-opacity stroke stroke-width stroke-linecap
stroke-linejoin stroke-dasharray stroke-dashoffset stroke-opacity opacity clip-path
clip-rule mask marker-start marker-mid marker-end markerwidth markerheight refx refy
orient markerunits gradientunits gradienttransform spreadmethod offset stop-color
stop-opacity patternunits patterncontentunits patterntransform font-family font-size
font-weight font-style text-anchor dominant-baseline alignment-baseline dx dy rotate
textlength lengthadjust display mathvariant mathsize mathcolor mathbackground
displaystyle scriptlevel stretchy symmetric largeop movablelimits form fence separator
lspace rspace accent accentunder bevelled linethickness notation columnalign rowalign
columnspacing rowspacing columnlines rowlines equalrows equalcolumns frame framespacing
rowspan columnspan actiontype selection encoding'''.split())

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
        self.scripts = []
        self.script = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if len(a) != len(attrs):
            self.errors.append('Active content has ambiguous duplicate attributes.')
        if tag not in AUTHOR_TAGS | {'html', 'head', 'body', 'meta', 'style', 'script'}:
            self.errors.append('Active content or unsupported element: '+tag)
        for key, value in attrs:
            if key.startswith('on'):
                self.errors.append('Active content event attribute: '+key)
            if key in ('href', 'xlink:href', 'src', 'cite'):
                url = re.sub(r'[\x00-\x20\x7f]', '', value or '')
                scheme = urlsplit(url).scheme.lower()
                image_data = (tag in ('img','image','use') and url.lower().startswith('data:image/'))
                if scheme not in ('', 'http', 'https', 'mailto') and not image_data:
                    self.errors.append('Active content or unsupported URL scheme.')
        if tag == 'meta' and a.get('http-equiv','').lower() not in ('','content-security-policy'):
            self.errors.append('Active content metadata directive.')
        if tag == 'script':
            self.script = [a, '']
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

    def handle_data(self, data):
        if self.script is not None:
            self.script[1] += data

    def unknown_decl(self, data):
        # HTMLParser skips CDATA/marked sections, whereas HTML browser parsing
        # may expose their contents as real elements. Escape literal examples.
        self.errors.append('Active content or unsupported markup declaration.')

    def handle_endtag(self, tag):
        if tag == 'script' and self.script is not None:
            self.scripts.append(self.script)
            self.script = None


def trusted_scripts():
    parser = Assets()
    parser.feed((ASSETS / 'notes.html').read_text(encoding='utf-8'))
    return {body for attrs, body in parser.scripts if not attrs}


def content_security_policy():
    hashes = ['\'sha256-'+base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()+"'"
              for body in sorted(trusted_scripts())]
    return ("default-src 'none'; script-src "+' '.join(hashes)+"; style-src 'unsafe-inline'; "
            "img-src data:; font-src data:; base-uri 'none'; form-action 'none'; object-src 'none'")


def inspect_author_html(text):
    class Author(Assets):
        def handle_starttag(self, tag, attrs):
            super().handle_starttag(tag, attrs)
            if tag not in AUTHOR_TAGS:
                self.errors.append('Active content or unsupported author element: '+tag)
            for key, _ in attrs:
                if key not in AUTHOR_ATTRS and not key.startswith(('aria-', 'data-')):
                    self.errors.append('Unsupported author attribute: '+key)
    return inspect_html(text, parser=Author())

def inspect_html(text, *, parser=None):
    p = parser if parser is not None else Assets()
    p.feed(text)
    p.close()
    allowed_scripts = trusted_scripts() if p.scripts else set()
    for attrs, body in p.scripts:
        # HTML input preprocessing normalizes newlines before script execution.
        # The approved file hash still binds the original bytes separately.
        body = body.replace('\r\n', '\n').replace('\r', '\n')
        if attrs == {'id':'notes-manifest', 'type':'application/json'}:
            try: json.loads(body)
            except ValueError: p.errors.append('Invalid notes manifest.')
        elif attrs or body not in allowed_scripts:
            p.errors.append('Active content script is not from the trusted template.')
    if p.script is not None:
        p.errors.append('Active content contains an unclosed script.')
    # CSS URLs must be embedded; ordinary source citations remain clickable URLs.
    for url in re.findall(r'url\(\s*[\"\']?([^\)\"\']+)', text, re.I):
        if not url.startswith(('data:','#')): p.errors.append('Unfrozen CSS resource: '+url)
    if p.errors: raise ValueError('; '.join(sorted(set(p.errors))))
    return p

def manifest_from(text):
    m = re.search(r'<script id="notes-manifest" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(m.group(1)) if m else None
