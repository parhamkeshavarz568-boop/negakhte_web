"""Every text node on home.html against its real painted ground.

The sweep is IMPORTED from contrast.py, not sliced out of it as text:
reading the file raw leaves the \\d escapes literal, JS then builds
/[\\d.]+/ which matches a backslash, every colour parses as black and all
111 rows report a fake 1:1 failure. Ask me how I know.
"""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("con", "contrast.py")
con = importlib.util.module_from_spec(spec)
sys.modules["con"] = con
spec.loader.exec_module.__self__ if False else None
# exec only the module top-level constants, not its main()
src = open("contrast.py", encoding="utf-8").read().split("def main(")[0]
ns = {}
exec(compile(src, "contrast.py", "exec"), ns)
SWEEP = ns["SWEEP"]

from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    bad = 0
    for W, H in [(390, 844), (1440, 950)]:
        p = b.new_page(viewport={"width": W, "height": H})
        p.goto("http://127.0.0.1:8731/home.html"); p.wait_for_timeout(900)
        p.evaluate("()=>document.querySelectorAll('details').forEach(d=>d.open=true)")
        p.wait_for_timeout(250)
        rows = p.evaluate(SWEEP)
        print(f"  {W:>5}px  {'OK' if not rows else str(len(rows)) + ' FAIL'}")
        for r in rows:
            bad += 1
            print(f"     {r['ratio']}:1 (need {r['need']}) {r['sel']} — {r['text'][:36]}"
                  f"   {r['fg']} on {r['bg']}")
        p.close()
    b.close()
print("\n✓ every visible text node on home.html clears AA on its real ground"
      if not bad else f"\n✗ {bad} failing")
