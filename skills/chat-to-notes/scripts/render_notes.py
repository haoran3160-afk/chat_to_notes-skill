"""Assemble authored notes with deterministic navigation; checks structure only."""
import argparse
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from artifact_contract import STYLES, inspect_html, font_fingerprints, sha


class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.duplicates = []
        self.links = []
        self.headings = []
        self.heading = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        identifier = attrs.get('id')
        if identifier:
            if identifier in self.ids:
                self.duplicates.append(identifier)
            self.ids.add(identifier)
        if tag == 'a' and attrs.get('href','').startswith('#'):
            self.links.append(attrs['href'][1:])
        if tag in ('h2','h3'):
            self.heading = [tag, identifier, []]

    def handle_data(self, data):
        if self.heading is not None:
            self.heading[2].append(data)

    def handle_endtag(self, tag):
        if self.heading is not None and self.heading[0] == tag:
            level, identifier, parts = self.heading
            self.headings.append((level,identifier,''.join(parts)))
            self.heading = None


def toc_for(body):
    parsed = Structure()
    parsed.feed(body)
    groups = []
    for level, identifier, title in parsed.headings:
        if not identifier:
            raise ValueError('Each h2/h3 needs an id for navigation.')
        if level == 'h2':
            groups.append([identifier,title,[]])
        elif groups and not identifier.endswith('-review'):
            groups[-1][2].append((identifier,title))
    result = []
    for identifier,title,children in groups:
        title = re.sub(r'^\d+\s+', '', title)
        item = f'<li><a href="#{escape(identifier,quote=True)}">{escape(title)}</a>'
        if children:
            nested = ''.join(f'<li><a href="#{escape(i,quote=True)}">{escape(t)}</a></li>' for i,t in children)
            item += f'<details class="outline"><summary>{len(children)} 个知识点</summary><ol>{nested}</ol></details>'
        result.append(item+'</li>')
    return ''.join(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--body',type=Path,required=True)
    parser.add_argument('--map',dest='map_path',type=Path,required=True)
    parser.add_argument('--title',required=True)
    parser.add_argument('--subtitle',default='')
    parser.add_argument('--source-note',default='')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--style',choices=STYLES,required=True,
                        help='The style already chosen by the user for this document; no implicit default.')
    args = parser.parse_args()
    try:
        body = args.body.read_text(encoding='utf-8')
        knowledge_map = args.map_path.read_text(encoding='utf-8')
        template = (Path(__file__).resolve().parents[1]/'assets/notes.html').read_text(encoding='utf-8')
        style_css = (Path(__file__).resolve().parents[1]/'assets/fixed-styles.css').read_text(encoding='utf-8')
        assets = inspect_html(body+knowledge_map)
        if '<script' in (body+knowledge_map).lower():
            raise ValueError('Author content must be static; keep runtime behavior in the reviewed template.')
        missing_classes = set(STYLES[args.style]['required_classes']) - assets.classes
        if missing_classes:
            raise ValueError('Author the selected layout before rendering; missing classes: '+str(sorted(missing_classes)))
        manifest = {'version':4,'style':args.style,'style_label':STYLES[args.style]['label'],
                    'body_sha256':sha(body.encode()),'map_sha256':sha(knowledge_map.encode()),
                    'template_sha256':sha(template.encode()),'style_css_sha256':sha(style_css.encode()),
                    'counts':assets.counts,'fonts':font_fingerprints(),
                    'semantic_review':'Required separately; not certified by renderer.'}
        values = {'TITLE':escape(args.title),'SUBTITLE':escape(args.subtitle),
                  'KNOWLEDGE_MAP':knowledge_map,'TOC':toc_for(body),'CONTENT':body,
                  'SOURCE_NOTE':escape(args.source_note),'STYLE':args.style,
                  'STYLE_LABEL':escape(STYLES[args.style]['label']),'STYLE_CSS':style_css,
                  'MANIFEST':json.dumps(manifest,ensure_ascii=False).replace('<','\\u003c')}
        placeholders = set(re.findall(r'{{([A-Z_]+)}}',template))
        if placeholders - values.keys():
            raise ValueError('Unknown template placeholders: '+str(placeholders-values.keys()))
        if not args.source_note:
            template = template.replace('<footer class="small">{{SOURCE_NOTE}}</footer>','')
        # One pass preserves literal template-like text in authored code examples.
        result = re.sub(r'{{([A-Z_]+)}}',lambda m:values[m.group(1)],template)
        structure = Structure()
        structure.feed(result)
        missing = set(structure.links)-structure.ids
        if structure.duplicates or missing:
            raise ValueError(f'Duplicate ids: {structure.duplicates}; unresolved links: {sorted(missing)}')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(result,encoding='utf-8')
        record = {**manifest,'html_sha256':sha(args.output.read_bytes())}
        args.output.with_suffix('.manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'output':str(args.output.resolve()),'anchors':len(structure.ids),
                          'internal_links':len(structure.links),'style':args.style,
                          'html_sha256':record['html_sha256'],'mechanical_check_only':True},ensure_ascii=False))
    except (OSError,ValueError) as exc:
        parser.exit(1,f'Render failed: {exc}\n')


if __name__ == '__main__':
    main()
