#!/usr/bin/env python3
"""Screenshot the built wiki for visual review. Usage: wiki_shots.py <label>"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8899/"
OUT = Path("/tmp/wikishots")

PAGES = [
    ("home", "", 1440, 1000, None),
    ("guide", "#getting-started.md", 1440, 1000, None),
    ("spec", "#LANGUAGE_SPEC.md", 1440, 1000, None),
    ("grammar", "#grammar.ebnf", 1440, 1000, None),
    ("tables", "#comparison.md", 1440, 1000, None),
    ("search", "", 1440, 1000, "search"),
    ("mobile", "", 420, 900, None),
    ("mobile-nav", "", 420, 900, "sidebar"),
]


def shoot(browser, label, name, frag, w, h, action, theme="dark"):
    page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
    page.goto(BASE, wait_until="domcontentloaded")
    page.evaluate(f"localStorage.setItem('flow-wiki-theme','{theme}')")
    # A hash-only navigation would not re-run the inline theme bootstrap.
    page.goto(BASE + frag, wait_until="domcontentloaded")
    page.reload(wait_until="networkidle")
    page.wait_for_timeout(1100)
    if action == "search":
        page.keyboard.press("Meta+k")
        page.wait_for_timeout(250)
        page.keyboard.type("effect")
        page.wait_for_timeout(700)
    elif action == "sidebar":
        page.click("#sidebarToggle")
        page.wait_for_timeout(450)
    page.screenshot(path=str(OUT / f"{label}-{name}.png"))
    page.close()


def main() -> None:
    label = sys.argv[1] if len(sys.argv) > 1 else "shot"
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, frag, w, h, action in PAGES:
            shoot(browser, label, name, frag, w, h, action)
        shoot(browser, label, "light", "", 1440, 1000, None, theme="light")
        shoot(browser, label, "light-spec", "#LANGUAGE_SPEC.md", 1440, 1000, None, theme="light")
        browser.close()
    print(f"wrote {label}-* to {OUT}")


if __name__ == "__main__":
    main()
