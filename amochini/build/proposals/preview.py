"""Render the chinese-ornament proposal onto the live page, without
changing it. Serve public/ on 8901, then:  python3 build/proposals/preview.py
Writes CLASSY-{phone,tablet,desktop}.png next to this file."""
import os
from playwright.sync_api import sync_playwright
seal = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"seal-shache.svg")).read()

FRET = ('<svg class="cn-fret" aria-hidden="true" preserveAspectRatio="none"><defs>'
        '<pattern id="cnf" width="44" height="14" patternUnits="userSpaceOnUse">'
        '<path d="M2 11 V2 H20 V8.5 H10 V5.5  M24 2 V11 H42 V5.5 H32 V8.5" '
        'fill="none" stroke="#f7ae0c" stroke-width="1.6"/></pattern>'
        '<linearGradient id="fg" x1="0" x2="1">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".13" stop-color="#fff" stop-opacity="1"/>'
        '<stop offset=".87" stop-color="#fff" stop-opacity="1"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        '<mask id="fm"><rect width="100%" height="14" fill="url(#fg)"/></mask></defs>'
        '<rect width="100%" height="14" fill="url(#cnf)" mask="url(#fm)" opacity=".85"/></svg>')
SEAL = f'<span class="cn-seal" aria-hidden="true">{seal}</span>'

CSS = (".bb-photo{position:relative}"
       ".cn-fret{position:absolute;inset-inline:0;inset-block-start:0;height:14px;z-index:4}"
       ".cn-seal{position:absolute;z-index:5;width:44px;height:44px;"
       "inset-block-start:20px;"
       "inset-inline-end:max(14px,calc((100% - 1180px)/2 + 12px))}"
       ".cn-seal svg{width:100%;height:100%;display:block}")
ADD = "(h)=>{document.querySelector('.bb-photo').insertAdjacentHTML('beforeend',h)}"

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    for W,H,name in [(375,812,"phone"),(768,1024,"tablet"),(1440,900,"desktop")]:
        p = b.new_page(viewport={"width":W,"height":H})
        p.goto("http://127.0.0.1:8901/", wait_until="networkidle")
        p.add_style_tag(content=CSS); p.evaluate(ADD, FRET+SEAL)
        p.wait_for_timeout(350)
        p.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),f"CLASSY-{name}.png"),
                     clip={"x":0,"y":0,"width":W,"height":min(H,900)})
        p.close()
    b.close()
print("ok")
