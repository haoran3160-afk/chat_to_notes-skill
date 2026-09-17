"""Capture actual Skill HTML without replacing its typography or layout CSS."""
import argparse
import base64
from pathlib import Path
import sys
import tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/chat-to-notes/scripts'))
from artifact_contract import STYLES
from browser_session import BrowserSession
from export_pdf import browser_path, READY

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--html-dir', type=Path, default=ROOT / 'outputs/demo')
parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/previews')
parser.add_argument('--browser')
args = parser.parse_args()
args.output_dir.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='notes-previews-') as temporary:
    with BrowserSession(browser_path(args.browser), Path(temporary) / 'profile') as browser:
        browser.call('Emulation.setDeviceMetricsOverride', {'width':980,'height':1400,'deviceScaleFactor':1,'mobile':False})
        for style in STYLES:
            browser.navigate((args.html_dir / (style + '.html')).resolve().as_uri())
            state = browser.evaluate(READY)
            assert state['style'] == style
            # Include the complete page and the expanded answer. No style CSS
            # is injected, so previews use the same rendering path as real notes.
            browser.evaluate("document.querySelector('details.answer').open=true")
            browser.evaluate('(async()=>{await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));})()')
            height = browser.evaluate('Math.ceil(document.documentElement.scrollHeight)')
            browser.call('Emulation.setDeviceMetricsOverride', {'width':980,'height':height,'deviceScaleFactor':1,'mobile':False})
            browser.evaluate('(async()=>{await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));})()')
            data = browser.call('Page.captureScreenshot', {'format':'png','captureBeyondViewport':True})['data']
            (args.output_dir / (style + '.png')).write_bytes(base64.b64decode(data))

sheet = Image.new('RGB', (1500, 1800), '#e9edf0')
draw = ImageDraw.Draw(sheet)
font = ImageFont.load_default(size=20)
for i, style in enumerate(STYLES):
    picture = Image.open(args.output_dir / (style + '.png'))
    picture.thumbnail((470, 835))
    x, y = (i % 3) * 500 + 15, (i // 3) * 900 + 50
    sheet.paste(picture, (x + (470 - picture.width)//2, y))
    draw.text((x, y - 35), f'{i+1:02}  {style}', font=font, fill='#243044')
sheet.save(args.output_dir / 'styles-overview.png')
print(args.output_dir.resolve())
