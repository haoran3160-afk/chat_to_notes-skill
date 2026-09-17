"""Render independent synthetic math notes through the actual Skill renderer."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/chat-to-notes'
sys.path.insert(0, str(SKILL / 'scripts'))
from artifact_contract import STYLES


def formula(content):
    return '<div class="formula"><math xmlns="http://www.w3.org/1998/Math/MathML" display="block">' + content + '</math></div>'


def example_body(style):
    model = formula('<mrow><mi>f</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>=</mo><msup><mrow><mo>(</mo><mi>x</mi><mo>−</mo><mn>2</mn><mo>)</mo></mrow><mn>2</mn></msup></mrow>')
    derivative = formula('<mrow><msup><mi>f</mi><mo>′</mo></msup><mo>(</mo><mi>x</mi><mo>)</mo><mo>=</mo><mn>2</mn><mo>(</mo><mi>x</mi><mo>−</mo><mn>2</mn><mo>)</mo><mo>=</mo><mn>0</mn><mo>⇒</mo><mi>x</mi><mo>=</mo><mn>2</mn></mrow>')
    proof = '<p>对任意实数 x，平方项都不小于 0；只有 x=2 时取等号。因此 x=2 是唯一全局极小点，最小值为 0。这个证明直接比较所有可行点，无需从局部结论猜测全局性质。</p>'
    body = '<h2 id="problem">从候选点到全局结论</h2><p>独立合成例题：在实数域上最小化下列函数。先区分“最优参数”和“最小函数值”。</p>' + model
    explanation = '<h3 id="solve">求导定位，比较函数值完成证明</h3>' + derivative + proof
    cue = '<p>梯度为零得到了什么？哪一步比较了整个定义域？</p>'
    boundary = '<p>导数为零通常只是候选条件。本例的全局结论来自平方非负与取等号条件。</p>'
    if style == 'cornell':
        body += '<div class="note-unit"><aside class="cue">' + cue + '</aside><div class="note-main">' + explanation + '</div><div class="note-summary">' + boundary + '</div></div>'
    elif style == 'outline':
        body += '<div class="outline-unit">' + explanation + boundary + '</div>'
    elif style == 'annotated':
        body += '<div class="annotated-example"><div class="example-steps">' + explanation + '</div><aside class="margin-note">' + boundary + '</aside></div>'
    elif style == 'sketch':
        body += '<div class="visual-explanation">' + explanation + boundary + '</div>'
    else:
        body += explanation + '<div class="caution">' + boundary + '</div>'
    points = ' '.join(f'{40 + x * 70:.2f},{170 - 36 * (x - 2)**2:.2f}' for x in [i / 25 for i in range(101)])
    body += '<h3 id="geometry">图形提供直觉，式子给出依据</h3>'
    body += f'''<figure><svg viewBox="0 0 370 205" role="img" aria-label="Parabola f(x)=(x-2)^2, with its minimum at x=2" style="display:block;width:380px;margin:auto">
<path d="M25 175H350 M40 185V12" fill="none" stroke="#8598a6"/>
<polyline points="{points}" fill="none" stroke="#366b58" stroke-width="2.5"/>
<circle cx="180" cy="170" r="4" fill="#a97131"/>
<g font-size="12" font-family="sans-serif" fill="#26364a"><text x="174" y="197">2</text><text x="31" y="197">0</text><text x="313" y="197">4</text><text x="347" y="194">x</text><text x="46" y="18">f(x)</text><text x="194" y="155">(2, 0)</text></g></svg>
<figcaption>曲线由本页函数采样计算；它不代替上面的全域比较。</figcaption></figure>'''
    body += '''<div class="retrieval"><h3 id="practice-review">变式：把平方项前的符号改成负号</h3>
<p>若 g(x)=−(x−2)²，驻点还在 x=2 吗？它是什么类型的极值？</p>
<details class="answer"><summary>答案与理由 / Answer</summary><div class="answer-body"><p>驻点仍为 x=2，但所有函数值都不大于 0，故它成为唯一全局极大点。改变符号没有改变驻点位置，却反转了比较方向。</p><p>English: x=2 is the unique global maximum.</p><a href="#solve">回看函数值比较</a></div></details></div>'''
    return body


MAP = '<section class="knowledge-map" id="knowledge-map"><h2 id="map-title">关系地图</h2><p><a href="#solve">求导得到候选 → 非负性给出全域比较</a> → <a href="#practice-review">变式检验判断依据</a></p></section>'


def render(style, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    body = directory / (style + '-body.html')
    graph = directory / 'map.html'
    output = directory / (style + '.html')
    body.write_text(example_body(style), encoding='utf-8')
    graph.write_text(MAP, encoding='utf-8')
    subprocess.run([sys.executable, str(SKILL / 'scripts/render_notes.py'), '--body', str(body),
        '--map', str(graph), '--style', style, '--title', STYLES[style]['label'],
        '--subtitle', 'Chat to Notes · Synthetic example / 合成示例', '--output', str(output)], check=True)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--style', choices=[*STYLES, 'all'], default='electronic')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs/demo')
    args = parser.parse_args()
    for choice in STYLES if args.style == 'all' else [args.style]:
        render(choice, args.output_dir)
