#!/usr/bin/env python3
"""Regenerate the link-preview image (og.png) and share tags in index.html.

Run from anywhere after updating the data block in index.html:
    python3 scripts/build_share.py

It opens index.html#og in headless Chromium, screenshots the 1200x630 share
card, and rewrites the tags between <!-- share:start --> and <!-- share:end -->
with the current reading. Fonts are loaded from scripts/fonts (SIL OFL).
"""
import datetime
import html
import pathlib
import re
import shutil
import subprocess

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://yuvrajkhetan.github.io/india-us-deal-clock/"
INDEX = ROOT / "index.html"
IMAGE = ROOT / "og.png"


def install_fonts():
    target = pathlib.Path.home() / ".fonts"
    target.mkdir(exist_ok=True)
    for font in (ROOT / "scripts" / "fonts").glob("*.ttf"):
        shutil.copy(font, target / font.name)
    subprocess.run(["fc-cache", "-f"], check=False, capture_output=True)


def render():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        # Use the local font copies rather than Google Fonts.
        page.route("**/fonts.googleapis.com/**", lambda route: route.abort())
        page.route("**/fonts.gstatic.com/**", lambda route: route.abort())
        page.goto(INDEX.as_uri() + "#og")
        page.wait_for_selector("#ogcard")
        page.evaluate("document.fonts.ready.then(() => true)")
        page.wait_for_timeout(300)
        share = page.evaluate("window.__share")
        page.screenshot(path=str(IMAGE), clip={"x": 0, "y": 0, "width": 1200, "height": 630})
        browser.close()
    return share


def write_tags(share):
    minutes = share["minutes"]
    unit = "minute" if minutes == 1 else "minutes"
    title = f"India–US Deal Clock: {minutes} {unit} to midnight"
    desc = (f"{share['p90']}% chance the first tranche of the India–US trade deal "
            f"is signed within 90 days. Updated {share['asOfText']}.")
    version = share["asOf"].replace("-", "")
    img = f"{SITE}og.png?v={version}"
    e = lambda s: html.escape(s, quote=True)
    block = "\n".join([
        "<!-- share:start -->",
        f'<meta name="description" content="{e(desc)}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="India–US Deal Clock">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(desc)}">',
        f'<meta property="og:url" content="{SITE}">',
        f'<meta property="og:image" content="{img}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{e(f"Clock face showing {minutes} {unit} to midnight")}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{e(title)}">',
        f'<meta name="twitter:description" content="{e(desc)}">',
        f'<meta name="twitter:image" content="{img}">',
        "<!-- share:end -->",
    ])
    text = INDEX.read_text(encoding="utf-8")
    new, n = re.subn(r"<!-- share:start -->.*?<!-- share:end -->", lambda _: block, text, flags=re.S)
    if n != 1:
        raise SystemExit("share markers not found in index.html")
    INDEX.write_text(new, encoding="utf-8")
    return title, desc


if __name__ == "__main__":
    install_fonts()
    share = render()
    title, desc = write_tags(share)
    print(f"og.png updated: {title}\n{desc}")
