"""Standard-library regression checks for public rendering behavior."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/chat-to-notes/scripts'
sys.path.insert(0, str(SCRIPTS))
from artifact_contract import STYLES, inspect_html, manifest_from

spec = importlib.util.spec_from_file_location('demo', ROOT / 'examples/build_demo.py')
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class RenderTests(unittest.TestCase):
    def test_six_styles_preserve_source_and_resources(self):
        with tempfile.TemporaryDirectory() as temp:
            for style in STYLES:
                with self.subTest(style=style):
                    output = demo.render(style, temp)
                    text = output.read_text(encoding='utf-8')
                    manifest = manifest_from(text)
                    self.assertEqual(manifest['style'], style)
                    self.assertEqual(manifest['counts'], dict(math=2, images=0, svg=1, answers=1))
                    # Body hashes represent decoded, LF-normalized content;
                    # only the approved HTML hash binds exact file bytes.
                    body = (Path(temp) / (style + '-body.html')).read_text(encoding='utf-8')
                    self.assertEqual(manifest['body_sha256'], hashlib.sha256(body.encode('utf-8')).hexdigest())
                    self.assertIn(body, text)
                    self.assertNotIn('data-theme=', text)
                    self.assertNotIn('new URLSearchParams', text)
                    record = json.loads(output.with_suffix('.manifest.json').read_text(encoding='utf-8'))
                    self.assertEqual(record['html_sha256'], hashlib.sha256(output.read_bytes()).hexdigest())

    def test_invalid_input_does_not_write_html(self):
        variants = {
            'missing-style': ('<h2 id="one">Title</h2>', []),
            'duplicate-id': ('<h2 id="one">One</h2><h3 id="one">Two</h3>', ['--style','electronic']),
            'broken-link': ('<h2 id="one">One</h2><a href="#absent">Bad</a>', ['--style','electronic']),
            'remote-image': ('<h2 id="one">One</h2><img src="https://example.invalid/x.png" alt="test">', ['--style','electronic']),
            'missing-cornell-layout': ('<h2 id="one">One</h2>', ['--style','cornell']),
            'unconverted-math': ('<h2 id="one">One</h2><tex>x^2</tex>', ['--style','electronic']),
        }
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            (folder/'map.html').write_text('',encoding='utf-8')
            for case,(body,flags) in variants.items():
                with self.subTest(case=case):
                    (folder/'body.html').write_text(body,encoding='utf-8')
                    out=folder/(case+'.html')
                    result=subprocess.run([sys.executable,str(SCRIPTS/'render_notes.py'),'--body',str(folder/'body.html'),
                        '--map',str(folder/'map.html'),'--title','Fixture','--output',str(out),*flags],capture_output=True)
                    self.assertNotEqual(result.returncode,0)
                    self.assertFalse(out.exists())

    def test_static_formula_and_svg_are_accepted(self):
        parsed=inspect_html('<math><mi>x</mi></math><svg role="img" aria-label="diagram"></svg>')
        self.assertEqual(parsed.counts['math'],1)
        self.assertEqual(parsed.counts['svg'],1)


if __name__=='__main__': unittest.main()
