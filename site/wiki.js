/* Flow Wiki — client-side documentation shell */

let navData = null;
let searchIndex = [];
let versionsData = null;
let currentPath = null;
let activeTab = 'all';
let flatNav = [];
let selectedVersion = null;
let searchFilter = 'all';
let pagefindApi = null;
let searchRenderToken = 0;
let searchFocusIndex = -1;

const VERSION_STORAGE_KEY = 'flow-wiki-version';
const THEME_STORAGE_KEY = 'flow-wiki-theme';

const SEARCH_CATEGORIES = [
    { id: 'all', label: 'All' },
    { id: 'guide', label: 'Guides' },
    { id: 'reference', label: 'Reference' },
    { id: 'tutorial', label: 'Tutorials' },
    { id: 'proof', label: 'Proofs' },
    { id: 'tooling', label: 'Tooling' },
];

marked.setOptions({
    gfm: true,
    breaks: false,
    langPrefix: 'language-',
});

function getPreferredTheme() {
    try {
        const stored = localStorage.getItem(THEME_STORAGE_KEY);
        if (stored === 'light' || stored === 'dark') return stored;
    } catch (_) { /* ignore */ }
    return 'dark';
}

function applyTheme(theme) {
    const next = theme === 'light' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try {
        localStorage.setItem(THEME_STORAGE_KEY, next);
    } catch (_) { /* ignore */ }
    const btn = document.getElementById('themeToggle');
    if (btn) {
        btn.setAttribute('aria-pressed', next === 'light' ? 'true' : 'false');
        btn.title = next === 'light' ? 'Switch to dark theme' : 'Switch to light theme';
    }
}

function toggleTheme() {
    applyTheme(getPreferredTheme() === 'light' ? 'dark' : 'light');
}

function initTheme() {
    applyTheme(getPreferredTheme());
    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);
}

async function tryInitPagefind() {
    try {
        const base = new URL('.', window.location.href);
        const mod = await import(new URL('pagefind/pagefind.js', base).href);
        await mod.options({ bundlePath: new URL('pagefind/', base).href });
        mod.init();
        pagefindApi = mod;
        return true;
    } catch (_) {
        pagefindApi = null;
        return false;
    }
}

async function init() {
    initTheme();
    const [navRes, searchRes, verRes] = await Promise.all([
        fetch('wiki-nav.json'),
        fetch('search-index.json'),
        fetch('versions.json'),
    ]);
    navData = await navRes.json();
    searchIndex = await searchRes.json();
    versionsData = await verRes.json();
    await tryInitPagefind();
    buildFlatNav();
    renderVersionPicker();
    renderTabs();
    renderSidebar();
    bindEvents();
    routeFromHash();
}

function versionSlug(id) {
    return id.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function getSelectedVersion() {
    if (!versionsData) return null;
    return versionsData.versions.find((v) => v.id === selectedVersion)
        || versionsData.versions.find((v) => v.latest)
        || versionsData.versions[0];
}

function renderVersionPicker() {
    const select = document.getElementById('versionSelect');
    if (!select || !versionsData) return;

    select.innerHTML = '';
    const group = document.createElement('optgroup');
    group.label = 'Documentation';

    for (const v of versionsData.versions) {
        const opt = document.createElement('option');
        opt.value = v.id;
        const tag = v.latest ? ' (latest)' : v.archived ? '' : ' — snapshot TBD';
        opt.textContent = `${v.label}${tag}`;
        group.appendChild(opt);
    }
    select.appendChild(group);

    const changelogOpt = document.createElement('option');
    changelogOpt.value = '__changelog__';
    changelogOpt.textContent = '── Changelog ──';
    changelogOpt.disabled = true;
    select.appendChild(changelogOpt);

    const viewLog = document.createElement('option');
    viewLog.value = '__view_changelog__';
    viewLog.textContent = 'View full changelog';
    select.appendChild(viewLog);

    const releases = document.createElement('option');
    releases.value = '__view_releases__';
    releases.textContent = 'Release history';
    select.appendChild(releases);

    const fromUrl = new URLSearchParams(window.location.search).get('v');
    const stored = localStorage.getItem(VERSION_STORAGE_KEY);
    selectedVersion = fromUrl || stored || versionsData.current;
    if (!versionsData.versions.some((v) => v.id === selectedVersion)) {
        selectedVersion = versionsData.current;
    }
    select.value = selectedVersion;
    updateVersionBanner();
}

function updateVersionBanner() {
    const banner = document.getElementById('versionBanner');
    if (!banner || !versionsData) return;

    const current = getSelectedVersion();
    const latest = versionsData.versions.find((v) => v.latest);

    if (!current || current.latest) {
        banner.hidden = true;
        banner.innerHTML = '';
        return;
    }

    banner.hidden = false;
    const slug = versionSlug(current.id);
    banner.innerHTML = `
        <span>Viewing <strong>${current.label}</strong> release notes context.
        Full docs archive not published yet — content reflects <strong>${latest?.label || 'latest'}</strong>.</span>
        <button type="button" class="banner-action" data-goto-changelog="${slug}">Release notes →</button>
        <button type="button" class="banner-action" data-reset-version>Back to latest</button>
    `;

    banner.querySelector('[data-goto-changelog]')?.addEventListener('click', () => {
        loadDoc(`project/CHANGELOG.md#v-${slug}`);
    });
    banner.querySelector('[data-reset-version]')?.addEventListener('click', () => {
        setVersion(versionsData.current);
    });
}

function setVersion(versionId) {
    selectedVersion = versionId;
    localStorage.setItem(VERSION_STORAGE_KEY, versionId);
    const select = document.getElementById('versionSelect');
    if (select) select.value = versionId;

    const url = new URL(window.location.href);
    if (versionId === versionsData.current) {
        url.searchParams.delete('v');
    } else {
        url.searchParams.set('v', versionId);
    }
    history.replaceState(null, '', url.pathname + url.search + url.hash);
    updateVersionBanner();
}

function buildFlatNav() {
    flatNav = [];
    for (const section of navData.sections) {
        for (const item of section.items) {
            if (!item.external) flatNav.push({ ...item, section: section.title });
        }
    }
}

function renderTabs() {
    const bar = document.getElementById('tabBar');
    bar.innerHTML = '';
    for (const tab of navData.tabs) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'tab-btn' + (tab.id === activeTab ? ' active' : '');
        btn.textContent = tab.label;
        btn.dataset.tab = tab.id;
        btn.addEventListener('click', () => setTab(tab.id));
        bar.appendChild(btn);
    }
}

