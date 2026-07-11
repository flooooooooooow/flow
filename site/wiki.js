/* Flow Wiki — client-side documentation shell */

let navData = null;
let searchIndex = [];
let versionsData = null;
let currentPath = null;
let activeTab = 'all';
let flatNav = [];
let selectedVersion = null;

const VERSION_STORAGE_KEY = 'flow-wiki-version';

marked.setOptions({
    gfm: true,
    breaks: false,
    langPrefix: 'language-',
    highlight(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
        }
        return hljs.highlightAuto(code).value;
    },
});

async function init() {
    const [navRes, searchRes, verRes] = await Promise.all([
        fetch('wiki-nav.json'),
        fetch('search-index.json'),
        fetch('versions.json'),
    ]);
    navData = await navRes.json();
    searchIndex = await searchRes.json();
    versionsData = await verRes.json();
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

function buildPageToc(container) {
    const tocCol = document.getElementById('tocColumn');
    const tocNav = document.getElementById('pageToc');
    const headings = container.querySelectorAll('h2, h3');

    if (headings.length < 2) {
        tocCol.hidden = true;
        return;
    }

    tocCol.hidden = false;
    tocNav.innerHTML = '';

    headings.forEach((h, i) => {
        const id = h.id || `heading-${i}`;
        h.id = id;
        const li = document.createElement('li');
        if (h.tagName === 'H3') li.className = 'toc-h3';
        const a = document.createElement('a');
        a.href = `#${id}`;
        a.textContent = h.textContent;
        a.addEventListener('click', (e) => {
            e.preventDefault();
            h.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
        li.appendChild(a);
        tocNav.appendChild(li);
    });
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
        if (/\.(md|proof\.md|ebnf)$/.test(resolved)) {
            a.addEventListener('click', (e) => {
                e.preventDefault();
                loadDoc(resolved);
            });
        }
    });
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
            annotateChangelogHeadings(content);
            wireInternalLinks(content, path);
            renderMath(content);
            highlightCode(content);
            if (path.startsWith('tutorials/')) {
                initTutorialRunners(content, { autoMain: true });
            }
            buildPageToc(content);
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
            }
        }

        history.replaceState(null, '', `#${encodeURIComponent(path)}`);
        document.title = `${displayTitle} — Flow Docs`;
        window.scrollTo({ top: 0, behavior: 'instant' });
    } catch (err) {
        content.innerHTML = `<p class="error-msg">Could not load <code>${escapeHtml(path)}</code>: ${escapeHtml(err.message)}</p>`;
    }
}

function resolveRelative(base, href) {
    if (href.startsWith('/')) return href.replace(/^\//, '');
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
    const hash = window.location.hash.slice(1);
    loadDoc(hash ? decodeURIComponent(hash) : (navData.default || 'wiki-home.md'));
}

/* ── Search ── */
function openSearch() {
    const overlay = document.getElementById('searchOverlay');
    overlay.hidden = false;
    const input = document.getElementById('searchInput');
    input.value = '';
    input.focus();
    renderSearchResults('');
}

function closeSearch() {
    document.getElementById('searchOverlay').hidden = true;
}

function renderSearchResults(query) {
    const ul = document.getElementById('searchResults');
    const q = query.toLowerCase().trim();
    ul.innerHTML = '';

    if (!q) return;

    const hits = searchIndex
        .map((entry) => {
            const hay = (entry.title + ' ' + entry.text + ' ' + entry.path).toLowerCase();
            const score = (hay.includes(q) ? 10 : 0)
                + (entry.title.toLowerCase().includes(q) ? 20 : 0)
                + (entry.path.toLowerCase().includes(q) ? 5 : 0);
            return { entry, score };
        })
        .filter((h) => h.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 12);

    for (const { entry } of hits) {
        const li = document.createElement('li');
        const btn = document.createElement('button');
        btn.innerHTML = `<span class="result-title">${escapeHtml(entry.title)}</span><span class="result-path">${escapeHtml(entry.path)}</span>`;
        btn.addEventListener('click', () => {
            closeSearch();
            loadDoc(entry.path);
        });
        li.appendChild(btn);
        ul.appendChild(li);
    }

    if (!hits.length) {
        ul.innerHTML = '<li><button type="button" disabled style="opacity:0.5">No results</button></li>';
    }
}

function closeMobileSidebar() {
    document.getElementById('sidebar').classList.remove('open');
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
    document.getElementById('searchInput').addEventListener('input', (e) => {
        renderSearchResults(e.target.value);
    });
    document.getElementById('sidebarToggle').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('open');
    });

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
        if (e.key === 'Escape') closeSearch();
    });

    window.addEventListener('hashchange', routeFromHash);
}

document.addEventListener('DOMContentLoaded', init);