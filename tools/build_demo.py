#!/usr/bin/env python3
"""Generate the two demo pages from a single source of truth.

    python3 tools/build_demo.py

Reads the copy-paste build prompt out of `prompts/一键构建.md` and injects it
into the demo shell twice:

* docs/index.html      – offline build, everything inlined, works with no network
* docs/index-cdn.html  – same content plus web fonts and GSAP choreography

产物同时充当 GitHub Pages 首页。共用一个源文件，两个页面的内容永远不会走散。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHELL = ROOT / "docs" / "_shell.html"
PROMPT_FILE = ROOT / "prompts" / "一键构建.md"
PLACEHOLDER = "{{BUILD_PROMPT}}"

CDN_HEAD = """<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/inter@5.0.16/index.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/jetbrains-mono@5.0.18/index.min.css">
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
  <style>
    /* ---------- CDN 版增强：字体、光晕、转场 ---------- */
    :root{
      --font:"Inter","PingFang SC","Microsoft YaHei","Noto Sans SC",system-ui,sans-serif;
      --mono:"JetBrains Mono","SFMono-Regular",Consolas,monospace;
    }
    /* 光标跟随光晕 */
    #spot{
      position:fixed; left:0; top:0; width:620px; height:620px; z-index:2;
      margin:-310px 0 0 -310px; border-radius:50%; pointer-events:none;
      background:radial-gradient(circle,rgba(200,247,81,.14),rgba(76,201,240,.07) 42%,transparent 68%);
      opacity:0; transition:opacity .5s ease; will-change:transform;
    }
    body:hover #spot{opacity:1}
    /* 标题渐变流光 */
    .slide.is-active h1 .accent,
    .slide.is-active h2 .accent{
      background:linear-gradient(92deg,#c8f751,#8ef0a0 42%,#c8f751);
      -webkit-background-clip:text; background-clip:text; color:transparent;
      background-size:220% 100%; animation:shine 5s linear infinite;
    }
    @keyframes shine{to{background-position:-220% 0}}
    /* 转场：模糊 + 位移 */
    .slide{filter:blur(0)}
    .slide:not(.is-active){filter:blur(9px)}
    /* 卡片描边呼吸 */
    .slide.is-active .card{animation:breathe 5.5s ease-in-out infinite}
    .slide.is-active .card:nth-child(2){animation-delay:.5s}
    .slide.is-active .card:nth-child(3){animation-delay:1s}
    @keyframes breathe{0%,100%{border-color:rgba(255,255,255,.10)}50%{border-color:rgba(200,247,81,.30)}}
    /* 流程箭头流光 */
    .slide.is-active .step::after{
      content:""; position:absolute; inset:0; border-radius:16px; pointer-events:none;
      background:linear-gradient(120deg,transparent 30%,rgba(200,247,81,.16),transparent 70%);
      background-size:220% 100%; animation:sweep 2.4s ease-in-out infinite;
    }
    @keyframes sweep{0%{background-position:180% 0}100%{background-position:-80% 0}}
    /* GSAP 接管后禁用 CSS 入场，避免两套动画打架 */
    .gsap-on .rv{animation:none!important;opacity:1!important;transform:none!important}
    .gsap-on .bar>i{animation:none!important}
  </style>
</head>"""

CDN_SCRIPT = """
<script>
/* ---------- CDN 版增强脚本：GSAP 编排 + 光标光晕 ---------- */
(function(){
  var ready = (typeof gsap !== 'undefined');
  if(ready) document.documentElement.classList.add('gsap-on');

  /* 光标光晕：lerp 跟随，比直接定位柔和 */
  var spot = document.createElement('div'); spot.id = 'spot'; document.body.appendChild(spot);
  var tx=window.innerWidth/2, ty=window.innerHeight/2, cx=tx, cy=ty;
  window.addEventListener('mousemove', function(e){ tx=e.clientX; ty=e.clientY; });
  (function loop(){ cx += (tx-cx)*0.09; cy += (ty-cy)*0.09;
    spot.style.transform='translate3d('+cx+'px,'+cy+'px,0)'; requestAnimationFrame(loop); })();

  if(!ready) return;

  var slides=[].slice.call(document.querySelectorAll('.slide'));

  /* 每页进入时重新编排：标题先落，内容错峰跟进 */
  function animate(slide){
    var heads = slide.querySelectorAll('h1,h2,.kicker,.quote,.closing h1');
    var items = slide.querySelectorAll('.rv');
    var bars  = slide.querySelectorAll('.bar > i');
    gsap.killTweensOf(slide.querySelectorAll('*'));

    /* 关键：把非当前页上的 GSAP 内联样式清掉，交还给 CSS，
       否则快速翻页时旧页会留下 opacity:1 的幽灵层。 */
    slides.forEach(function(s){
      if(s !== slide) gsap.set(s, {clearProps:'opacity,transform,filter'});
    });

    gsap.fromTo(slide, {opacity:0, x:70, scale:.985},
                {opacity:1, x:0, scale:1, duration:.62, ease:'power3.out',
                 onComplete:function(){ gsap.set(slide,{clearProps:'opacity,transform,filter'}); }});
    if(heads.length) gsap.fromTo(heads, {opacity:0, y:34, filter:'blur(8px)'},
                {opacity:1, y:0, filter:'blur(0px)', duration:.7, stagger:.08, ease:'power3.out', delay:.1});
    if(items.length) gsap.fromTo(items, {opacity:0, y:30, scale:.985},
                {opacity:1, y:0, scale:1, duration:.6, stagger:.055, ease:'power2.out', delay:.26});
    if(bars.length)  gsap.fromTo(bars, {scaleX:0},
                {scaleX:function(i,t){return t.style.getPropertyValue('--w')||1;},
                 duration:1.05, stagger:.12, ease:'power2.out', delay:.7});
  }

  var current = -1;
  function sync(){
    var i = slides.findIndex(function(s){ return s.classList.contains('is-active'); });
    if(i !== -1 && i !== current){ current = i; animate(slides[i]); }
    requestAnimationFrame(sync);
  }
  requestAnimationFrame(sync);
})();
</script>
</body>"""


def extract_prompt() -> str:
    """Pull the fenced ```text block that starts with 【开始：."""
    text = PROMPT_FILE.read_text(encoding="utf-8")
    for block in re.findall(r"```text\n(.*?)```", text, flags=re.S):
        if "【开始：" in block:
            return block.rstrip()
    raise SystemExit("在 prompts/一键构建.md 中找不到以 【开始： 开头的 ```text 代码块")


def main() -> int:
    shell = SHELL.read_text(encoding="utf-8")
    if PLACEHOLDER not in shell:
        raise SystemExit(f"docs/_shell.html 缺少占位符 {PLACEHOLDER}；请先还原模板")

    prompt = extract_prompt()
    offline = shell.replace(PLACEHOLDER, prompt)
    (ROOT / "docs" / "index.html").write_text(offline, encoding="utf-8")

    cdn = offline.replace("</head>", CDN_HEAD)
    cdn = cdn.replace("</body>", CDN_SCRIPT)
    cdn = cdn.replace("<title>个人知识库 · 产品演示", "<title>个人知识库 · 产品演示（CDN 增强版）")
    (ROOT / "docs" / "index-cdn.html").write_text(cdn, encoding="utf-8")

    print(f"已生成 docs/index.html 与 docs/index-cdn.html（构建指令 {len(prompt)} 字符）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