function setTab(tabId) {
    activeTab = tabId;
    renderTabs();
    renderSidebar();
}

function sectionVisible(section) {
    if (activeTab === 'all') return true;
    return section.tab === activeTab;
}

function renderSidebar() {
    const nav = document.getElementById('sidebarNav');
    nav.innerHTML = '';

    for (const section of navData.sections) {
        if (!sectionVisible(section)) continue;

        const wrap = document.createElement('div');
        wrap.className = 'sidebar-section' + (section.collapsed ? ' collapsed' : '');

        const header = document.createElement('button');
        header.type = 'button';
        header.className = 'sidebar-section-header';
        header.innerHTML = `<span>${section.title}</span><span class="chevron">▼</span>`;
        header.addEventListener('click', () => wrap.classList.toggle('collapsed'));
        wrap.appendChild(header);

        const ul = document.createElement('ul');
        ul.className = 'sidebar-items';

        for (const item of section.items) {
            const li = document.createElement('li');
            const a = document.createElement('a');
            const label = document.createElement('span');
            label.textContent = item.label;
            a.appendChild(label);

            if (item.badge) {
                const badge = document.createElement('span');
                badge.className = 'item-badge';
                badge.textContent = item.badge;
                a.appendChild(badge);
            }

            if (item.external) {
                a.href = item.path;
            } else {
                a.href = '#';
                if (item.path === currentPath) a.classList.add('active');
                a.addEventListener('click', (e) => {
                    e.preventDefault();
                    loadDoc(item.path);
                    closeMobileSidebar();
                });
            }
            li.appendChild(a);
            ul.appendChild(li);
        }

        wrap.appendChild(ul);
        nav.appendChild(wrap);
    }
}

function setBreadcrumb(path) {
    const el = document.getElementById('breadcrumb');
    const parts = path.split('/');
    const crumbs = [];

    crumbs.push(`<a href="#" data-crumb="wiki-home.md">Docs</a>`);

    let acc = '';
    for (let i = 0; i < parts.length - 1; i++) {
        acc += (acc ? '/' : '') + parts[i];
        const label = parts[i].replace(/-/g, ' ');
        crumbs.push(`<span class="sep">/</span><span>${label}</span>`);
    }
    const file = parts[parts.length - 1].replace(/\.(md|ebnf)$/, '');
    crumbs.push(`<span class="sep">/</span><span>${file}</span>`);

    el.innerHTML = crumbs.join(' ');
    el.querySelector('[data-crumb]')?.addEventListener('click', (e) => {
        e.preventDefault();
        loadDoc(navData.default || 'wiki-home.md');
    });
}

