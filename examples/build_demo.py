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
    proof = '<p>对任意实数 x，平方项都不小于 0；只有 x=2 时取等号。因此 x=2 是唯一全局极小点，最小值为 0。</p>'
    boundary = '<p>导数为零通常只是候选条件。本例用平方非负与取等号条件完成全域比较。</p>'
    points = ' '.join(f'{40 + x * 70:.2f},{170 - 36 * (x - 2)**2:.2f}' for x in [i / 25 for i in range(101)])
    curve = f'''<svg viewBox="0 0 370 205" role="img" aria-label="Parabola f(x)=(x-2)^2, with its minimum at x=2" style="display:block;width:340px;margin:auto">
<path d="M25 175H350 M40 185V12" fill="none" stroke="#8598a6"/>
<polyline points="{points}" fill="none" stroke="var(--accent)" stroke-width="2.5"/>
<circle cx="180" cy="170" r="4" fill="#a97131"/>
<g font-size="12" font-family="sans-serif" fill="#26364a"><text x="174" y="197">2</text><text x="31" y="197">0</text><text x="313" y="197">4</text><text x="347" y="194">x</text><text x="46" y="18">f(x)</text><text x="194" y="155">(2, 0)</text></g></svg>
'''
    figure = '<h3 id="geometry">几何核对</h3><figure>' + curve + '<figcaption>曲线由函数采样计算；谷底位置与代数结果一致。</figcaption></figure>'
    title = '<h2 id="problem">驻点之后，还差一个证明</h2>'
    if style == 'cornell':
        body = title + '<p class="source-label">复习方法：遮住右栏，用左栏问题重建推导。</p>'
        body += '<div class="note-unit"><aside class="cue"><strong>01 · 求什么？</strong><p>参数与评分有什么区别？</p></aside><div class="note-main"><strong>先分清问题</strong><p>在实数域上最小化 f。x 是可选参数，f(x) 是比较方案的评分。</p>' + model + '</div></div>'
        body += '<div class="note-unit"><aside class="cue"><strong>02 · 如何定位？</strong><p>导数为零足够吗？</p></aside><div class="note-main"><h3 id="solve">先求候选点</h3>' + derivative + '<p>得到 x=2，此时还没有完成极值判定。</p></div></div>'
        body += '<div class="note-unit"><aside class="cue"><strong>03 · 凭何全局？</strong><p>哪个条件证明唯一？</p></aside><div class="note-main"><strong>比较整个定义域</strong>' + proof + '</div><div class="note-summary"><strong>回忆线索：</strong>候选点 → 全域下界 → 唯一取等号条件。</div></div>' + figure
    elif style == 'outline':
        body = title + '<div class="outline-unit"><h3 id="setup">1　问题与前提</h3><ol><li><strong>定义域：</strong>x ∈ ℝ，可行点没有边界。</li><li><strong>目标：</strong>找最优参数及最小函数值。' + model + '</li></ol>'
        body += '<div class="outline-unit"><h3 id="solve">2　求解与判定</h3><ol><li><strong>候选条件</strong>' + derivative + '</li><li><strong>全局证据</strong><ul><li>下界：平方项对所有 x 非负。</li><li>取等号：仅当 x=2。</li></ul></li><li><strong>结论：</strong>x=2 是唯一全局极小点，最小值为 0。</li></ol></div>'
        body += '<h3 id="boundary">3　使用边界</h3>' + boundary + '</div>' + figure
    elif style == 'annotated':
        body = title + '<p class="module-context">例题：在 ℝ 上最小化 f。左边完成解题，右边核对每步依据。</p>'
        body += '<div class="annotated-example"><div class="example-steps"><strong>① 写清目标</strong>' + model + '</div><aside class="margin-note"><strong>↖ 对象</strong><p>x 是参数，f(x) 是评分，二者不能混写。</p></aside></div>'
        body += '<div class="annotated-example"><div class="example-steps"><h3 id="solve">② 求驻点</h3>' + derivative + '</div><aside class="margin-note"><strong>↖ 必要条件</strong><p>得到候选位置；导数为零尚不能判定极值类型。</p></aside></div>'
        body += '<div class="annotated-example"><div class="example-steps"><strong>③ 证明并作答</strong>' + proof + '</div><aside class="margin-note"><strong>↖ 关键一步</strong><p>“对所有 x”给出全局性；“仅当”给出唯一性。</p></aside></div>' + figure
    elif style == 'sketch':
        body = title + '<p class="lead"><mark>先看谷底，再证明为什么只有一个。</mark></p>' + model
        # The graph and the proof path share a figure so their relationship is
        # visible at a glance. Plot points still come from the same equation.
        diagram = curve.replace('viewBox="0 0 370 205"','viewBox="0 0 710 265"').replace('width:340px','width:100%').replace('</svg>', '''
<g fill="var(--paper)" stroke="var(--accent)" stroke-width="1.5"><rect x="410" y="10" width="278" height="54" rx="3"/><rect x="410" y="96" width="278" height="54" rx="3"/><rect x="410" y="182" width="278" height="54" rx="3"/></g>
<g fill="var(--ink)" font-size="19" font-family="KaiTi,STKaiti,serif" text-anchor="middle"><text x="549" y="44">所有 x：f(x) ≥ 0</text><text x="549" y="130">仅在 x=2：f(x)=0</text><text x="549" y="216">唯一全局极小点</text></g>
<g fill="var(--accent)" font-size="14" text-anchor="middle"><text x="549" y="85">↓ 再检查何时取到</text><text x="549" y="172">↓ 核对取等号条件</text></g>
<path d="M192 166Q300 236 398 206" fill="none" stroke="#a97131" stroke-width="2"/><path d="M389 201L398 206L390 212" fill="none" stroke="#a97131" stroke-width="2"/>
<text x="220" y="251" text-anchor="middle" fill="#a97131" font-size="13" font-family="KaiTi,STKaiti,serif">图中的点，对应式中的等号</text></svg>''')
        body += '<div class="visual-explanation"><h3 id="geometry">一张图连接位置、下界与唯一性</h3><figure>' + diagram + '<figcaption>定义域为 ℝ；曲线按方程采样，右侧关系给出证明依据。</figcaption></figure></div>'
        body += '<h3 id="solve">代数定位</h3>' + derivative + '<p>因此最优参数是 2，最小函数值是 0。</p><div class="caution">' + boundary + '</div>'
    elif style == 'handwritten':
        body = title + '<p class="lead">先记住：<mark>找到驻点，还要说明它为什么最好。</mark></p>'
        body += '<p>题目是在实数域上最小化下面的函数。x 是我们要找的参数，f(x) 是它的评分。</p>' + model
        body += '<h3 id="solve">第一步，求出候选位置</h3>' + derivative
        body += '<p>到这里先别急着写“最小”。接着看原式：<mark>平方项永远非负</mark>，而 x=2 恰好让它等于零。</p>'
        body += '<div class="worked-example"><strong>所以，答案要分开写</strong><p>最优参数 x*=2；最小函数值 f(x*)=0。</p><p>只有 x=2 能取到这个下界，因此全局极小点是唯一的。</p></div>' + figure
    else:
        body = title + '<p class="module-context">目标：在 x ∈ ℝ 上确定最优参数与最小函数值。</p>' + model
        body += '<h3 id="solve">计算候选点</h3>' + derivative
        body += '<table><thead><tr><th>判定事项</th><th>依据</th><th>结论</th></tr></thead><tbody><tr><td>候选位置</td><td>一阶导数为零</td><td>x=2</td></tr><tr><td>全局最小值</td><td>对所有 x，f(x)≥0</td><td>下界为 0</td></tr><tr><td>唯一性</td><td>仅在 x=2 取等号</td><td>唯一全局极小点</td></tr></tbody></table>'
        body += '<div class="question"><strong>结果</strong><p>最优参数为 2；最小函数值为 0。</p></div><p class="source-label">适用边界：驻点方程负责定位，全局结论由函数值比较建立。</p>' + figure
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
