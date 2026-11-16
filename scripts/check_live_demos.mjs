#!/usr/bin/env node
// Qualify the published Flow WASM gallery and execute real examples in Chromium.
// The Flow-native recorder, catalog and wiki checks run in CI alongside this harness.
import { createServer } from 'node:http';
import { existsSync, readFileSync, statSync, createReadStream } from 'node:fs';
import { dirname, extname, isAbsolute, join, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const site = join(root, 'site');
const wasm = join(site, 'wasm');

function json(path) {
    return JSON.parse(readFileSync(path, 'utf8'));
}

function confined(base, relative) {
    if (isAbsolute(relative)) {
        throw new Error('Absolute path: ' + relative);
    }
    const path = resolve(base, relative);
    if (path !== base && !path.startsWith(base + sep)) {
        throw new Error('Path escapes root: ' + relative);
    }
    return path;
}

function staticCheck(wiki) {
    const manifest = json(join(wasm, 'manifest.json'));
    const gallery = readFileSync(join(wasm, 'index.html'), 'utf8');
    const runs = [...gallery.matchAll(/<button\b[^>]*\bdata-run="([^"]+)"/g)].map(match => match[1]);
    const errors = [];
    const names = new Set();
    const pages = new Set();
    const categories = new Set(manifest.categories.map(item => item.id));
    let totalBytes = 0;

    for (const id of ['modal', 'demoSearch', 'matchCount', 'share']) {
        if (!gallery.includes('id="' + id + '"')) {
            errors.push('Gallery missing control #' + id);
        }
    }

    for (const entry of manifest.entries) {
        const name = entry.name;
        const page = entry.page || name + '/index.html';
        if (names.has(name)) errors.push('Duplicate name: ' + name);
        names.add(name);
        if (!categories.has(entry.category)) errors.push(name + ': unknown category ' + entry.category);
        if (entry.status !== 'ok') {
            errors.push(name + ': manifest reports status ' + entry.status);
            continue;
        }
        if (pages.has(page)) errors.push('Duplicate page: ' + page);
        pages.add(page);
        if (runs.filter(value => value === page).length !== 1) {
            errors.push(name + ': expected exactly one gallery button for ' + page);
        }
        if (!existsSync(join(root, entry.source))) {
            errors.push(name + ': source missing: ' + entry.source);
        }

        try {
            const htmlFile = confined(wasm, page);
            const dir = dirname(htmlFile);
            const jsFile = confined(dir, name + '.js');
            const wasmFile = confined(dir, name + '.wasm');
            if (![htmlFile, jsFile, wasmFile].every(existsSync)) {
                errors.push(name + ': HTML, JavaScript or WASM is missing');
                continue;
            }
            const html = readFileSync(htmlFile, 'utf8');
            const scriptSources = [...html.matchAll(/<script\b[^>]*\bsrc="([^"]+)"/g)].map(match => match[1]);
            if (!scriptSources.includes(name + '.js')) {
                errors.push(name + ': generated HTML does not load its JavaScript');
            }
            if (!(html.includes('createFlowModule(') || html.includes('createFlowThreaded(')) ||
                !html.includes('id="status"')) {
                errors.push(name + ': missing runtime startup/status controls');
            }
            if (!readFileSync(wasmFile).subarray(0, 4).equals(Buffer.from([0, 97, 115, 109]))) {
                errors.push(name + ': invalid WebAssembly header');
            }
            const jsBytes = statSync(jsFile).size;
            const wasmBytes = statSync(wasmFile).size;
            if (jsBytes !== entry.js_bytes) errors.push(name + ': stale JavaScript byte count');
            if (wasmBytes !== entry.wasm_bytes) errors.push(name + ': stale WASM byte count');
            totalBytes += jsBytes + wasmBytes;
            if (wiki) {
                for (const relative of [page, name + '/' + name + '.js', name + '/' + name + '.wasm']) {
                    if (!existsSync(confined(join(wiki, 'wasm'), relative))) {
                        errors.push(name + ': missing in deployed wiki: ' + relative);
                    }
                }
            }
        } catch (error) {
            errors.push(name + ': ' + error.message);
        }
    }

    for (const run of runs) {
        if (!pages.has(run)) errors.push('Unindexed gallery button: ' + run);
    }
    if (manifest.examples !== manifest.entries.length ||
        manifest.built !== pages.size || manifest.failed !== 0) {
        errors.push('Manifest summary does not match published entries');
    }
    if (manifest.total_bytes !== totalBytes) errors.push('Manifest total byte count is stale');

    const navigation = json(join(root, 'docs/nav.json'));
    const links = navigation.sections.flatMap(section => section.items || []);
    if (!links.some(item => item.path === 'wasm/index.html' && item.external)) {
        errors.push('Documentation sidebar does not link to the live gallery');
    }
    const catalog = json(join(root, 'docs/demos/catalog.json'));
    for (const collection of catalog.collections) {
        for (const key of ['page', 'preview']) {
            const path = join(root, 'docs/demos', collection[key]);
            if (!existsSync(path)) errors.push(collection.id + ': missing ' + key + ' ' + path);
        }
    }
    if (wiki && !existsSync(join(wiki, 'wasm/index.html'))) {
        errors.push('Deployed wiki does not contain the live gallery');
    }

    console.log('Static live gallery: ' + manifest.entries.length + ' entries, ' +
        runs.length + ' routes, ' + totalBytes + ' WASM/JS bytes');
    for (const error of errors) console.error('FAIL: ' + error);
    if (errors.length) throw new Error(errors.length + ' static live-demo qualification errors');
    return manifest.entries;
}

function serveSite(contentRoot = site) {
    const types = {
        '.html': 'text/html; charset=utf-8',
        '.js': 'application/javascript; charset=utf-8',
        '.wasm': 'application/wasm',
        '.json': 'application/json; charset=utf-8',
        '.css': 'text/css; charset=utf-8',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.svg': 'image/svg+xml',
        '.woff2': 'font/woff2',
        '.gif': 'image/gif',
    };
    const server = createServer((request, response) => {
        response.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
        response.setHeader('Cross-Origin-Embedder-Policy', 'require-corp');
        response.setHeader('Cross-Origin-Resource-Policy', 'same-origin');
        try {
            const relative = decodeURIComponent(new URL(request.url, 'http://localhost').pathname).replace(/^\/+/, '');
            let path = confined(contentRoot, relative);
            if (existsSync(path) && statSync(path).isDirectory()) path = join(path, 'index.html');
            if (!existsSync(path) || !statSync(path).isFile()) {
                response.writeHead(404);
                response.end('Not found');
                return;
            }
            response.setHeader('Content-Type', types[extname(path)] || 'application/octet-stream');
            createReadStream(path).pipe(response);
        } catch (error) {
            response.writeHead(400);
            response.end(error.message);
        }
    });
    return server;
}

async function browserCheck(entries, opts) {
    let chromium;
    try {
        ({ chromium } = await import('playwright'));
    } catch (_) {
        throw new Error('Playwright not installed; run npm install --no-save playwright@1.55.0');
    }
    const selected = entries.filter((entry, index) => index % opts.shardCount === opts.shardIndex &&
        (!opts.names.size || opts.names.has(entry.name)));
    if (!selected.length) throw new Error('No demos matched this browser shard');
    const server = serveSite();
    await new Promise((resolveListen, reject) => {
        server.once('error', reject);
        server.listen(0, '127.0.0.1', resolveListen);
    });

    const base = 'http://127.0.0.1:' + server.address().port;
    const failures = [];
    let browser;
    try {
        browser = await chromium.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-dev-shm-usage'],
        });
        const context = await browser.newContext();
        const gallery = await context.newPage();
        try {
            await gallery.goto(base + '/wasm/index.html#' + encodeURIComponent(selected[0].name), {
                waitUntil: 'domcontentloaded',
                timeout: opts.timeout,
            });
            await gallery.locator('#modal.open').waitFor({ state: 'visible', timeout: opts.timeout });
            const route = await gallery.locator('#frame').getAttribute('src');
            if (!route || !route.startsWith(selected[0].name + '/index.html?autostart=1')) {
                failures.push('Gallery deep link points to incorrect demo: ' + route);
            }
            await gallery.locator('#close').click({ timeout: opts.timeout });
            if (await gallery.locator('#modal').evaluate(element => element.classList.contains('open'))) {
                failures.push('Gallery close button does not close the modal');
            }
            await gallery.locator('#demoSearch').fill(selected[0].name, { timeout: opts.timeout });
            if (!(await gallery.locator('.card:visible').count())) {
                failures.push('Gallery search hides the exact-match demo');
            }
        } catch (error) {
            failures.push('Gallery routing/search: ' + error.message.split('\n')[0]);
        } finally {
            await gallery.close();
        }

        for (const entry of selected) {
            const page = await context.newPage();
            const missing = [];
            page.on('response', response => {
                if (response.status() >= 400 && /\.(wasm|js)(\?|$)/.test(response.url())) {
                    missing.push(response.url());
                }
            });
            try {
                await page.goto(base + '/wasm/' + entry.page + '?autostart=1', {
                    waitUntil: 'domcontentloaded',
                    timeout: opts.timeout,
                });
                await page.waitForFunction(() => {
                    const status = (document.getElementById('status')?.textContent || '').trim();
                    return /^(running|finished after|exit -?\d+|failed to load)/.test(status);
                }, null, { timeout: opts.timeout });
                const status = (await page.locator('#status').innerText()).trim();
                if (status.startsWith('failed') || missing.length) {
                    throw new Error('status=' + status + ', missing=' + missing.join(','));
                }
                if (entry.gfx) {
                    const canvas = page.locator('canvas');
                    if (await canvas.count() !== 1) throw new Error('Graphics canvas missing');
                    const dims = await canvas.evaluate(el => [el.width, el.height]);
                    if (Math.min(...dims) <= 0) throw new Error('Invalid graphics canvas dimensions');
                }
                console.log('PASS ' + entry.name + ': ' + status);
            } catch (error) {
                const why = error.message.split('\n')[0];
                failures.push(entry.name + ': ' + why);
                console.error('FAIL ' + entry.name + ': ' + why);
            } finally {
                await page.close();
            }
        }
        await context.close();
    } finally {
        if (browser) await browser.close();
        await new Promise(resolveClose => server.close(resolveClose));
    }
    console.log('Browser shard ' + (opts.shardIndex + 1) + '/' + opts.shardCount +
        ': tested ' + selected.length + ', failed ' + failures.length);
    if (failures.length) throw new Error(failures.join('\n'));
}


