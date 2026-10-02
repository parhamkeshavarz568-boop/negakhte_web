# negakhte_web

All of negakhte's websites, one folder each, under [`websites/`](websites/).

| Folder | Site | What it is |
|---|---|---|
| [`websites/negakhte_main/`](websites/negakhte_main/) | **نگاخته** | The company site. `home.html` is the homepage; `index.html` is the self-knowledge tests app. |
| [`websites/concept-store/`](websites/concept-store/) | **کانسپت استور** | The concept store: 170 pages built from the shop's price lists and photos. |
| [`websites/ali-optimized/`](websites/ali-optimized/) | **کافه نگاخته** | The café. The live site is the folder's root; `_archive/` keeps older copies and a test page. |
| [`websites/amochini/`](websites/amochini/) | **عمو چینی** (amochini.ir) | Daily prices for ASMCO brake parts (pads, discs, drums) for Chinese cars. |

## Look at one on your computer

Each site runs from its own folder with Python's built-in server, for example:

```powershell
cd negakhte_web\websites\negakhte_main
python -m http.server 8780
```

Then open <http://127.0.0.1:8780/home.html>. The concept store and amochini
serve from their `public\` folder; see each site's own README.

## Make the file to send or upload

| Site | Command (run inside the site's folder) | Result |
|---|---|---|
| negakhte_main | `python tools/make_zip.py` | `dist/negakhte-main.zip` |
| concept-store | `python build/make_upload.py` | `dist/concept-store-upload.zip` |
| amochini | see [its README](websites/amochini/README.md) | the contents of `public/` |
| ali-optimized | zip the folder's root, without `_archive/` | |

Upload zips are rebuilt, never committed (`dist/` is ignored, and so are zips
at the top of the repo).

## Rules that hold across the sites

- **No people in images** on negakhte_main. Its images are objects, light and
  nature (see `websites/negakhte_main/DESIGN.md` §2.5).
- **negakhte_main presents; it does not sell.** No FAQs that answer
  objections, no sign-up steps, no calls to action.
- Persian copy speaks to one person (تو), warmly, not formally.