function renderPager(path) {
    const pager = document.getElementById('docPager');
    const idx = flatNav.findIndex((n) => n.path === path);
    if (idx < 0) {
        pager.hidden = true;
        return;
    }

    pager.hidden = false;
    pager.innerHTML = '';

    if (idx > 0) {
        const prev = flatNav[idx - 1];
        pager.appendChild(makePagerLink(prev, 'prev'));
    }
    if (idx < flatNav.length - 1) {
        const next = flatNav[idx + 1];
        pager.appendChild(makePagerLink(next, 'next'));
    }
}

function makePagerLink(item, dir) {
    const a = document.createElement('a');
    a.className = `pager-link ${dir}`;
    a.href = '#';
    a.innerHTML = `<span class="pager-label">${dir === 'prev' ? 'Previous' : 'Next'}</span><span class="pager-title">${item.label}</span>`;
    a.addEventListener('click', (e) => {
        e.preventDefault();
        loadDoc(item.path);
    });
    return a;
}

/** GitHub/GFM-style heading id (matches LANGUAGE_SPEC.md TOC anchors). */
function headingSlug(text) {
    return String(text || '')
        .trim()
        .toLowerCase()
        .replace(/[^\w\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-|-$/g, '');
}

function assignHeadingIds(container) {
    const used = new Set(
        [...container.querySelectorAll('[id]')].map((el) => el.id).filter(Boolean)
    );
    container.querySelectorAll('h2, h3').forEach((h, i) => {
        if (h.id) {
            used.add(h.id);
            return;
        }
        let id = headingSlug(h.textContent) || `heading-${i}`;
        if (used.has(id)) {
            let n = 1;
            while (used.has(`${id}-${n}`)) n += 1;
            id = `${id}-${n}`;
        }
        used.add(id);
        h.id = id;
    });
}

let tocObserver = null;

function buildPageToc(container) {
    const tocCol = document.getElementById('tocColumn');
    const tocNav = document.getElementById('pageToc');
    assignHeadingIds(container);
    const headings = [...container.querySelectorAll('h2, h3')];

    tocObserver?.disconnect();
    tocObserver = null;

    if (headings.length < 2) {
        tocCol.hidden = true;
        return;
    }

    tocCol.hidden = false;
    tocNav.innerHTML = '';

    const links = new Map();
    headings.forEach((h) => {
        const li = document.createElement('li');
        if (h.tagName === 'H3') li.className = 'toc-h3';
        const a = document.createElement('a');
        a.href = `#${h.id}`;
        a.textContent = h.textContent;
        a.addEventListener('click', (e) => {
            e.preventDefault();
            h.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
        li.appendChild(a);
        tocNav.appendChild(li);
        links.set(h.id, a);
    });

    spyOnHeadings(headings, links, tocCol);
}

/** Highlights the TOC entry for the heading nearest the top of the viewport. */
function spyOnHeadings(headings, links, tocCol) {
    const visible = new Set();

    const setActive = () => {
        let id = null;
        if (visible.size) {
            id = headings.find((h) => visible.has(h.id))?.id || null;
        } else {
            // Nothing intersecting (long section) — fall back to the last heading passed.
            const top = window.scrollY + parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop || '0') + 4;
            for (const h of headings) {
                if (h.getBoundingClientRect().top + window.scrollY <= top) id = h.id;
            }
        }
        for (const [key, a] of links) a.classList.toggle('active', key === id);

        const active = id && links.get(id);
        if (active && tocCol.scrollHeight > tocCol.clientHeight) {
            const box = active.getBoundingClientRect();
            const col = tocCol.getBoundingClientRect();
            if (box.top < col.top || box.bottom > col.bottom) {
                active.scrollIntoView({ block: 'nearest' });
            }
        }
    };

    tocObserver = new IntersectionObserver((entries) => {
        for (const entry of entries) {
            if (entry.isIntersecting) visible.add(entry.target.id);
            else visible.delete(entry.target.id);
        }
        setActive();
    }, { rootMargin: '-15% 0px -70% 0px', threshold: 0 });

    headings.forEach((h) => tocObserver.observe(h));
    setActive();
}

function updateReadProgress() {
    const bar = document.getElementById('readProgress');
    if (!bar) return;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const ratio = max > 20 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    bar.style.transform = `scaleX(${ratio})`;
}

function renderMath(el) {
    if (typeof renderMathInElement === 'function') {
        renderMathInElement(el, {
            delimiters: [
                { left: '$$', right: '$$', display: true },
                { left: '$', right: '$', display: false },
            ],
            throwOnError: false,
        });
    }
}

function highlightCode(el) {
    el.querySelectorAll('pre code').forEach((block) => {
        if (block.className.includes('language-')) {
            hljs.highlightElement(block);
        } else {
            block.classList.add('language-flow');
            hljs.highlightElement(block);
        }
    });
}

function wireInternalLinks(container, basePath) {
    container.querySelectorAll('a[href]').forEach((a) => {
        const href = a.getAttribute('href');
        if (!href || href.startsWith('http') || href.startsWith('#') || href.startsWith('mailto:')) return;
        const resolved = resolveRelative(basePath, href);
        a.setAttribute('href', `#${encodeURIComponent(resolved)}`);
        const docPath = resolved.split('#')[0];
        if (/\.(md|proof\.md|ebnf)$/.test(docPath)) {
            a.addEventListener('click', (e) => {
                e.preventDefault();
                loadDoc(resolved);
            });
        }
    });
}

function rewriteMediaUrls(container, basePath) {
    container.querySelectorAll('img[src]').forEach((img) => {
        const src = img.getAttribute('src');
        if (!src || /^(https?:|data:|\/\/)/i.test(src)) return;
        img.setAttribute('src', resolveRelative(basePath, src));
    });
}

function looksLikeHtmlDocument(text) {
    const head = String(text || '').slice(0, 240).trim().toLowerCase();
    return head.startsWith('<!doctype html') || head.startsWith('<html');
}

async function loadDoc(path) {
    let anchor = '';
    const hashIdx = path.indexOf('#');
    if (hashIdx >= 0) {
        anchor = path.slice(hashIdx + 1);
        path = path.slice(0, hashIdx);
    }

    currentPath = path;
    const content = document.getElementById('markdownContent');
    const titleEl = document.getElementById('docTitle');
    const leadEl = document.getElementById('docLead');

    content.innerHTML = '<p class="loading">Loading…</p>';
    titleEl.textContent = '';
    leadEl.hidden = true;
    updateEditLink(null);
    document.getElementById('tocColumn').hidden = true;

    setBreadcrumb(path);
    renderSidebar();
    renderPager(path);

    if (path.endsWith('.html')) {
        window.location.href = path;
        return;
    }

    try {
        const response = await fetch(path);
        if (!response.ok) throw new Error(`Not found (${response.status})`);
        const text = await response.text();
        // nginx try_files falls back to index.html with HTTP 200 — never render that as a doc
        if (looksLikeHtmlDocument(text)) {
            throw new Error('Not found (got site shell HTML instead of the document)');
        }

        if (path.endsWith('.ebnf')) {
            const page = renderEbnfPage(text);
            content.innerHTML = '';
            content.appendChild(page);
            bindGrammarPage(content);
            document.getElementById('tocColumn').hidden = true;
        } else if (path.endsWith('.yaml')) {
            content.innerHTML = `<pre class="code-panel"><code class="language-yaml">${escapeHtml(text)}</code></pre>`;
            highlightCode(content);
        } else {
            content.innerHTML = marked.parse(text);
            transformAdmonitions(content);
            annotateChangelogHeadings(content);
            rewriteMediaUrls(content, path);
            wireInternalLinks(content, path);
            renderMath(content);
            highlightCode(content);
            if (path.startsWith('tutorials/')) {
                initTutorialRunners(content, { autoMain: true });
            }
            // After the runners claim their blocks, so interactive embeds keep
            // their own chrome instead of getting a second header.
            enhanceCodeBlocks(content);
            wrapTables(content);
            buildPageToc(content);
            addHeadingAnchors(content);
            if (anchor) {
                const target = document.getElementById(anchor);
                if (target) setTimeout(() => target.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);
            }
        }

        let displayTitle;
        if (path.endsWith('.ebnf')) {
            displayTitle = 'Formal Grammar (EBNF)';
        } else {
            const h1 = content.querySelector('h1');
            displayTitle = h1 ? h1.textContent : path.split('/').pop().replace(/\.[^.]+$/, '');
        }
        titleEl.textContent = displayTitle;
        updateEditLink(path);

        if (path.endsWith('.proof.md')) addBadge(titleEl, 'PROOF', 'proof-badge');
        else if (path.endsWith('.ebnf')) addBadge(titleEl, 'EBNF', 'grammar-badge');
        else if (path.endsWith('language/grammar.md')) addBadge(titleEl, 'GRAMMAR', 'grammar-badge');
        else if (path.endsWith('LANGUAGE_SPEC.md')) addBadge(titleEl, 'SPEC', 'spec-badge');
        else if (/^language\/(verification|epistemology|claim-coordinates|math-proof-book|mathlib-equivalence-toc)\.md$/.test(path)) {
            addBadge(titleEl, 'LIBRARY', 'proof-badge');
        }

        if (!path.endsWith('.ebnf')) {
            const firstP = content.querySelector('blockquote, p');
            if (firstP && firstP.textContent.length < 220) {
                leadEl.textContent = firstP.textContent;
                leadEl.hidden = false;
                // Only a leading subtitle gets promoted into the header; drop
                // the original so it does not read twice.
                const lead = [...content.children].find((el) => el.tagName !== 'H1');
                if (lead === firstP) firstP.remove();
            }
        }

        document.body.classList.toggle('page-home', path === 'wiki-home.md');
        document.body.classList.toggle('page-wide', path.endsWith('.ebnf'));
        if (path === 'wiki-home.md') {
            // The home page's only H1 *is* the hero headline — keep it. Any
            // stray H1 outside the hero would duplicate .doc-title, so drop it.
            const hero = content.querySelector('.wiki-hero');
            const h1 = content.querySelector('h1');
            if (hero && h1 && !hero.contains(h1)) h1.remove();
        }

        const loc = anchor ? `${path}#${anchor}` : path;
        history.replaceState(null, '', `#${encodeURIComponent(loc)}`);
        document.title = `${displayTitle} — Flow Docs`;
        if (!anchor) window.scrollTo({ top: 0, behavior: 'instant' });
        updateReadProgress();
    } catch (err) {
        document.body.classList.remove('page-home', 'page-wide');
        content.innerHTML = renderNotFound(path, err.message);
    }
}

function transformAdmonitions(container) {
    container.querySelectorAll('blockquote').forEach((bq) => {
        const first = bq.querySelector('p');
        if (!first) return;

        // The marker sits in the paragraph's leading text node. Strip it there
        // rather than dropping the whole paragraph, because the rest of that
        // first paragraph usually carries the callout's prose and links.
        const lead = first.firstChild;
        if (!lead || lead.nodeType !== Node.TEXT_NODE) return;
        const m = lead.nodeValue.match(/^\s*\[!(note|tip|warning|important|caution)\]([^\n]*)(?:\n|$)/i);
        if (!m) return;

        const kind = m[1].toLowerCase();
        const title = m[2].trim() || kind;
        lead.nodeValue = lead.nodeValue.slice(m[0].length);
        if (!first.textContent.trim() && !first.firstElementChild) first.remove();

        const body = document.createElement('div');
        body.className = 'admonition-body';
        while (bq.firstChild) body.appendChild(bq.firstChild);
        const wrap = document.createElement('div');
        wrap.className = `admonition admonition-${kind}`;
        wrap.innerHTML = `<div class="admonition-title">${escapeHtml(title)}</div>`;
        wrap.appendChild(body);
        bq.replaceWith(wrap);
    });
}

/* ── Content enhancement ── */

const LANG_LABELS = {
    sh: 'shell', bash: 'shell', zsh: 'shell', console: 'shell',
    js: 'javascript', ts: 'typescript', py: 'python',
    md: 'markdown', yml: 'yaml', 'c++': 'cpp',
};

function enhanceCodeBlocks(container) {
    container.querySelectorAll('pre').forEach((pre) => {
        if (pre.closest('.code-block, .flow-runner')) return;
        if (pre.classList.contains('wiki-hero-code') || pre.classList.contains('ebnf-block')) return;
        const code = pre.querySelector('code');
        if (!code) return;

        const cls = [...code.classList].find((c) => c.startsWith('language-'));
        const raw = cls ? cls.slice('language-'.length) : '';
        const lang = LANG_LABELS[raw] || raw;

        const wrap = document.createElement('div');
        wrap.className = 'code-block';
        if (raw) wrap.dataset.lang = raw;

        const head = document.createElement('div');
        head.className = 'code-block-head';
        const label = document.createElement('span');
        label.className = 'code-lang';
        label.textContent = lang || 'code';
        head.appendChild(label);

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'code-copy';
        btn.textContent = 'Copy';
        btn.setAttribute('aria-label', 'Copy code to clipboard');
        btn.addEventListener('click', () => copyToClipboard(btn, code.textContent));
        head.appendChild(btn);

        pre.replaceWith(wrap);
        wrap.appendChild(head);
        wrap.appendChild(pre);
    });
}

async function copyToClipboard(btn, text) {
    try {
        await navigator.clipboard.writeText(text);
    } catch (_) {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); } catch (__) { /* give up quietly */ }
        ta.remove();
    }
    btn.textContent = 'Copied';
    btn.classList.add('copied');
    clearTimeout(btn._resetTimer);
    btn._resetTimer = setTimeout(() => {
        btn.textContent = 'Copy';
        btn.classList.remove('copied');
    }, 1600);
}