// Exercise the actual deployed wiki layout, not only the source gallery directory.
// These pages are copied/assembled by build_wiki and can fail independently.
async function docsBrowserCheck(wikiRoot, opts) {
    if (!wikiRoot || !existsSync(join(wikiRoot, 'index.html'))) {
        throw new Error('Build the wiki before --docs-browser: ./flow tool build_wiki');
    }
    let chromium;
    try {
        ({ chromium } = await import('playwright'));
    } catch (_) {
        throw new Error('Playwright not installed; run npm install --no-save playwright@1.55.0');
    }
    const server = serveSite(wikiRoot);
    await new Promise((resolveListen, reject) => {
        server.once('error', reject);
        server.listen(0, '127.0.0.1', resolveListen);
    });
    const base = 'http://127.0.0.1:' + server.address().port;
    const failures = [];
    let browser;
    try {
        browser = await chromium.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-dev-shm-usage'],
        });
        const context = await browser.newContext();

        async function check(name, fn) {
            const page = await context.newPage();
            const errors = [];
            page.on('pageerror', error => errors.push(error.message));
            page.on('response', response => {
                if (response.status() >= 400 && response.url().startsWith(base + '/') &&
                    /\.(js|wasm|json)(\?|$)/.test(response.url())) {
                    errors.push('HTTP ' + response.status() + ' ' + response.url());
                }
            });
            try {
                await fn(page);
                if (errors.length) throw new Error(errors.join('; '));
                console.log('PASS docs ' + name);
            } catch (error) {
                const why = error.message.split('\n')[0];
                failures.push(name + ': ' + why);
                console.error('FAIL docs ' + name + ': ' + why);
            } finally {
                await page.close();
            }
        }

        await check('wiki navigation', async page => {
            await page.goto(base + '/index.html#start-here.md', {
                waitUntil: 'domcontentloaded', timeout: opts.timeout,
            });
            await page.waitForFunction(() => {
                const title = document.getElementById('docTitle')?.textContent.trim();
                const content = document.getElementById('markdownContent')?.textContent.trim();
                return title && content && !content.includes('Loading documentation');
            }, null, { timeout: opts.timeout });
            if (await page.locator('#markdownContent .not-found-panel').count()) {
                throw new Error('Wiki could not render Start Here');
            }
            await page.locator('#searchTrigger').click();
            await page.locator('#searchInput').fill('memory');
            await page.locator('#searchResults li').first().waitFor({ timeout: opts.timeout });
            await page.locator('#searchInput').press('Escape');
            await page.goto(base + '/index.html#getting-started.md', {
                waitUntil: 'domcontentloaded', timeout: opts.timeout,
            });
            await page.waitForFunction(() => document.getElementById('docTitle')?.textContent.trim(), null,
                { timeout: opts.timeout });
        });

        await check('playground interpreter, examples and sharing', async page => {
            await page.goto(base + '/playground/index.html', {
                waitUntil: 'domcontentloaded', timeout: opts.timeout,
            });
            await page.locator('#runBrowserBtn:visible').waitFor({ timeout: opts.timeout });
            const original = await page.locator('#editor').inputValue();
            await page.locator('#runBrowserBtn').click();
            await page.waitForFunction(() => /^Exited /.test(
                document.getElementById('editorStatusText')?.textContent || ''), null,
                { timeout: opts.timeout });
            if (!(await page.locator('#output').innerText()).includes('browser interpreter')) {
                throw new Error('Playground did not execute the browser interpreter');
            }
            await page.locator('#examples').selectOption('fibonacci');
            if (!(await page.locator('#editor').inputValue()).includes('function main')) {
                throw new Error('Example selector did not populate the editor');
            }
            await page.locator('#examples').selectOption('hello');
            await page.locator('button[onclick="shareCode()"]').click();
            const shareUrl = await page.locator('#shareUrl').inputValue();
            if (!shareUrl.includes('?code=')) throw new Error('Share action produced no code URL');
            const shared = await context.newPage();
            try {
                await shared.goto(shareUrl, { waitUntil: 'domcontentloaded', timeout: opts.timeout });
                if (await shared.locator('#editor').inputValue() !== original) {
                    throw new Error('Shared URL did not restore the code');
                }
            } finally {
                await shared.close();
            }
        });

        await check('playground keyboard and screen-reader accessibility', async page => {
            await page.goto(base + '/playground/index.html', {
                waitUntil: 'domcontentloaded', timeout: opts.timeout,
            });
            await page.getByRole('textbox', { name: 'Flow source code editor' })
                .waitFor({ timeout: opts.timeout });
            if (await page.locator('#output').getAttribute('role') !== 'status' ||
                await page.locator('#output').getAttribute('aria-live') !== 'polite') {
                throw new Error('Playground output lacks accessible status announcements');
            }

            const share = page.locator('button[onclick="shareCode()"]');
            await share.focus();
            await page.keyboard.press('Enter');

            const dialog = page.getByRole('dialog', { name: 'Share Your Code' });
            await dialog.waitFor({ state: 'visible', timeout: opts.timeout });
            if (await dialog.getAttribute('aria-modal') !== 'true' ||
                await page.locator('#shareModal').getAttribute('aria-hidden') !== 'false') {
                throw new Error('Share dialog lacks modal accessibility semantics');
            }

            const url = dialog.getByRole('textbox', { name: 'Shareable playground URL' });
            const close = dialog.getByRole('button', { name: 'Close' });
            const copy = dialog.getByRole('button', { name: 'Copy URL' });
            async function expectFocus(target, action) {
                if (action) await page.keyboard.press(action);
                if (!(await target.evaluate(element => document.activeElement === element))) {
                    throw new Error('Dialog keyboard focus lost at ' + (action || 'open'));
                }
            }

            await page.waitForTimeout(250);
            const focusDiagnostic = await page.evaluate(() => ({
                active: document.activeElement?.id,
                element: document.activeElement?.tagName,
                overlayVisibility: getComputedStyle(document.getElementById('shareModal')).visibility,
                inputVisibility: getComputedStyle(document.getElementById('shareUrl')).visibility,
                modalClass: document.getElementById('shareModal').className,
            }));
            console.log('Playground modal focus diagnostic: ' + JSON.stringify(focusDiagnostic));
            await page.waitForFunction(() => document.activeElement?.id === 'shareUrl', null,
                { timeout: opts.timeout });
            await expectFocus(url);
            await expectFocus(copy, 'Shift+Tab');
            await expectFocus(url, 'Tab');
            await expectFocus(close, 'Tab');
            await expectFocus(copy, 'Tab');
            await expectFocus(url, 'Tab');

            const statusBefore = await page.locator('#editorStatusText').textContent();
            await page.keyboard.press('Control+Enter');
            if (await page.locator('#editorStatusText').textContent() !== statusBefore) {
                throw new Error('Editor shortcut executed through the open share dialog');
            }

            await page.keyboard.press('Escape');
            await dialog.waitFor({ state: 'hidden', timeout: opts.timeout });
            if (await page.locator('#shareModal').getAttribute('aria-hidden') !== 'true' ||
                !(await share.evaluate(element => document.activeElement === element))) {
                throw new Error('Escape did not dismiss share dialog and restore focus');
            }

            await page.keyboard.press('Enter');
            await dialog.waitFor({ state: 'visible', timeout: opts.timeout });
            await close.click();
            await dialog.waitFor({ state: 'hidden', timeout: opts.timeout });
            if (!(await share.evaluate(element => document.activeElement === element))) {
                throw new Error('Close button did not restore the original focus');
            }
        });

        await check('browser representation preview', async page => {
            await page.goto(base + '/playground/pyodide.html', {
                waitUntil: 'domcontentloaded', timeout: opts.timeout,
            });
            await page.locator('#run:enabled').waitFor({ timeout: opts.timeout });
            await page.locator('#run').click();
            await page.waitForFunction(() => /^Exited /.test(
                document.getElementById('status')?.textContent || ''), null,
                { timeout: opts.timeout });
            await page.locator('#view').selectOption('output');
            if (!(await page.locator('#out').innerText()).includes('hello from Flow')) {
                throw new Error('Browser preview did not run the supplied code');
            }
            await page.locator('#view').selectOption('c');
            if (!(await page.locator('#out').innerText()).trim()) {
                throw new Error('C preview is empty');
            }
        });

        await check('interactive tutorials', async page => {
            await page.goto(base + '/tutorials/index.html', {
                waitUntil: 'domcontentloaded', timeout: opts.timeout,
            });
            await page.locator('.tutorials-lesson').first().waitFor({ timeout: opts.timeout });
            await page.locator('[data-runner-slot] button[data-run]').click();
            await page.waitForFunction(() => {
                const status = document.querySelector('[data-runner-slot] [data-status]')?.textContent || '';
                return /^(Exited |Native only|Error$)/.test(status);
            }, null, { timeout: opts.timeout });
            const status = await page.locator('[data-runner-slot] [data-status]').innerText();
            if (!status.startsWith('Exited ')) throw new Error('First interactive lesson: ' + status);
            const output = await page.locator('[data-runner-slot] [data-pane="output"]').innerText();
            if (!output.trim()) throw new Error('Interactive lesson output is empty');
            await page.locator('.tutorials-track').filter({ hasText: /^All \(/ }).click();
            if (!(await page.locator('.tutorials-lesson').count())) {
                throw new Error('Tutorial track filter returned no lessons');
            }
        });

        await check('deployed WASM sample', async page => {
            await page.goto(base + '/wasm/hello_world/index.html?autostart=1', {
                waitUntil: 'domcontentloaded', timeout: opts.timeout,
            });
            await page.waitForFunction(() => /^exit -?\d+$/.test(
                (document.getElementById('status')?.textContent || '').trim()), null,
                { timeout: opts.timeout });
            if (!(await page.locator('#out').innerText()).includes('main returned')) {
                throw new Error('WASM did not execute main');
            }
        });

        await context.close();
    } finally {
        if (browser) await browser.close();
        await new Promise(resolveClose => server.close(resolveClose));
    }
    console.log('Docs browser: ' + (5 - failures.length) + '/5 scenarios passed');
    if (failures.length) throw new Error(failures.join('\n'));
}

