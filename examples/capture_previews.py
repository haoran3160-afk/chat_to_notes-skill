"""Capture full Skill pages and characteristic body excerpts without CSS overrides."""
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
            # Show the style-specific explanation, not identical page furniture.
            # The visual style includes its diagram; the other excerpts end
            # before their shared geometric cross-check. Full pages remain linked.
            clip = browser.evaluate('''(()=>{
                const sheet=document.querySelector('.sheet').getBoundingClientRect();
                const article=document.querySelector('article').getBoundingClientRect();
                const stop=document.getElementById(document.documentElement.dataset.style==='sketch'?'practice-review':'geometry').getBoundingClientRect();
                const top=article.top+scrollY-12;
                return {x:sheet.left+38,y:top,width:sheet.width-76,height:stop.top+scrollY-top-12,scale:1};
            })()''')
            if clip['height'] <= 0:
                raise RuntimeError('Missing or reversed showcase bounds for ' + style)
            data = browser.call('Page.captureScreenshot', {'format':'png','captureBeyondViewport':True,'clip':clip})['data']
            (args.output_dir / (style + '-detail.png')).write_bytes(base64.b64decode(data))

captions = {
    'cornell': ('CORNELL CUES', 'Recall questions / Full explanations / Summary'),
    'outline': ('HIERARCHICAL OUTLINE', 'Nested logic / Numbered steps / Explicit conditions'),
    'annotated': ('ANNOTATED EXAMPLE', 'Solution on the left / Reasons on the right'),
    'sketch': ('VISUAL HANDWRITTEN', 'Graph / Proof path / Handwritten emphasis'),
    'handwritten': ('CLASSIC HANDWRITTEN', 'Calligraphy / Warm dotted paper / Continuous prose'),
    'electronic': ('FORMAL DIGITAL', 'Sans-serif type / Evidence table / White paper'),
}
sheet = Image.new('RGB', (1800, 2460), '#e9edf0')
draw = ImageDraw.Draw(sheet)
font = ImageFont.load_default(size=30)
small = ImageFont.load_default(size=19)
for i, style in enumerate(STYLES):
    picture = Image.open(args.output_dir / (style + '-detail.png'))
    picture.thumbnail((844, 685))
    x, y = (i % 2) * 900 + 28, (i // 2) * 820 + 108
    draw.rectangle((x,y,x+844,y+685),fill='#ffffff')
    sheet.paste(picture, (x + (844 - picture.width)//2, y))
    heading,description=captions[style]
    draw.text((x, y - 84), f'{i+1:02}  {heading}', font=font, fill='#243044')
    draw.text((x, y - 42), description, font=small, fill='#526578')
sheet.save(args.output_dir / 'styles-overview.png')
print(args.output_dir.resolve())
