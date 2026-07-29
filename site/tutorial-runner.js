/* Embeds interactive Flow compile/run widgets in tutorial pages */

const TUTORIAL_PROGRESS_KEY = 'flow-tutorial-progress';

function createFlowRunner(source, options = {}) {
    const wrap = document.createElement('div');
    wrap.className = 'flow-runner';
    wrap.innerHTML = `
        <div class="flow-runner-header">
            <span class="flow-runner-title">${options.title || 'Try it — compiles in browser'}</span>
            <div class="flow-runner-actions">
                <span class="flow-runner-status">
                    <span class="flow-runner-dot" data-dot></span>
                    <span data-status>Ready</span>
                </span>
                <button type="button" class="flow-runner-btn" data-reset>Reset</button>
                <button type="button" class="flow-runner-btn flow-runner-btn-primary" data-run>Run</button>
            </div>
        </div>
        <div class="flow-runner-body">
            <div class="flow-runner-editor">
                <textarea spellcheck="false" aria-label="Flow source code"></textarea>
            </div>
            <div class="flow-runner-output">
                <div class="flow-runner-tabs" role="tablist">
                    <button type="button" class="flow-runner-tab active" data-tab="output" role="tab">Output</button>
                    <button type="button" class="flow-runner-tab" data-tab="ast" role="tab">AST</button>
                    <button type="button" class="flow-runner-tab" data-tab="c" role="tab">Generated C</button>
                    <button type="button" class="flow-runner-tab" data-tab="mlir" role="tab">MLIR</button>
                </div>
                <pre class="flow-runner-pane success" data-pane="output">Click Run to compile and execute.</pre>
                <pre class="flow-runner-pane" data-pane="ast" hidden></pre>
                <pre class="flow-runner-pane" data-pane="c" hidden></pre>
                <pre class="flow-runner-pane" data-pane="mlir" hidden></pre>
            </div>
        </div>
        <div class="flow-runner-hint">Browser interpreter · <kbd>⌘</kbd>+<kbd>Enter</kbd> to run · not the native compiler</div>
    `;

    const textarea = wrap.querySelector('textarea');
    const original = source.trim();
    textarea.value = original;

    const dot = wrap.querySelector('[data-dot]');
    const status = wrap.querySelector('[data-status]');
    const panes = {
        output: wrap.querySelector('[data-pane="output"]'),
        ast: wrap.querySelector('[data-pane="ast"]'),
        c: wrap.querySelector('[data-pane="c"]'),
        mlir: wrap.querySelector('[data-pane="mlir"]'),
    };

    let activeTab = 'output';

    function setTab(name) {
        activeTab = name;
        wrap.querySelectorAll('.flow-runner-tab').forEach((t) => {
            t.classList.toggle('active', t.dataset.tab === name);
        });
        Object.entries(panes).forEach(([key, el]) => {
            el.hidden = key !== name;
        });
    }

    wrap.querySelectorAll('.flow-runner-tab').forEach((btn) => {
        btn.addEventListener('click', () => setTab(btn.dataset.tab));
    });

    function setState(state, message) {
        dot.className = 'flow-runner-dot' + (state ? ` ${state}` : '');
        status.textContent = message;
    }

    function run() {
        if (!window.FlowCompile) {
            panes.output.textContent = 'Compile engine not loaded.';
            panes.output.className = 'flow-runner-pane error';
            setState('err', 'Missing engine');
            return;
        }

        setState('running', 'Running…');
        const code = textarea.value;

        window.requestAnimationFrame(() => {
            const result = FlowCompile.run(code);
            if (!result.ok) {
                panes.output.textContent = `Error: ${result.error}`;
                panes.output.className = 'flow-runner-pane error';
                panes.ast.textContent = '';
                panes.c.textContent = '';
                panes.mlir.textContent = '';
                setState('err', 'Error');
                setTab('output');
                if (typeof options.onResult === 'function') options.onResult(result, code);
                return;
            }

            panes.output.textContent = result.output;
            panes.output.className = 'flow-runner-pane success';
            panes.ast.textContent = result.ast;
            panes.c.textContent = result.c;
            panes.mlir.textContent = result.mlir;
            setState('ok', 'Success');
            if (activeTab === 'output' || !panes[activeTab].textContent) {
                setTab('output');
            }
            if (typeof options.onResult === 'function') options.onResult(result, code);
        });
    }

    wrap.querySelector('[data-run]').addEventListener('click', run);
    wrap.querySelector('[data-reset]').addEventListener('click', () => {
        textarea.value = original;
        panes.output.textContent = 'Click Run to compile and execute.';
        panes.output.className = 'flow-runner-pane success';
        panes.ast.textContent = '';
        panes.c.textContent = '';
        panes.mlir.textContent = '';
        setState('', 'Ready');
        setTab('output');
    });

    textarea.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            e.preventDefault();
            run();
        }
        // Tab inserts spaces in the editor
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            textarea.value = `${textarea.value.slice(0, start)}    ${textarea.value.slice(end)}`;
            textarea.selectionStart = textarea.selectionEnd = start + 4;
        }
    });

    if (options.autorun) {
        setTimeout(run, 80);
    }

    return wrap;
}