async function main() {
    const opts = { browser: false, docsBrowser: false, wiki: null, shardIndex: 0, shardCount: 1, names: new Set(), timeout: 25000 };
    const args = process.argv.slice(2);
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        if (arg === '--browser') opts.browser = true;
        else if (arg === '--docs-browser') opts.docsBrowser = true;
        else if (arg === '--wiki') opts.wiki = resolve(args[++i]);
        else if (arg === '--shard-index') opts.shardIndex = Number(args[++i]);
        else if (arg === '--shard-count') opts.shardCount = Number(args[++i]);
        else if (arg === '--name') opts.names.add(args[++i]);
        else if (arg === '--timeout-ms') opts.timeout = Number(args[++i]);
        else throw new Error('Unknown argument ' + arg);
    }
    if (!Number.isInteger(opts.shardCount) || opts.shardCount < 1 ||
        !Number.isInteger(opts.shardIndex) || opts.shardIndex < 0 ||
        opts.shardIndex >= opts.shardCount) throw new Error('Invalid browser shard');
    const entries = staticCheck(opts.wiki);
    if (opts.browser) await browserCheck(entries, opts);
    if (opts.docsBrowser) await docsBrowserCheck(opts.wiki, opts);
}

main().catch(error => {
    console.error(error.stack || error.message);
    process.exitCode = 1;
});
