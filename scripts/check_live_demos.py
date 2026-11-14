#!/usr/bin/env python3
"""Qualify committed Flow WASM demos and optionally execute them in Chromium.

Static qualification covers every published manifest entry. Browser mode executes
all matching pages (or one deterministic shard), without substituting JS demos.
"""
import argparse
from contextlib import contextmanager
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading


ROOT = Path(__file__).resolve().parents[1]
WASM = ROOT / "site" / "wasm"


class GalleryLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.runs = []

    def handle_starttag(self, tag, attrs):
        if tag == "button":
            attrs = dict(attrs)
            if attrs.get("data-run"):
                self.runs.append(attrs["data-run"])


class ScriptSources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            source = dict(attrs).get("src")
            if source:
                self.sources.append(source)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def qualified_path(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError("Path escapes root: " + relative)
    return path


def static_check(wiki=None):
    manifest = read_json(WASM / "manifest.json")
    entries = manifest["entries"]
    gallery = GalleryLinks()
    gallery_html = (WASM / "index.html").read_text(encoding="utf-8")
    gallery.feed(gallery_html)
    runs = gallery.runs
    errors = []
    for control in ("modal", "demoSearch", "matchCount", "share"):
        if 'id="' + control + '"' not in gallery_html:
            errors.append("gallery missing required control #" + control)
    names = set()
    pages = set()
    categories = {category["id"] for category in manifest["categories"]}
    actual_bytes = 0

    for entry in entries:
        name = entry["name"]
        page = entry.get("page", name + "/index.html")
        if name in names:
            errors.append("duplicate name " + name)
        names.add(name)
        if entry["category"] not in categories:
            errors.append(name + ": unknown category " + entry["category"])
        if entry["status"] != "ok":
            errors.append(name + ": manifest reports " + entry["status"])
            continue
        if page in pages:
            errors.append("duplicate page " + page)
        pages.add(page)
        if runs.count(page) != 1:
            errors.append(name + ": expected one gallery Run button for " + page)
        if not (ROOT / entry["source"]).is_file():
            errors.append(name + ": missing Flow source " + entry["source"])
        try:
            html_file = qualified_path(WASM, page)
            js_file = qualified_path(html_file.parent, name + ".js")
            wasm_file = qualified_path(html_file.parent, name + ".wasm")
            if not html_file.is_file() or not js_file.is_file() or not wasm_file.is_file():
                errors.append(name + ": HTML, JavaScript or WASM missing")
                continue
            html = html_file.read_text(encoding="utf-8")
            scripts = ScriptSources()
            scripts.feed(html)
            if name + ".js" not in scripts.sources:
                errors.append(name + ": generated HTML does not load its JS")
            has_factory = "createFlowModule(" in html or "createFlowThreaded(" in html
            if not has_factory or 'id="status"' not in html:
                errors.append(name + ": missing runtime startup/status controls")
            if wasm_file.open("rb").read(8)[:4] != b"\x00asm":
                errors.append(name + ": invalid WASM magic")
            if entry["js_bytes"] != js_file.stat().st_size:
                errors.append(name + ": manifest JS byte count is stale")
            if entry["wasm_bytes"] != wasm_file.stat().st_size:
                errors.append(name + ": manifest WASM byte count is stale")
            actual_bytes += js_file.stat().st_size + wasm_file.stat().st_size
            if wiki:
                for rel in (page, name + "/" + name + ".js", name + "/" + name + ".wasm"):
                    if not (wiki / "wasm" / rel).is_file():
                        errors.append(name + ": not packaged in wiki: wasm/" + rel)
        except (OSError, ValueError, UnicodeError) as exc:
            errors.append(name + ": " + str(exc))

    unexpected = set(runs) - pages
    if unexpected:
        errors.append("unindexed Run buttons: " + ", ".join(sorted(unexpected)))
    if manifest["examples"] != len(entries) or manifest["built"] != len(pages) or manifest["failed"] != 0:
        errors.append("manifest summary does not match published entries")
    if manifest["total_bytes"] != actual_bytes:
        errors.append("manifest total byte count is stale")

    nav = read_json(ROOT / "docs" / "nav.json")
    links = [item for section in nav["sections"] for item in section.get("items", [])]
    if not any(item.get("path") == "wasm/index.html" and item.get("external") for item in links):
        errors.append("docs sidebar has no live gallery route")
    catalog = read_json(ROOT / "docs" / "demos" / "catalog.json")
    for collection in catalog["collections"]:
        for key in ("page", "preview"):
            target = ROOT / "docs" / "demos" / collection[key]
            if not target.is_file():
                errors.append(collection["id"] + ": broken gallery " + key + ": " + str(target))
    if wiki and not (wiki / "wasm" / "index.html").is_file():
        errors.append("wiki does not contain live gallery index")

    print("Static live gallery: %d entries, %d routes, %d WASM bytes" %
          (len(entries), len(runs), actual_bytes))
    for error in errors:
        print("FAIL: " + error)
    if errors:
        raise SystemExit("%d live-demo qualification errors" % len(errors))
    return entries


class IsolatedHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        super().end_headers()

    def log_message(self, format, *args):
        pass


@contextmanager
def serving_site():
    handler = partial(IsolatedHandler, directory=str(ROOT / "site"))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:%d" % server.server_port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def browser_check(entries, shard_index, shard_count, names, timeout):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Browser qualification requires pip install playwright and playwright install chromium") from exc

    selected = [entry for pos, entry in enumerate(entries)
                if pos % shard_count == shard_index and
                (not names or entry["name"] in names)]
    if not selected:
        raise SystemExit("No demos matched this browser shard")

    failures = []
    with serving_site() as base, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context()
        # Exercise the gallery route and search once per shard.
        gallery = context.new_page()
        gallery.goto(base + "/wasm/index.html#" + selected[0]["name"], wait_until="domcontentloaded")
        try:
            gallery.locator("#modal.open").wait_for(timeout=timeout)
            actual = gallery.locator("#frame").get_attribute("src") or ""
            if not actual.startswith(selected[0]["name"] + "/index.html?autostart=1"):
                failures.append("Gallery deep link routes to wrong demo: " + actual)
            gallery.locator("#close").click()
            if gallery.locator("#modal").get_attribute("class") == "open":
                failures.append("Gallery close button does not close modal")
            gallery.locator("#demoSearch").fill(selected[0]["name"])
            visible = gallery.locator(".card:visible").count()
            if visible < 1:
                failures.append("Gallery search hides its exact match")
        except Exception as exc:
            failures.append("Gallery routing/search: " + str(exc))
        gallery.close()

        for entry in selected:
            name = entry["name"]
            page = context.new_page()
            bad_responses = []
            page.on("response", lambda response: bad_responses.append(response.url) if response.status >= 400 and
                    (response.url.endswith(".wasm") or response.url.endswith(".js")) else None)
            try:
                page.goto(base + "/wasm/" + entry["page"] + "?autostart=1",
                          wait_until="domcontentloaded", timeout=timeout)
                page.wait_for_function(
                    """() => {
                      const s = (document.getElementById('status')?.textContent || '').trim();
                      return /^(running|finished after|exit -?[0-9]+|failed to load)/.test(s);
                    }""", timeout=timeout)
                status = (page.locator("#status").inner_text() or "").strip()
                if status.startswith("failed") or bad_responses:
                    raise AssertionError("status=" + status + ", missing=" + str(bad_responses))
                if entry["gfx"]:
                    if page.locator("canvas").count() != 1:
                        raise AssertionError("no graphics canvas")
                    dimensions = page.locator("canvas").evaluate("(el) => [el.width, el.height]")
                    if min(dimensions) <= 0:
                        raise AssertionError("invalid canvas size")
                print("PASS %s: %s" % (name, status), flush=True)
            except Exception as exc:
                failures.append(name + ": " + str(exc).splitlines()[0])
                print("FAIL " + name + ": " + str(exc).splitlines()[0], flush=True)
            finally:
                page.close()
        browser.close()

    print("Browser shard %d/%d: tested %d, failed %d" %
          (shard_index + 1, shard_count, len(selected), len(failures)))
    if failures:
        raise SystemExit("\n".join(failures))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki", type=Path, help="also validate deployed wiki bundle")
    parser.add_argument("--browser", action="store_true", help="execute real WASM pages in Chromium")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--name", action="append", default=[], help="select one or more examples")
    parser.add_argument("--timeout-ms", type=int, default=25000)
    args = parser.parse_args()
    if args.shard_count < 1 or not 0 <= args.shard_index < args.shard_count:
        parser.error("invalid shard selection")
    entries = static_check(args.wiki)
    if args.browser:
        browser_check(entries, args.shard_index, args.shard_count, set(args.name), args.timeout_ms)


if __name__ == "__main__":
    main()
