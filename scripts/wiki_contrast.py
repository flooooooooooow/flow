#!/usr/bin/env python3
"""Audit rendered text contrast across the wiki and tutorials shells.

Walks every visible text-bearing element, resolves its effective background by
compositing ancestor backgrounds, and reports anything under the WCAG AA bar.
"""
import sys

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8899/"

TARGETS = [
    ("docs-home", BASE),
    ("docs-spec", BASE + "#LANGUAGE_SPEC.md"),
    ("tutorials", BASE + "tutorials/"),
    ("tut-doc", BASE + "#tutorials/effects-basics.md"),
]

AUDIT_JS = r"""
() => {
  const parse = (c) => {
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  };
  const over = (fg, bg) => ({
    r: fg.r * fg.a + bg.r * (1 - fg.a),
    g: fg.g * fg.a + bg.g * (1 - fg.a),
    b: fg.b * fg.a + bg.b * (1 - fg.a),
    a: 1,
  });
  const lum = (c) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  };
  const ratio = (a, b) => {
    const la = lum(a), lb = lum(b);
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  };

    // Returns null when an ancestor paints a gradient/image, since the real
  // backdrop is then unknowable from computed styles alone.
  const effectiveBg = (el) => {
    let acc = null;
    let node = el;
    while (node && node !== document.documentElement.parentNode) {
      const cs = getComputedStyle(node);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0) acc = acc ? over(acc, c) : c;
      if (acc && acc.a >= 1) return acc;
      node = node.parentElement;
    }
    const base = { r: 255, g: 255, b: 255, a: 1 };
    return acc ? over(acc, base) : base;
  };

  const out = [];
  const seen = new Set();
  for (const el of document.querySelectorAll('body *')) {
    // Only elements that render their own text.
    const own = [...el.childNodes]
      .filter((n) => n.nodeType === 3 && n.nodeValue.trim())
      .map((n) => n.nodeValue.trim())
      .join(' ');
    if (!own) continue;

    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) < 0.15) continue;
    const box = el.getBoundingClientRect();
    if (box.width < 2 || box.height < 2) continue;
    // Gradient-clipped text legitimately reports transparent colour.
    if (cs.webkitBackgroundClip === 'text' || cs.backgroundClip === 'text') continue;

    const fgRaw = parse(cs.color);
    if (!fgRaw) continue;
    const bg = effectiveBg(el);
    if (!bg) continue;
    const fg = fgRaw.a < 1 ? over(fgRaw, bg) : fgRaw;
    const r = ratio(fg, bg);

    const size = parseFloat(cs.fontSize);
    const weight = parseInt(cs.fontWeight, 10) || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    const need = large ? 3.0 : 4.5;
    if (r >= need) continue;

    const key = el.className + '|' + own.slice(0, 30);
    if (seen.has(key)) continue;
    seen.add(key);

    out.push({
      sel: el.tagName.toLowerCase() + (el.className && typeof el.className === 'string'
        ? '.' + el.className.trim().split(/\s+/).join('.') : ''),
      text: own.slice(0, 46),
      ratio: Math.round(r * 100) / 100,
      need,
      color: cs.color,
    });
  }
  return out.sort((a, b) => a.ratio - b.ratio);
}
"""


def main() -> int:
    total = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for theme in ("dark", "light"):
            for name, url in TARGETS:
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                page.goto(BASE, wait_until="domcontentloaded")
                page.evaluate(f"localStorage.setItem('flow-wiki-theme','{theme}')")
                page.goto(url, wait_until="domcontentloaded")
                page.reload(wait_until="networkidle")
                page.wait_for_timeout(1400)
                issues = page.evaluate(AUDIT_JS)
                if issues:
                    print(f"\n=== {theme} / {name} — {len(issues)} low-contrast")
                    for i in issues[:14]:
                        print(f"  {i['ratio']:>5} (need {i['need']}) {i['sel'][:64]}")
                        print(f"        text={i['text']!r} color={i['color']}")
                total += len(issues)
                page.close()
        browser.close()
    print(f"\nTotal low-contrast elements: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
