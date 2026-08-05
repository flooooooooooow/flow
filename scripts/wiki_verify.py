#!/usr/bin/env python3
"""Smoke-test the built wiki shell in a real browser.

Checks the things that are easy to break silently in a client-rendered docs
site: console errors, syntax highlighting, callouts, code copy buttons,
TOC scroll-spy, and contrast of the hero call-to-action.
"""
import sys

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8899/"


def luminance(rgb):
    def chan(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def parse_rgb(value):
    nums = value[value.index("(") + 1:value.index(")")].split(",")
    return tuple(int(float(n)) for n in nums[:3])


def main() -> int:
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch()

        for theme in ("dark", "light"):
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            errors = []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))

            page.goto(BASE, wait_until="networkidle")
            page.evaluate(f"localStorage.setItem('flow-wiki-theme','{theme}')")
            page.reload(wait_until="networkidle")
            page.wait_for_timeout(900)

            def check(name, ok, detail=""):
                if not ok:
                    failures.append(f"[{theme}] {name} {detail}".strip())

            check("no console errors", not errors, str(errors[:3]))

            # Hero headline must survive the H1 promotion logic.
            check("hero title visible", page.locator(".wiki-hero-title").is_visible())

            # Primary CTA must not be accent-on-accent.
            cta = page.locator(".wiki-cta-primary").first
            fg = parse_rgb(cta.evaluate("e => getComputedStyle(e).color"))
            bg = parse_rgb(cta.evaluate("e => getComputedStyle(e).backgroundColor"))
            ratio = contrast(fg, bg)
            check("CTA contrast >= 4.5", ratio >= 4.5, f"got {ratio:.2f}")

            # Body text contrast against the page canvas.
            body_fg = parse_rgb(page.evaluate("getComputedStyle(document.body).color"))
            body_bg = parse_rgb(page.evaluate("getComputedStyle(document.body).backgroundColor"))
            body_ratio = contrast(body_fg, body_bg)
            check("body contrast >= 7", body_ratio >= 7, f"got {body_ratio:.2f}")

            # Flow syntax highlighting actually produced tokens.
            tokens = page.locator(".wiki-hero-code .hljs-built_in").count()
            check("flow syntax tokens", tokens > 0, f"got {tokens}")

            # Callouts converted, no raw [!tip] left in the text.
            raw = page.evaluate("document.getElementById('markdownContent').innerText.includes('[!')")
            check("no raw admonition markers", not raw)
            check("admonition rendered", page.locator(".admonition").count() >= 2)

            # The empty warning bar bug.
            banner_shown = page.evaluate(
                "getComputedStyle(document.getElementById('versionBanner')).display !== 'none'"
            )
            check("version banner hidden on latest", not banner_shown)

            # Code blocks get a header + working copy button.
            check("code block chrome", page.locator(".code-block .code-copy").count() > 0)

            page.goto(BASE + "#LANGUAGE_SPEC.md", wait_until="networkidle")
            page.wait_for_timeout(900)
            check("no duplicate lead", page.evaluate(
                "(() => {const l=document.getElementById('docLead');"
                "const f=document.querySelector('#markdownContent > *:not(h1)');"
                "return !l || l.hidden || !f || f.textContent.trim() !== l.textContent.trim();})()"
            ))
            # Scroll over the article, not the sidebar, so the page scrolls.
            page.mouse.move(700, 500)
            for _ in range(6):
                page.mouse.wheel(0, 400)
                page.wait_for_timeout(120)
            page.wait_for_timeout(700)
            active = page.locator("#pageToc a.active").count()
            check("toc scroll-spy active", active == 1, f"got {active}")
            progress = page.evaluate(
                "getComputedStyle(document.getElementById('readProgress')).transform"
            )
            check("read progress advances", progress not in ("none", "matrix(0, 0, 0, 1, 0, 0)"), progress)

            page.close()

        browser.close()

    if failures:
        print("FAIL")
        for f in failures:
            print("  -", f)
        return 1
    print("All wiki checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
