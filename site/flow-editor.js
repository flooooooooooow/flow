/* Syntax-highlighted Flow editor + a structural analyser used to explain a
 * program instead of dumping it as one opaque block.
 *
 * The editor is a transparent <textarea> laid over a highlighted <pre>, so the
 * code stays editable while always rendering with real syntax colours, line
 * numbers, and highlightable line ranges.
 */

function highlightFlow(code) {
    if (typeof hljs !== 'undefined') {
        try {
            return hljs.highlight(code, { language: 'flow', ignoreIllegals: true }).value;
        } catch (_) { /* fall through to plain text */ }
    }
    return code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function createFlowEditor(source, options = {}) {
    const wrap = document.createElement('div');
    wrap.className = 'flow-code';
    wrap.innerHTML = `
        <div class="flow-code-gutter" data-gutter aria-hidden="true"></div>
        <div class="flow-code-area">
            <div class="flow-code-marks" data-marks aria-hidden="true"></div>
            <pre class="flow-code-view" data-view aria-hidden="true"><code class="language-flow"></code></pre>
            <textarea class="flow-code-input" data-input spellcheck="false" wrap="off"
                autocapitalize="off" autocomplete="off" autocorrect="off"></textarea>
        </div>
    `;

    const gutter = wrap.querySelector('[data-gutter]');
    const marks = wrap.querySelector('[data-marks]');
    const view = wrap.querySelector('[data-view]');
    const viewCode = view.querySelector('code');
    const input = wrap.querySelector('[data-input]');

    input.value = source;
    input.setAttribute('aria-label', options.label || 'Flow source code');
    if (options.readOnly) input.readOnly = true;

    function lineMetrics() {
        const cs = getComputedStyle(view);
        return {
            height: parseFloat(cs.lineHeight) || 21,
            top: parseFloat(cs.paddingTop) || 0,
        };
    }

    function renderGutter(count) {
        if (gutter.childElementCount === count) return;
        gutter.innerHTML = '';
        for (let i = 1; i <= count; i += 1) {
            const n = document.createElement('span');
            n.className = 'flow-code-ln';
            n.dataset.line = String(i);
            n.textContent = String(i);
            gutter.appendChild(n);
        }
    }

    function render() {
        const code = input.value;
        // Trailing newline keeps the last (empty) line addressable in the view.
        viewCode.innerHTML = highlightFlow(code.endsWith('\n') ? `${code} ` : code);
        const count = code.split('\n').length;
        renderGutter(count);
        // Grow to fit the program so short lessons are not a tall empty box and
        // mid-sized ones do not need scrolling to be read.
        const rows = Math.min(Math.max(count, options.minRows || 8), options.maxRows || 30);
        wrap.style.setProperty('--flow-code-rows', String(rows));
        syncScroll();
    }

    function syncScroll() {
        view.scrollTop = input.scrollTop;
        view.scrollLeft = input.scrollLeft;
        marks.style.transform = `translateY(${-input.scrollTop}px)`;
        gutter.scrollTop = input.scrollTop;
    }

    function highlightLines(start, end) {
        marks.innerHTML = '';
        gutter.querySelectorAll('.flow-code-ln.lit').forEach((n) => n.classList.remove('lit'));
        if (!start) return;

        const { height, top } = lineMetrics();
        const band = document.createElement('div');
        band.className = 'flow-code-mark';
        band.style.top = `${top + (start - 1) * height}px`;
        band.style.height = `${(end - start + 1) * height}px`;
        marks.appendChild(band);

        for (let i = start; i <= end; i += 1) {
            gutter.querySelector(`.flow-code-ln[data-line="${i}"]`)?.classList.add('lit');
        }

        // Bring the range into view if the reader is looking elsewhere.
        const targetTop = (start - 1) * height;
        if (targetTop < input.scrollTop || targetTop > input.scrollTop + input.clientHeight - height * 2) {
            input.scrollTop = Math.max(0, targetTop - height);
            syncScroll();
        }
    }

    input.addEventListener('input', render);
    input.addEventListener('scroll', syncScroll, { passive: true });

    input.addEventListener('keydown', (e) => {
        if (e.key !== 'Tab') return;
        e.preventDefault();
        const { selectionStart: s, selectionEnd: t, value } = input;
        input.value = `${value.slice(0, s)}    ${value.slice(t)}`;
        input.selectionStart = input.selectionEnd = s + 4;
        render();
    });

    render();

    return {
        el: wrap,
        get value() { return input.value; },
        set value(v) { input.value = v; render(); },
        input,
        highlightLines,
        clearHighlight: () => highlightLines(null),
        focus: () => input.focus(),
    };
}

/* ── Program structure ───────────────────────────────────────────────────── */

const TOP_LEVEL_RE = /^(?:export\s+)?(function|struct|enum|effect|capability|trait|impl|flow|extern|import|const|type)\b/;

const KIND_LABEL = {
    function: 'function',
    struct: 'struct',
    enum: 'enum',
    effect: 'effect',
    capability: 'capability',
    trait: 'trait',
    impl: 'impl',
    flow: 'flow',
    extern: 'extern',
    import: 'import',
    const: 'const',
    type: 'type',
};

function countBraces(line) {
    // Braces inside strings and comments must not move the nesting depth.
    const stripped = line
        .replace(/"(?:[^"\\]|\\.)*"/g, '""')
        .replace(/'(?:[^'\\]|\\.)*'/g, "''")
        .replace(/#.*$/, '')
        .replace(/\/\/.*$/, '');
    let delta = 0;
    for (const ch of stripped) {
        if (ch === '{') delta += 1;
        else if (ch === '}') delta -= 1;
    }
    return delta;
}