function shouldMakeInteractive(codeEl, options) {
    if (codeEl.classList.contains('run') || codeEl.classList.contains('interactive')) {
        return true;
    }
    if (options.autoMain && /function\s+main\s*\(/.test(codeEl.textContent)) {
        return true;
    }
    return false;
}

function initTutorialRunners(container, options = {}) {
    if (!container || !window.FlowCompile) return;

    const blocks = container.querySelectorAll('pre > code.language-flow');
    blocks.forEach((codeEl) => {
        if (!shouldMakeInteractive(codeEl, options)) return;

        const pre = codeEl.parentElement;
        if (!pre || pre.dataset.flowRunner) return;
        pre.dataset.flowRunner = '1';

        const source = codeEl.textContent;
        const runner = createFlowRunner(source, {
            title: options.title,
            autorun: options.autorun && codeEl.classList.contains('run'),
        });
        pre.replaceWith(runner);
    });
}

function loadTutorialProgress() {
    try {
        return JSON.parse(localStorage.getItem(TUTORIAL_PROGRESS_KEY) || '{}');
    } catch {
        return {};
    }
}

function saveTutorialProgress(map) {
    localStorage.setItem(TUTORIAL_PROGRESS_KEY, JSON.stringify(map));
}

function normalizeOutput(text) {
    return String(text || '').replace(/\r\n/g, '\n').trim();
}

function initTutorialsApp(root) {
    const sidebar = root.querySelector('[data-lessons]');
    const main = root.querySelector('[data-lesson-main]');
    const trackBar = root.querySelector('[data-tracks]');
    const progressEl = root.querySelector('[data-progress]');
    if (!sidebar || !main) return;

    const TRACKS = [
        { id: 'all', label: 'All' },
        { id: 'beginner', label: 'Beginner' },
        { id: 'control', label: 'Control' },
        { id: 'functions', label: 'Functions' },
        { id: 'structs', label: 'Structs' },
        { id: 'arrays', label: 'Arrays' },
        { id: 'strings', label: 'Strings' },
        { id: 'pointers', label: 'Pointers' },
        { id: 'memory', label: 'Memory' },
        { id: 'errors', label: 'Errors' },
        { id: 'intermediate', label: 'Intermediate' },
        { id: 'concurrency', label: 'Concurrency' },
        { id: 'algorithms', label: 'Algorithms' },
        { id: 'systems', label: 'Systems' },
        { id: 'effects-basics', label: 'Effects' },
        { id: 'autodiff-basics', label: 'Autodiff' },
        { id: 'audio-basics', label: 'Audio' },
        { id: 'advanced', label: 'Advanced' },
        { id: 'dynamics', label: 'Dynamics' },
        { id: 'projects', label: 'Projects' },
    ];

    fetch('exercises.json')
        .then((r) => {
            if (!r.ok) throw new Error(`exercises.json ${r.status}`);
            return r.json();
        })
        .then((data) => {
            const lessons = data.lessons || [];
            let activeTrack = 'beginner';
            let activeId = null;
            let progress = loadTutorialProgress();

            function filteredLessons() {
                if (activeTrack === 'all') return lessons;
                return lessons.filter((l) => l.track === activeTrack);
            }

            function updateProgressUi() {
                if (!progressEl) return;
                const done = lessons.filter((l) => progress[l.id]).length;
                const pct = lessons.length ? Math.round((done / lessons.length) * 100) : 0;
                progressEl.innerHTML = `
                    <div class="tutorials-progress-bar"><span style="width:${pct}%"></span></div>
                    <span class="tutorials-progress-label">${done} / ${lessons.length} completed</span>
                `;
            }

            function markComplete(id) {
                progress[id] = true;
                saveTutorialProgress(progress);
                updateProgressUi();
                renderSidebar();
            }

            function renderTracks() {
                if (!trackBar) return;
                trackBar.innerHTML = '';
                for (const track of TRACKS) {
                    const count = track.id === 'all'
                        ? lessons.length
                        : lessons.filter((l) => l.track === track.id).length;
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'tutorials-track' + (track.id === activeTrack ? ' active' : '');
                    btn.textContent = `${track.label} (${count})`;
                    btn.addEventListener('click', () => {
                        activeTrack = track.id;
                        const list = filteredLessons();
                        if (!list.some((l) => l.id === activeId)) {
                            activeId = list[0]?.id || null;
                        }
                        renderTracks();
                        renderSidebar();
                        if (activeId) renderLesson(activeId);
                    });
                    trackBar.appendChild(btn);
                }
            }

            function renderSidebar() {
                sidebar.innerHTML = '';
                const list = filteredLessons();
                let currentSection = '';

                for (const lesson of list) {
                    if (lesson.section && lesson.section !== currentSection) {
                        currentSection = lesson.section;
                        const h = document.createElement('h3');
                        h.className = 'tutorials-section';
                        h.textContent = currentSection;
                        sidebar.appendChild(h);
                    }

                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'tutorials-lesson'
                        + (lesson.id === activeId ? ' active' : '')
                        + (progress[lesson.id] ? ' done' : '');
                    btn.dataset.id = lesson.id;
                    btn.innerHTML = `
                        <span class="tutorials-lesson-mark">${progress[lesson.id] ? '✓' : '○'}</span>
                        <span class="tutorials-lesson-title">${lesson.title}</span>
                    `;
                    btn.addEventListener('click', () => renderLesson(lesson.id));
                    sidebar.appendChild(btn);
                }

                if (!list.length) {
                    sidebar.innerHTML = '<p class="tutorials-empty">No lessons in this track.</p>';
                }
            }

            function renderLesson(id) {
                const list = filteredLessons();
                const lesson = lessons.find((l) => l.id === id);
                if (!lesson) return;
                activeId = id;
                const idx = list.findIndex((l) => l.id === id);
                const prev = idx > 0 ? list[idx - 1] : null;
                const next = idx >= 0 && idx < list.length - 1 ? list[idx + 1] : null;

                renderSidebar();

                const expected = window.FlowCompile
                    ? normalizeOutput(FlowCompile.run(lesson.code).output)
                    : '';

                main.innerHTML = `
                    <div class="tutorials-meta">
                        <span class="tutorials-track-badge">${lesson.track}</span>
                        <span class="tutorials-meta-sep">·</span>
                        <span>${lesson.section || ''}</span>
                        ${progress[lesson.id] ? '<span class="tutorials-done-pill">Completed</span>' : ''}
                    </div>
                    <h1>${lesson.title}</h1>
                    <p class="tutorials-lead">${lesson.description || 'Edit the code and click Run.'}</p>
                    <ol class="tutorials-goals">
                        <li>Read the starter program — what should it print?</li>
                        <li>Click <strong>Run</strong> (or ⌘/Ctrl+Enter).</li>
                        <li>Tweak values / add a <code>printf</code>, then Run again.</li>
                    </ol>
                    <div data-runner-slot></div>
                    <div class="tutorials-check" data-check hidden></div>
                    <div class="tutorials-nav">
                        <button type="button" class="flow-runner-btn" data-prev ${prev ? '' : 'disabled'}>← ${prev ? prev.title : 'Previous'}</button>
                        <button type="button" class="flow-runner-btn flow-runner-btn-primary" data-next ${next ? '' : 'disabled'}>${next ? next.title : 'Next'} →</button>
                    </div>
                `;

                const slot = main.querySelector('[data-runner-slot]');
                const check = main.querySelector('[data-check]');
                const runner = createFlowRunner(lesson.code, {
                    title: `${lesson.track} · live`,
                    onResult(result) {
                        if (!result.ok) {
                            check.hidden = false;
                            check.className = 'tutorials-check fail';
                            check.textContent = 'Compile/run failed — fix the error and try again.';
                            return;
                        }
                        const got = normalizeOutput(result.output);
                        const matched = !expected || got === expected || got.includes(expected.slice(0, Math.min(40, expected.length)));
                        check.hidden = false;
                        if (matched) {
                            check.className = 'tutorials-check pass';
                            check.textContent = 'Nice — output looks good. Lesson marked complete.';
                            markComplete(lesson.id);
                        } else {
                            check.className = 'tutorials-check hint';
                            check.innerHTML = `Ran successfully. Starter output was:<pre>${expected.replace(/</g, '&lt;')}</pre>`;
                            markComplete(lesson.id);
                        }
                    },
                });
                slot.appendChild(runner);

                main.querySelector('[data-prev]')?.addEventListener('click', () => {
                    if (prev) renderLesson(prev.id);
                });
                main.querySelector('[data-next]')?.addEventListener('click', () => {
                    if (next) renderLesson(next.id);
                });

                const url = new URL(window.location.href);
                url.hash = id;
                history.replaceState(null, '', url.pathname + url.search + url.hash);
            }

            const fromHash = decodeURIComponent(window.location.hash.slice(1) || '');
            if (fromHash && lessons.some((l) => l.id === fromHash)) {
                activeId = fromHash;
                activeTrack = lessons.find((l) => l.id === fromHash)?.track || 'beginner';
            } else {
                activeId = filteredLessons()[0]?.id || lessons[0]?.id;
            }

            renderTracks();
            updateProgressUi();
            renderSidebar();
            if (activeId) renderLesson(activeId);
        })
        .catch((err) => {
            main.innerHTML = `<p class="error-msg">Could not load tutorials: ${err.message}</p>`;
        });
}
