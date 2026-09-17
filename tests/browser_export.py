"""Real browser integration tests; missing dependencies fail this suite."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import fitz
from test_render import demo, STYLES, SCRIPTS
from browser_session import BrowserSession
from export_pdf import browser_path, READY


class BrowserExportTests(unittest.TestCase):
    def test_all_styles_and_real_pdf_exports(self):
        browser = browser_path(os.environ.get('NOTES_BROWSER'))
        with tempfile.TemporaryDirectory(prefix='notes-browser-test-') as temp:
            folder=Path(temp)
            typography={}
            with BrowserSession(browser,folder/'profile') as session:
                for style in STYLES:
                    with self.subTest(style=style):
                        html=demo.render(style,folder)
                        session.call('Emulation.setDeviceMetricsOverride',{'width':1000,'height':900,'deviceScaleFactor':1,'mobile':False})
                        session.navigate(html.as_uri()+'?style=not-the-selected-style')
                        self.assertEqual(session.evaluate(READY)['style'],style)
                        typography[style]=session.evaluate('({font:getComputedStyle(document.body).fontFamily,paper:getComputedStyle(document.querySelector(".sheet")).backgroundColor})')
                        self.assertFalse(session.evaluate('document.querySelector("details.answer").open'))
                        session.evaluate('dispatchEvent(new Event("beforeprint"))')
                        self.assertTrue(session.evaluate('document.querySelector("details.answer").open'))
                        session.evaluate('dispatchEvent(new Event("afterprint"))')
                        self.assertFalse(session.evaluate('document.querySelector("details.answer").open'))
                        session.call('Emulation.setDeviceMetricsOverride',{'width':390,'height':900,'deviceScaleFactor':1,'mobile':False})
                        self.assertTrue(session.evaluate('document.documentElement.scrollWidth<=innerWidth'))
                        digest=hashlib.sha256(html.read_bytes()).hexdigest()
                        pdf=folder/(style+'.pdf')
                        command=[sys.executable,str(SCRIPTS/'export_pdf.py'),str(html),'--output',str(pdf),
                            '--approved-sha256',digest,'--browser',browser,'--work-dir',str(folder)]
                        result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=90)
                        self.assertEqual(result.returncode,0,result.stderr)
                        record=json.loads(pdf.with_suffix('.verification.json').read_text(encoding='utf-8'))
                        self.assertEqual(record['style'],style)
                        with fitz.open(pdf) as doc:
                            self.assertTrue(doc.get_toc())
                            text=''.join(page.get_text() for page in doc)
                            self.assertIn('unique global maximum',' '.join(text.split()))
                            links=[link for page in doc for link in page.get_links() if link['kind']==fitz.LINK_GOTO]
                            self.assertGreater(len(links),0)
                            self.assertTrue(all(0<=link['page']<len(doc) for link in links))
                        blocked=folder/(style+'-blocked.pdf')
                        conflict=command.copy();conflict[conflict.index('--output')+1]=str(blocked)
                        conflict.extend(['--style','outline' if style!='outline' else 'electronic'])
                        bad=subprocess.run(conflict,capture_output=True,timeout=30)
                        self.assertNotEqual(bad.returncode,0)
                        self.assertFalse(blocked.exists())
                        conflict=command.copy();conflict[conflict.index('--output')+1]=str(blocked)
                        conflict[conflict.index('--approved-sha256')+1]='0'*64
                        bad=subprocess.run(conflict,capture_output=True,timeout=30)
                        self.assertNotEqual(bad.returncode,0)
                        self.assertFalse(blocked.exists())
            self.assertNotEqual(typography['handwritten'],typography['electronic'])


if __name__=='__main__': unittest.main()
