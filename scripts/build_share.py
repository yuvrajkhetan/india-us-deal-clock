#!/usr/bin/env python3
"""Regenerate the link-preview image and dated metadata from index.html's data.

Run from anywhere after updating the data block in index.html:
    python3 scripts/build_share.py

It serves the site locally, opens index.html#og in headless Chromium,
screenshots the 1200x630 share card to og.png, then rewrites the share tags
(between <!-- share:start --> and <!-- share:end -->), the structured-data
dateModified, and sitemap.xml with the current reading and date.

It also bakes the computed content (the reading, chances, inputs, events and
scoring) into index.html between <!-- bake:ID --> markers, so search engines
and AI crawlers that do not run JavaScript still see the full page. The page's
script replaces this content on load, so visitors see no difference.
"""
import functools
import html
import http.server
import pathlib
import re
import threading

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://yuvrajkhetan.github.io/india-us-deal-clock/"
INDEX = ROOT / "index.html"
IMAGE = ROOT / "og.png"
BAKE_IDS = ["asof", "watch", "headline", "odds", "deltas", "midnight",
            "inputs", "tip", "events", "factors", "methodTable", "scale"]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve():
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def render():
    server = serve()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        page.goto(f"http://127.0.0.1:{server.server_port}/index.html#og")
        page.wait_for_selector("#ogcard")
        page.evaluate("document.fonts.ready.then(() => true)")
        page.wait_for_timeout(300)
        share = page.evaluate("window.__share")
        page.screenshot(path=str(IMAGE), clip={"x": 0, "y": 0, "width": 1200, "height": 630})
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(f"http://127.0.0.1:{server.server_port}/index.html")
        page.wait_for_selector("#events li")
        baked = page.evaluate("""ids => Object.fromEntries(ids.map(id => [id, document.getElementById(id).innerHTML]))""", BAKE_IDS)
        baked["watch:label"] = page.get_attribute("#watch", "aria-label")
        browser.close()
    server.shutdown()
    return share, baked


def bake(text, baked):
    """Write rendered content between the bake markers so it is readable without JavaScript."""
    for i in BAKE_IDS:
        body = baked[i].replace("<!--", "").replace("-->", "")
        text, n = re.subn(rf"<!--bake:{i}-->.*?<!--/bake:{i}-->",
                          lambda _: f"<!--bake:{i}-->{body}<!--/bake:{i}-->", text, flags=re.S)
        if n != 1:
            raise SystemExit(f"bake marker for #{i} not found in index.html")
    label = html.escape(baked["watch:label"] or "", quote=True)
    text, n = re.subn(r'(id="watch" role="img")(?: aria-label="[^"]*")?', rf'\1 aria-label="{label}"', text)
    if n != 1:
        raise SystemExit("#watch not found in index.html")
    return text


def write_tags(share, baked):
    minutes = share["minutes"]
    unit = "minute" if minutes == 1 else "minutes"
    title = f"India–US Trade Deal Clock: {minutes} {unit} to midnight"
    desc = (f"{share['p90']}% chance the first tranche of the India–US trade deal "
            f"is signed within 90 days. Updated {share['asOfText']}.")
    version = share["asOf"].replace("-", "")
    img = f"{SITE}og.png?v={version}"
    e = lambda s: html.escape(s, quote=True)
    block = "\n".join([
        "<!-- share:start -->",
        f'<meta name="description" content="{e(desc)}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="India–US Trade Deal Clock">',
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
    text, n = re.subn(r"<!-- share:start -->.*?<!-- share:end -->", lambda _: block, text, flags=re.S)
    if n != 1:
        raise SystemExit("share markers not found in index.html")
    text = re.sub(r'"dateModified": "[0-9-]*"', f'"dateModified": "{share["asOf"]}"', text)
    text = bake(text, baked)
    INDEX.write_text(text, encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{SITE}</loc><lastmod>{share['asOf']}</lastmod></url>\n"
        "</urlset>\n", encoding="utf-8")
    return title, desc


if __name__ == "__main__":
    share, baked = render()
    title, desc = write_tags(share, baked)
    print(f"og.png updated: {title}\n{desc}")
