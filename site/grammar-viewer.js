/* EBNF grammar viewer — sections, rule index, syntax colours */

function parseEbnfSections(text) {
    const lines = text.split('\n');
    const sections = [];
    let current = { title: 'Overview', lines: [] };

    for (const line of lines) {
        if (/^# ={5,}/.test(line)) continue;
        if (/^# [A-Z]/.test(line) && !line.includes('::=')) {
            if (current.lines.length) sections.push(current);
            current = { title: line.replace(/^#\s*/, '').trim(), lines: [] };
        } else {
            current.lines.push(line);
        }
    }
    if (current.lines.length) sections.push(current);
    return sections;
}

function highlightEbnfLine(line) {
    if (!line.trim()) return '&nbsp;';
    if (line.trim().startsWith('#')) {
        return `<span class="ebnf-comment">${escapeHtml(line)}</span>`;
    }
    if (line.includes('::=')) {
        const [lhs, rhs] = line.split('::=');
        return `<span class="ebnf-rule-name">${escapeHtml(lhs.trim())}</span><span class="ebnf-def"> ::= </span><span class="ebnf-rhs">${highlightRhs(rhs || '')}</span>`;
    }
    return `<span class="ebnf-rhs">${highlightRhs(line)}</span>`;
}

function highlightRhs(text) {
    let s = escapeHtml(text);
    s = s.replace(/"([^"]*)"/g, '<span class="ebnf-terminal">"$1"</span>');
    s = s.replace(/\b([A-Z][A-Z0-9_]*)\b/g, '<span class="ebnf-nt">$1</span>');
    s = s.replace(/(\||ε)/g, '<span class="ebnf-alt">$1</span>');
    return s;
}

function collectRules(text) {
    const rules = [];
    for (const line of text.split('\n')) {
        const m = line.match(/^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*::=/);
        if (m) rules.push(m[1]);
    }
    return [...new Set(rules)].sort();
}

function renderEbnfPage(text) {
    const sections = parseEbnfSections(text);
    const rules = collectRules(text);

    let html = `
    <div class="grammar-page">
      <div class="grammar-legend">
        <h2>Notation</h2>
        <div class="legend-grid">
          <span><code class="ebnf-rule-name">rule</code> nonterminal</span>
          <span><code class="ebnf-terminal">"token"</code> terminal</span>
          <span><code class="ebnf-alt">|</code> alternative</span>
          <span><code class="ebnf-alt">ε</code> empty</span>
        </div>
        <p class="grammar-meta">${rules.length} rules · ${sections.length} sections · <a href="#" data-path="language/grammar.md">Readable grammar guide →</a></p>
      </div>
      <div class="grammar-layout">
        <aside class="grammar-index">
          <p class="grammar-index-label">Rules</p>
          <input type="search" class="grammar-rule-search" id="ruleSearch" placeholder="Filter rules…">
          <ul class="grammar-rule-list" id="ruleList"></ul>
        </aside>
        <div class="grammar-sections" id="grammarSections"></div>
      </div>
    </div>`;

    const wrapper = document.createElement('div');
    wrapper.innerHTML = html;

    const ruleList = wrapper.querySelector('#ruleList');
    for (const rule of rules) {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = `#rule-${rule}`;
        a.textContent = rule;
        a.dataset.rule = rule;
        li.appendChild(a);
        ruleList.appendChild(li);
    }

    const sectionsEl = wrapper.querySelector('#grammarSections');
    for (const section of sections) {
        const sec = document.createElement('section');
        sec.className = 'ebnf-section';
        const h2 = document.createElement('h2');
        h2.textContent = section.title;
        sec.appendChild(h2);

        const pre = document.createElement('pre');
        pre.className = 'ebnf-block';
        const code = document.createElement('code');
        let lineNum = 1;
        for (const line of section.lines) {
            const row = document.createElement('div');
            row.className = 'ebnf-line';
            const m = line.match(/^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*::=/);
            if (m) row.id = `rule-${m[1]}`;

            const num = document.createElement('span');
            num.className = 'ebnf-ln';
            num.textContent = String(lineNum++);
            row.appendChild(num);

            const content = document.createElement('span');
            content.className = 'ebnf-content';
            content.innerHTML = highlightEbnfLine(line);
            row.appendChild(content);
            code.appendChild(row);
        }
        pre.appendChild(code);
        sec.appendChild(pre);
        sectionsEl.appendChild(sec);
    }

    return wrapper;
}

function bindGrammarPage(container) {
    const search = container.querySelector('#ruleSearch');
    const ruleList = container.querySelector('#ruleList');
    if (!search || !ruleList) return;

    search.addEventListener('input', () => {
        const q = search.value.toLowerCase();
        ruleList.querySelectorAll('li').forEach((li) => {
            const name = li.textContent.toLowerCase();
            li.hidden = q && !name.includes(q);
        });
    });

    ruleList.querySelectorAll('a').forEach((a) => {
        a.addEventListener('click', (e) => {
            e.preventDefault();
            const el = container.querySelector(a.getAttribute('href'));
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    });

    container.querySelectorAll('[data-path]').forEach((a) => {
        a.addEventListener('click', (e) => {
            e.preventDefault();
            if (typeof loadDoc === 'function') loadDoc(a.dataset.path);
        });
    });
}