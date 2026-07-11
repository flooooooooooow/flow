/* Embeds interactive Flow compile/run widgets in tutorial pages */

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

function initTutorialsApp(root) {
    const sidebar = root.querySelector('[data-lessons]');
    const main = root.querySelector('[data-lesson-main]');
    if (!sidebar || !main) return;

    fetch('tutorials/exercises.json')
        .then((r) => r.json())
        .then((data) => {
            let activeId = data.lessons[0]?.id;

            function renderLesson(id) {
                const lesson = data.lessons.find((l) => l.id === id);
                if (!lesson) return;
                activeId = id;

                sidebar.querySelectorAll('.tutorials-lesson').forEach((btn) => {
                    btn.classList.toggle('active', btn.dataset.id === id);
                });

                main.innerHTML = `
                    <h1>${lesson.title}</h1>
                    <p class="tutorials-lead">${lesson.description || ''}</p>
                    <div data-runner-slot></div>
                `;

                const slot = main.querySelector('[data-runner-slot]');
                const runner = createFlowRunner(lesson.code, { title: lesson.track, autorun: false });
                slot.appendChild(runner);
            }

            data.lessons.forEach((lesson, i) => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'tutorials-lesson' + (i === 0 ? ' active' : '');
                btn.dataset.id = lesson.id;
                btn.textContent = lesson.title;
                btn.addEventListener('click', () => renderLesson(lesson.id));
                sidebar.appendChild(btn);
            });

            renderLesson(activeId);
        })
        .catch((err) => {
            main.innerHTML = `<p class="error-msg">Could not load tutorials: ${err.message}</p>`;
        });
}