/** Wide tables need their own scroll container so they never blow out the column. */
function wrapTables(container) {
    container.querySelectorAll('table').forEach((table) => {
        if (table.closest('.table-wrap')) return;
        const wrap = document.createElement('div');
        wrap.className = 'table-wrap';
        table.replaceWith(wrap);
        wrap.appendChild(table);
    });
}

function addHeadingAnchors(container) {
    container.querySelectorAll('h2[id], h3[id], h4[id]').forEach((h) => {
        if (h.querySelector('.heading-anchor')) return;
        const a = document.createElement('a');
        a.className = 'heading-anchor';
        a.href = `#${encodeURIComponent(currentPath)}`;
        a.textContent = '#';
        a.setAttribute('aria-label', `Link to “${h.textContent.trim()}”`);
        a.addEventListener('click', (e) => {
            e.preventDefault();
            const loc = `#${encodeURIComponent(`${currentPath}#${h.id}`)}`;
            history.replaceState(null, '', loc);
            h.scrollIntoView({ behavior: 'smooth', block: 'start' });
            navigator.clipboard?.writeText(new URL(loc, window.location.href).href).catch(() => {});
        });
        h.prepend(a);
    });
}

function renderNotFound(path, message) {
    return `
        <div class="not-found-panel">
            <h2>Page not found</h2>
            <p>Could not load <code>${escapeHtml(path)}</code>${message ? ` — ${escapeHtml(message)}` : ''}.</p>
            <div class="not-found-links">
                <a href="#" class="wiki-cta wiki-cta-primary" data-goto="wiki-home.md">Home</a>
                <a href="#" class="wiki-cta" data-goto="getting-started.md">Quick Start</a>
                <a href="#" class="wiki-cta" data-goto="tutorials/beginner.md">Tutorials</a>
                <a href="#" class="wiki-cta" data-goto="third-party/flow-verify-catalog.md">Proof catalog</a>
            </div>
        </div>
    `;
}