function truncate(text, max = 46) {
    // A dangling opening brace reads as noise when quoted mid-sentence.
    const t = String(text).trim().replace(/\s*\{$/, '');
    return t.length > max ? `${t.slice(0, max - 1)}…` : t;
}

/** Field/variant names, whether the body is inline or spread over lines. */
function memberNames(header, body) {
    const inline = header.match(/\{(.*)\}/);
    const source = inline
        ? inline[1].split(',')
        : body.map((l) => l.trim());
    return source
        .map((part) => part.trim().match(/^(\w+)\s*[:,]?/))
        .filter(Boolean)
        .map((m) => m[1])
        .filter((n) => n && !/^(function|struct|enum)$/.test(n));
}

/** Plain-language gloss for a single statement, or null if it is not notable. */
function describeStatement(line) {
    const s = line.trim();
    let m;

    if ((m = s.match(/^for\s+(\w+)\s+in\s+(.+?)\s+to\s+(.+?)\s*\{/))) {
        return `Counts ${m[1]} from ${truncate(m[2], 18)} up to ${truncate(m[3], 18)}, repeating the block.`;
    }
    if ((m = s.match(/^for\s+(\w+)\s+in\s+(.+?)\s*\{/))) {
        return `Walks ${m[1]} over ${truncate(m[2], 24)}.`;
    }
    if ((m = s.match(/^while\s+(.+?)\s*\{/))) {
        return `Repeats while ${truncate(m[1], 34)} holds.`;
    }
    if ((m = s.match(/^if\s+(.+?)\s*\{/))) {
        return `Runs only when ${truncate(m[1], 34)}.`;
    }
    if (/^\}\s*else\s*\{/.test(s)) return 'Otherwise, runs this branch instead.';
    if ((m = s.match(/^\}\s*elif\s+(.+?)\s*\{/))) return `Otherwise checks ${truncate(m[1], 30)}.`;
    if ((m = s.match(/^match\s+(.+?)\s*\{/))) return `Branches on the shape of ${truncate(m[1], 26)}.`;
    if ((m = s.match(/^handle\s+(.+?)\s*\{/))) return `Handles the ${truncate(m[1], 26)} effect here.`;
    if ((m = s.match(/^(\w+)\s+evolves\s+as\s+(.+)$/))) {
        return `State ${m[1]} changes at the rate ${truncate(m[2], 30)}.`;
    }
    if ((m = s.match(/^printf\s*\(\s*"((?:[^"\\]|\\.)*)"/))) {
        return `Prints “${truncate(m[1].replace(/\\n/g, ' '), 34)}”.`;
    }
    if ((m = s.match(/^let\s+mut\s+(\w+)\s*:\s*([^=]+?)\s*=\s*(.+)$/))) {
        return `Declares ${m[1]} as a mutable ${m[2].trim()}, starting at ${truncate(m[3], 20)}.`;
    }
    if ((m = s.match(/^let\s+(\w+)\s*:\s*([^=]+?)\s*=\s*(.+)$/))) {
        return `Binds ${m[1]} (${m[2].trim()}, immutable) to ${truncate(m[3], 20)}.`;
    }
    if ((m = s.match(/^return\s+(.+)$/))) {
        return m[1].trim() === '0' ? 'Returns 0 — the exit code meaning success.' : `Returns ${truncate(m[1], 28)}.`;
    }
    if ((m = s.match(/^free\s*\(\s*(\w+)/))) return `Releases the memory held by ${m[1]}.`;
    if ((m = s.match(/^(\w+)\s*\[([^\]]+)\]\s*=\s*(.+)$/))) {
        return `Stores ${truncate(m[3], 16)} at index ${truncate(m[2], 12)} of ${m[1]}.`;
    }
    if ((m = s.match(/^(\w+)\s*=\s*(.+)$/))) return `Updates ${m[1]} to ${truncate(m[2], 24)}.`;
    return null;
}

function describeConstruct(kind, header, body) {
    let m;
    if (kind === 'extern') {
        const fns = body.map((l) => l.match(/function\s+(\w+)/)).filter(Boolean).map((x) => x[1]);
        return fns.length
            ? `Declares ${fns.length} C function${fns.length > 1 ? 's' : ''} the program may call: ${truncate(fns.join(', '), 60)}.`
            : 'Declares external symbols provided by the C runtime.';
    }
    if (kind === 'struct') {
        const fields = memberNames(header, body);
        return fields.length
            ? `A record type holding ${fields.length} field${fields.length > 1 ? 's' : ''}: ${truncate(fields.join(', '), 56)}.`
            : 'Defines a record type.';
    }
    if (kind === 'enum') {
        const variants = memberNames(header, body);
        return variants.length
            ? `A tagged union with ${variants.length} variant${variants.length > 1 ? 's' : ''}: ${truncate(variants.join(', '), 56)}.`
            : 'Defines a tagged union.';
    }
    if (kind === 'effect' || kind === 'capability') {
        const ops = body.map((l) => l.match(/function\s+(\w+)/)).filter(Boolean).map((x) => x[1]);
        return ops.length
            ? `Declares the ${ops.length === 1 ? 'operation' : 'operations'} ${truncate(ops.join(', '), 50)} that handlers must supply.`
            : 'Declares an algebraic effect interface.';
    }
    if (kind === 'flow') {
        const states = body.filter((l) => /^\s*state\b/.test(l)).length;
        const params = body.filter((l) => /^\s*param\b/.test(l)).length;
        return `A dynamical system with ${states} state variable${states === 1 ? '' : 's'} and ${params} parameter${params === 1 ? '' : 's'}.`;
    }
    if (kind === 'import') return `Pulls in ${truncate(header.replace(/^import\s+/, ''), 40)}.`;
    if (kind === 'const') return 'A compile-time constant, fixed for the whole program.';
    if (kind === 'type') return 'A type alias.';

    if (kind === 'function') {
        const name = (header.match(/function\s+(\w+)/) || [])[1] || 'function';
        const rawParams = (header.match(/\(([^)]*)\)/) || ['', ''])[1].trim();
        const ret = (header.match(/->\s*([^{]+)/) || [])[1]?.trim();
        if (name === 'main') {
            return `The entry point. Execution starts here and the ${ret || 'i32'} it returns becomes the exit code.`;
        }
        const params = rawParams ? rawParams.split(',').map((p) => p.trim()).filter(Boolean) : [];
        const takes = params.length
            ? `takes ${params.length} argument${params.length > 1 ? 's' : ''} (${truncate(params.join(', '), 44)})`
            : 'takes no arguments';
        return `A helper that ${takes}${ret ? ` and returns ${ret}` : ''}.`;
    }
    return '';
}

/**
 * Breaks Flow source into explained, line-addressed steps.
 * Returns [{ kind, label, title, detail, start, end, sub: [...] }].
 */
function analyzeFlowProgram(code) {
    const lines = code.split('\n');
    const steps = [];
    let i = 0;

    while (i < lines.length) {
        const raw = lines[i];
        const trimmed = raw.trim();
        const match = trimmed.match(TOP_LEVEL_RE);

        if (!trimmed || !match) {
            i += 1;
            continue;
        }

        const kind = match[1];
        const start = i + 1;
        let depth = countBraces(raw);
        let end = start;

        if (/\{/.test(raw)) {
            while (depth > 0 && end < lines.length) {
                depth += countBraces(lines[end]);
                end += 1;
            }
        }

        const body = lines.slice(start, Math.max(start, end - 1));
        const title = trimmed.replace(/\s*\{\s*$/, '');

        const step = {
            kind,
            label: KIND_LABEL[kind] || kind,
            title: truncate(title, 62),
            detail: describeConstruct(kind, trimmed, body),
            start,
            end,
            sub: [],
        };

        // One level of statement-level commentary inside function bodies.
        if (kind === 'function' || kind === 'flow') {
            let inner = 0;
            for (let j = start; j < end - 1; j += 1) {
                const line = lines[j];
                const text = line.trim();
                if (text && inner === 0) {
                    const detail = describeStatement(line);
                    if (detail) {
                        let subEnd = j + 1;
                        if (/\{\s*$/.test(text)) {
                            let d = countBraces(line);
                            while (d > 0 && subEnd < end - 1) {
                                d += countBraces(lines[subEnd]);
                                subEnd += 1;
                            }
                        }
                        step.sub.push({ title: truncate(text.replace(/\s*\{$/, ''), 54), detail, start: j + 1, end: subEnd });
                    }
                }
                inner += countBraces(line);
                if (inner < 0) inner = 0;
            }
            if (step.sub.length > 10) step.sub = step.sub.slice(0, 10);
        }

        steps.push(step);
        // `end` is 1-based and inclusive, so it is already the next 0-based index.
        i = Math.max(end, start);
    }

    return steps;
}
