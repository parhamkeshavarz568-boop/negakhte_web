#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The tape must never show a gap.

    cd amochini/public && python3 -m http.server 8907 &
    PORT=8907 python3 build/check_tape.py

A marquee is N identical copies translated by one copy's width, so that the
next copy arrives exactly where the last began. Two things decide whether that
works, and neither is visible in the rule that sets it up.

WHICH EDGE the overflowing track is anchored to — decided by the direction of
the track's PARENT, not the track. On an RTL page the window inherited rtl, the
track hung off to the left, and animating it further left emptied the window
and left it blank for the rest of the 64s cycle.

HOW MANY COPIES — the window is covered only while window <= (N-1) x copy.
Two copies means "window <= one copy", which held to 2560 and opened a hole at
3440 and 3840.

So this does not check the CSS. It samples 21 offsets across one half-width,
walks the window in 4px steps at each one, and requires every step to land on
a .tick. That is the property the reader actually cares about: at no moment is
there a hole in the tape.

It also checks the reduced-motion path, where the animation is dropped and the
strip has to stay horizontally scrollable — a separate failure that has
happened before (width:auto made scrollWidth == clientWidth and stranded 17 of
20 items out of reach).
"""
import os, sys
from playwright.sync_api import sync_playwright

PORT = os.environ.get("PORT", "8907")
BASE = f"http://localhost:{PORT}"
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium")
# 360 is the narrowest phone worth serving. 3440 and 3840 are here because
# that is exactly where the two-copy version broke — a window wider than one
# copy — so they are the cases this check exists to hold.
WIDTHS = [(360, 780), (390, 844), (768, 1024), (1024, 768), (1440, 900),
          (1920, 1080), (2560, 1080), (3440, 1440), (3840, 1600)]
SAMPLES = 21
STEP_PX = 4

# Freeze the animation and place the track by hand, so the probe is
# deterministic — sampling a live animation would make this flaky.
PROBE = """(t)=>{
  const win=document.querySelector('.ticker-win');
  const tr=document.querySelector('.ticker-track');
  tr.style.animation='none';
  // Derive the copy width from data-copies — the same number the keyframe
  // divides by — so this cannot silently measure the wrong stride.
  const copies=Number(tr.dataset.copies);
  if(!copies || tr.children.length % copies) return {err:
    `data-copies=${tr.dataset.copies} does not divide ${tr.children.length} ticks`};
  const declared=getComputedStyle(tr).getPropertyValue('--copies').trim();
  if(Number(declared)!==copies) return {err:
    `markup says data-copies=${copies} but CSS says --copies=${declared}`};
  // Stride = trackWidth / copies, which is what the keyframe's
  // calc(-100% / var(--copies)) actually resolves to. Summing the first
  // copy's ticks instead would agree only while every copy is identical —
  // true today, but then the check would be assuming the thing it is
  // supposed to be testing.
  const half=tr.getBoundingClientRect().width/copies;
  tr.style.transform=`translateX(${-half*t}px)`;
  const w=win.getBoundingClientRect();
  let gaps=0, first=null;
  for(let x=w.left+1; x<w.right-1; x+=STEP){
    const hit=document.elementsFromPoint(x, w.top+w.height/2)
        .some(el=>el.closest && el.closest('.tick'));
    if(!hit){ gaps++; if(first===null) first=Math.round(x-w.left); }
  }
  return {gaps, firstGapAtPx:first, winW:Math.round(w.width),
          halfW:Math.round(half), copies};
}""".replace("STEP", str(STEP_PX))

# Under reduced motion the question is not "does it scroll" — on a wide
# screen ten prices already fit and there is nothing to scroll, which the
# first version of this check reported as a failure. The question is whether
# EVERY tick can be REACHED: scroll the strip to its end and require the last
# one fully inside the window, and at scroll 0 require the first one. That is
# what the historical bug broke — width:auto shrank the track so
# scrollWidth == clientWidth while the items past the edge were clipped and
# unreachable.
REDUCED = """()=>{
  const w=document.querySelector('.ticker-win');
  const shown=[...document.querySelectorAll('.tick')]
      .filter(e=>getComputedStyle(e).display!=='none');
  const win=()=>w.getBoundingClientRect();
  // EDGE reachability, not containment: at 360px the first tick is ~282px
  // wide against a 280px window, so it can never fit entirely — and that is
  // not a defect. What matters is that nothing is clipped off the reachable
  // end: scrolled to 0 the first tick must start at or after the window's
  // left edge, and scrolled to the maximum the last must end at or before
  // the right edge.
  const startsAtLeft=el=>el.getBoundingClientRect().left >= win().left-1;
  const endsAtRight=el=>el.getBoundingClientRect().right <= win().right+1;
  w.scrollLeft = w.scrollWidth;            // clamps to the maximum
  const lastReachable = endsAtRight(shown[shown.length-1]);
  const scrolledTo = Math.round(w.scrollLeft);
  w.scrollLeft = 0;
  return {visible: shown.length, scrollW: w.scrollWidth, clientW: w.clientWidth,
          scrolledTo, lastReachable, firstReachableAtStart: startsAtLeft(shown[0])};
}"""


# The gap probe above is blind to everything about INTERACTION — the review
# that found the anchoring bug also pointed out that this check freezes the
# animation and never touches focus or the control, so the whole surface that
# produced the worst defect went untested. These assert the three properties
# that defect turned on.
INTERACTION = """()=>{
  const out={};
  const win=document.querySelector('.ticker-win');
  const tr=document.querySelector('.ticker-track');
  const ticks=[...tr.children];

  // 1. NO TICK IS FOCUSABLE. A tick inside a transform-animated,
  //    overflow-hidden strip cannot be revealed by focus: transform creates
  //    no scrollable overflow, so scrollLeft stays 0 while the element is
  //    drawn at negative x. Measured before the fix: 0px visible past 30% of
  //    the cycle. The board table below is the accessible equivalent.
  out.focusableTicks = ticks.filter(a=>a.tabIndex >= 0).length;
  out.ariaHiddenWindow = win.getAttribute('aria-hidden') === 'true';
  //    aria-hidden must never CONTAIN something focusable.
  out.focusableInsideHidden = out.ariaHiddenWindow
      ? [...win.querySelectorAll('a,button,input,select,textarea,[tabindex]')]
          .filter(el=>el.tabIndex >= 0).length
      : 0;

  // 2. THE STOP CONTROL actually stops it, and works from the keyboard.
  const box=document.querySelector('.tape-stop');
  const lbl=document.querySelector('.tape-btn');
  out.hasControl = !!(box && lbl && lbl.htmlFor === box.id);
  out.controlFocusable = !!box && box.tabIndex >= 0
      && getComputedStyle(box).display !== 'none'
      && getComputedStyle(box).visibility !== 'hidden';
  out.controlHasName = !!(lbl && lbl.textContent.trim().length);
  if (box) {
    box.checked = false;
    out.runningWhenUnchecked =
        getComputedStyle(tr).animationPlayState === 'running';
    box.checked = true;
    out.pausedWhenChecked =
        getComputedStyle(tr).animationPlayState === 'paused';
    box.checked = false;
  }

  // 3. THE DUPLICATE COPIES are hidden under reduced motion by data-dup, not
  //    by an ARIA state that every tick now shares.
  out.dupMarked = ticks.filter(a=>a.dataset.dup).length;
  out.originals = ticks.length - out.dupMarked;
  return out;
}"""

COPIES_SEEN = []


def main():
    fails = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROME)
        for w, h in WIDTHS:
            for reduced in (False, True):
                ctx = br.new_context(
                    viewport={"width": w, "height": h},
                    reduced_motion="reduce" if reduced else "no-preference")
                page = ctx.new_page()
                page.goto(BASE + "/", wait_until="networkidle")
                if reduced:
                    r = page.evaluate(REDUCED)
                    ok = (r["visible"] > 0 and r["lastReachable"]
                          and r["firstReachableAtStart"])
                    span = ("all fit" if r["scrollW"] <= r["clientW"]
                            else "scrolls to " + str(r["scrolledTo"]))
                    print(f"{w:5d} reduced   {r['visible']} ticks, {span}, "
                          f"first+last reachable   {'OK' if ok else 'FAIL'}")
                    if not ok:
                        why = ("no ticks shown" if not r["visible"]
                               else "last tick unreachable at full scroll"
                               if not r["lastReachable"]
                               else "first tick not visible at scroll 0")
                        fails.append((w, "reduced motion: " + why))
                else:
                    bad = []
                    r = None
                    for i in range(SAMPLES):
                        t = i / (SAMPLES - 1)
                        r = page.evaluate(PROBE, t)
                        if r.get("copies") and not COPIES_SEEN:
                            COPIES_SEEN.append(r["copies"])
                        if r.get("err"):
                            print(f"{w:5d} animated  CONFIG ERROR: {r['err']}")
                            fails.append((w, r["err"]))
                            break
                        if r["gaps"]:
                            bad.append((round(t, 2), r["firstGapAtPx"]))
                    if r.get("err"):
                        ctx.close(); continue
                    print(f"{w:5d} animated  window {r['winW']}, copy {r['halfW']}   "
                          + (f"OK — no gap at any of {SAMPLES} offsets" if not bad
                             else f"FAIL — gaps at t={[x[0] for x in bad]}, "
                                  f"first at +{bad[0][1]}px"))
                    if bad:
                        fails.append((w, f"gap from t={bad[0][0]} of the cycle"))
                ctx.close()
        # ---- interaction, once; it does not vary by width ----
        ctx = br.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(BASE + "/", wait_until="networkidle")
        i = page.evaluate(INTERACTION)
        checks = [
            ("no tick is focusable", i["focusableTicks"] == 0,
             f"{i['focusableTicks']} ticks in the tab order"),
            ("the strip is aria-hidden", i["ariaHiddenWindow"], "it is not"),
            ("nothing focusable inside aria-hidden", i["focusableInsideHidden"] == 0,
             f"{i['focusableInsideHidden']} focusable descendants"),
            ("a labelled stop control exists", i["hasControl"] and i["controlHasName"],
             "missing, or its label does not point at it"),
            ("the control is keyboard-focusable", i["controlFocusable"],
             "it is hidden from the keyboard"),
            ("unchecked -> running", i.get("runningWhenUnchecked"), "it was not running"),
            ("checked -> paused", i.get("pausedWhenChecked"), "it did not pause"),
            ("repeats marked with data-dup", i["dupMarked"] == i["originals"] * (COPIES_SEEN[0] - 1)
             if COPIES_SEEN else True,
             f"{i['dupMarked']} marked against {i['originals']} originals"),
        ]
        print()
        for name, ok, why in checks:
            print(f"      {'OK  ' if ok else 'FAIL'}  {name}" + ("" if ok else f" — {why}"))
            if not ok:
                fails.append(("interaction", name + ": " + why))
        ctx.close()
        br.close()
    if fails:
        print(f"\n✗ {len(fails)} tape failure(s):")
        for w, why in fails:
            print(f"    {w}px  {why}")
        return 1
    print(f"\n✓ the tape covers its window at all {SAMPLES} sampled offsets, at "
          f"{len(WIDTHS)} widths, and every tick is reachable under reduced motion")
    return 0


if __name__ == "__main__":
    sys.exit(main())