function resolveRelative(base, href) {
    if (!href) return href;
    if (/^(https?:|mailto:|#)/i.test(href)) return href;
    if (href.startsWith('/')) return href.replace(/^\//, '');

    // Bare filenames / ./foo → resolve against the current document directory
    // (proof diagrams: prop-04….proof.svg next to the .proof.md)
    if (href.startsWith('./') || !href.includes('/')) {
        const baseParts = base.split('/');
        baseParts.pop();
        for (const part of href.replace(/^\.\//, '').split('/')) {
            if (part === '..') baseParts.pop();
            else if (part && part !== '.') baseParts.push(part);
        }
        return baseParts.join('/');
    }

    // Catalog / index links are written as wiki-root paths (third-party/…).
    // Only ../… walks from the current document.
    if (!href.startsWith('../')) {
        return href;
    }

    const baseParts = base.split('/');
    baseParts.pop();
    for (const part of href.split('/')) {
        if (part === '..') baseParts.pop();
        else if (part && part !== '.') baseParts.push(part);
    }
    return baseParts.join('/');
}

function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function addBadge(parent, label, className) {
    const badge = document.createElement('span');
    badge.className = className;
    badge.textContent = label;
    parent.appendChild(badge);
}

function annotateChangelogHeadings(container) {
    container.querySelectorAll('h2').forEach((h2) => {
        const m = h2.textContent.match(/\[([^\]]+)\]/);
        if (m) h2.id = `v-${versionSlug(m[1])}`;
    });
}

function routeFromHash() {
    const raw = window.location.hash.slice(1);
    const hash = raw ? decodeURIComponent(raw) : '';
    // Legacy /flow/#viewer bookmark from the old Umbra docs shell
    if (!hash || hash === 'viewer') {
        loadDoc(navData.default || 'wiki-home.md');
        return;
    }
    loadDoc(hash);
}

/* ── Search ── */
function openSearch() {
    const overlay = document.getElementById('searchOverlay');
    overlay.hidden = false;
    const input = document.getElementById('searchInput');
    input.value = '';
    input.focus();
    searchFocusIndex = -1;
    if (pagefindApi && typeof pagefindApi.init === 'function') {
        try { pagefindApi.init(); } catch (_) { /* already inited */ }
    }
    renderSearchFilters();
    renderSearchResults('');
}

function renderSearchFilters() {
    const el = document.getElementById('searchFilters');
    if (!el) return;
    el.innerHTML = '';
    for (const cat of SEARCH_CATEGORIES) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'search-filter' + (searchFilter === cat.id ? ' active' : '');
        btn.textContent = cat.label;
        btn.addEventListener('click', () => {
            searchFilter = cat.id;
            renderSearchFilters();
            renderSearchResults(document.getElementById('searchInput').value);
        });
        el.appendChild(btn);
    }
}

function closeSearch() {
    document.getElementById('searchOverlay').hidden = true;
}

function pagefindUrlToWikiPath(url) {
    if (!url) return '';
    let path = url.replace(/^\//, '');
    try {
        if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('file:')) {
            path = new URL(url).pathname.replace(/^\//, '');
        }
    } catch (_) { /* keep path */ }
    // Stubs are written as "<wiki-path>.html" under _pagefind_src/
    if (path.endsWith('.html')) path = path.slice(0, -5);
    // Drop accidental site prefixes if the index was built with absolute paths
    for (const prefix of ['flow/', 'transpile/', 'build/wiki/', '_pagefind_src/']) {
        if (path.startsWith(prefix)) path = path.slice(prefix.length);
    }
    return path;
}

function searchButtons() {
    return [...document.querySelectorAll('#searchResults li button:not([disabled])')];
}

function setSearchFocus(index) {
    const buttons = searchButtons();
    if (!buttons.length) {
        searchFocusIndex = -1;
        return;
    }
    searchFocusIndex = (index + buttons.length) % buttons.length;
    buttons.forEach((b, i) => b.classList.toggle('focused', i === searchFocusIndex));
    buttons[searchFocusIndex].scrollIntoView({ block: 'nearest' });
}

function moveSearchFocus(delta) {
    setSearchFocus(searchFocusIndex < 0 ? (delta > 0 ? 0 : -1) : searchFocusIndex + delta);
}

function activateSearchFocus() {
    const buttons = searchButtons();
    (buttons[searchFocusIndex] || buttons[0])?.click();
}

function renderSearchHitList(hits) {
    const ul = document.getElementById('searchResults');
    ul.innerHTML = '';
    for (const hit of hits) {
        const li = document.createElement('li');
        const btn = document.createElement('button');
        const cat = hit.category ? `<span class="result-cat">${escapeHtml(hit.category)}</span>` : '';
        const excerpt = hit.excerpt
            ? `<span class="result-excerpt">${hit.excerpt}</span>`
            : '';
        btn.innerHTML = `${cat}<span class="result-title">${escapeHtml(hit.title)}</span>`
            + `<span class="result-path">${escapeHtml(hit.path)}</span>${excerpt}`;
        btn.addEventListener('click', () => {
            closeSearch();
            if (hit.path.endsWith('.html') && !hit.path.endsWith('.proof.md.html')) {
                window.location.href = hit.path;
                return;
            }
            loadDoc(hit.path);
        });
        li.appendChild(btn);
        ul.appendChild(li);
    }
    if (!hits.length) {
        ul.innerHTML = '<li class="search-empty">No matching pages. Try a different term or category.</li>';
        searchFocusIndex = -1;
        return;
    }
    setSearchFocus(0);
}

function scoreLocalSearchEntry(entry, q, terms) {
    const title = (entry.title || '').toLowerCase();
    const path = (entry.path || '').toLowerCase();
    const text = (entry.text || '').toLowerCase();
    const hay = `${title} ${text} ${path}`;
    let score = 0;
    if (title === q) score += 100;
    if (title.startsWith(q)) score += 40;
    if (title.includes(q)) score += 30;
    if (path.includes(q)) score += 12;
    if (hay.includes(q)) score += 8;
    for (const term of terms) {
        if (!term) continue;
        if (title.includes(term)) score += 10;
        else if (path.includes(term)) score += 4;
        else if (text.includes(term)) score += 2;
    }
    // Prefer shorter, more specific docs slightly over huge proof dumps when tied
    if (entry.category === 'tutorial') score += 3;
    if (entry.category === 'reference' || entry.category === 'guide') score += 2;
    return score;
}

function localSearchHits(query) {
    const q = query.toLowerCase().trim();
    const terms = q.split(/\s+/).filter(Boolean);
    return searchIndex
        .map((entry) => ({ entry, score: scoreLocalSearchEntry(entry, q, terms) }))
        .filter((h) => h.score > 0)
        .filter((h) => searchFilter === 'all' || h.entry.category === searchFilter)
        .sort((a, b) => b.score - a.score || a.entry.title.localeCompare(b.entry.title))
        .slice(0, 12)
        .map(({ entry }) => ({
            path: entry.path,
            title: entry.title,
            category: entry.category,
            excerpt: '',
        }));
}

async function pagefindSearchHits(query) {
    if (!pagefindApi) return null;
    const opts = {};
    if (searchFilter !== 'all') {
        opts.filters = { category: searchFilter };
    }
    const search = await pagefindApi.debouncedSearch(query, opts, 120);
    if (search === null) return null; // superseded by a newer query
    const raw = await Promise.all(search.results.slice(0, 12).map((r) => r.data()));
    return raw.map((data) => ({
        path: pagefindUrlToWikiPath(data.url),
        title: (data.meta && data.meta.title) || pagefindUrlToWikiPath(data.url),
        category: (data.meta && data.meta.category)
            || (data.filters && data.filters.category && data.filters.category[0])
            || '',
        // Pagefind excerpts encode entities and may include <mark>; safe for innerHTML
        excerpt: data.excerpt || '',
    })).filter((h) => h.path);
}

async function renderSearchResults(query) {
    const ul = document.getElementById('searchResults');
    const q = query.trim();
    ul.innerHTML = '';
    if (!q) return;

    const token = ++searchRenderToken;
    if (pagefindApi) {
        try {
            const hits = await pagefindSearchHits(q);
            if (token !== searchRenderToken) return;
            if (hits === null) return;
            if (hits.length) {
                renderSearchHitList(hits);
                return;
            }
            // Empty Pagefind result — fall through to local index
        } catch (_) {
            // fall through to local
        }
    }
    if (token !== searchRenderToken) return;
    renderSearchHitList(localSearchHits(q));
}

function setMobileSidebar(open) {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    const toggle = document.getElementById('sidebarToggle');
    sidebar.classList.toggle('open', open);
    document.body.classList.toggle('sidebar-open', open);
    if (backdrop) backdrop.hidden = !open;
    if (toggle) toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
}

function closeMobileSidebar() {
    setMobileSidebar(false);
}

function githubEditUrl(path) {
    const base = 'https://github.com/abhishekshivakumar/transpile/edit/main/';
    if (path === 'project/language-roadmap.md') return `${base}ROADMAP.md`;
    if (path === 'project/benchmark-results.md') return `${base}benchmarks/suite/RESULTS.md`;
    if (path.startsWith('third-party/flow-verify/proofs/lib/')) {
        const rel = path.replace('third-party/flow-verify/proofs/lib/', '');
        return `${base}lib/verify/${rel}`;
    }
    if (path.startsWith('third-party/flow-verify/proofs/examples/')) {
        const rel = path.replace('third-party/flow-verify/proofs/examples/', '');
        return `${base}examples/verify/${rel}`;
    }
    if (path.startsWith('project/')) {
        return `${base}docs/${path}`;
    }
    return `${base}docs/${path}`;
}

function updateEditLink(path) {
    const el = document.getElementById('docEditLink');
    if (!el) return;
    if (!path || path.endsWith('.ebnf') || path.endsWith('.html')) {
        el.hidden = true;
        return;
    }
    el.href = githubEditUrl(path);
    el.hidden = false;
}

function bindEvents() {
    document.getElementById('versionSelect')?.addEventListener('change', (e) => {
        const val = e.target.value;
        if (val === '__view_changelog__') {
            e.target.value = selectedVersion;
            loadDoc('project/CHANGELOG.md');
            return;
        }
        if (val === '__view_releases__') {
            e.target.value = selectedVersion;
            loadDoc('releases.md');
            return;
        }
        setVersion(val);
    });

    document.getElementById('searchTrigger').addEventListener('click', openSearch);
    document.getElementById('searchOverlay').addEventListener('click', (e) => {
        if (e.target.id === 'searchOverlay') closeSearch();
    });
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', (e) => {
        const value = e.target.value;
        if (pagefindApi && typeof pagefindApi.preload === 'function' && value.trim()) {
            pagefindApi.preload(value.trim());
        }
        renderSearchResults(value);
    });

    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown') { e.preventDefault(); moveSearchFocus(1); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); moveSearchFocus(-1); }
        else if (e.key === 'Enter') { e.preventDefault(); activateSearchFocus(); }
    });
    document.getElementById('sidebarToggle').addEventListener('click', () => {
        const open = !document.getElementById('sidebar').classList.contains('open');
        setMobileSidebar(open);
    });
    document.getElementById('sidebarBackdrop')?.addEventListener('click', closeMobileSidebar);

    document.querySelectorAll('[data-path]').forEach((a) => {
        if (a.closest('.markdown-body')) return;
        a.addEventListener('click', (e) => {
            e.preventDefault();
            loadDoc(a.dataset.path);
        });
    });

    document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            openSearch();
        }
        if (e.key === 'Escape') {
            closeSearch();
            closeMobileSidebar();
        }
    });

    document.getElementById('markdownContent').addEventListener('click', (e) => {
        const link = e.target.closest('[data-goto]');
        if (!link) return;
        e.preventDefault();
        loadDoc(link.dataset.goto);
    });

    window.addEventListener('hashchange', routeFromHash);

    let progressQueued = false;
    window.addEventListener('scroll', () => {
        if (progressQueued) return;
        progressQueued = true;
        requestAnimationFrame(() => {
            progressQueued = false;
            updateReadProgress();
        });
    }, { passive: true });
    window.addEventListener('resize', updateReadProgress, { passive: true });
    updateReadProgress();
}

document.addEventListener('DOMContentLoaded', init);