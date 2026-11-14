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

function serveSite() {
    const types = {
        '.html': 'text/html; charset=utf-8',
        '.js': 'application/javascript; charset=utf-8',
        '.wasm': 'application/wasm',
        '.json': 'application/json; charset=utf-8',
        '.css': 'text/css; charset=utf-8',
    };
    const server = createServer((request, response) => {
        response.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
        response.setHeader('Cross-Origin-Embedder-Policy', 'require-corp');
        response.setHeader('Cross-Origin-Resource-Policy', 'same-origin');
        try {
            const relative = decodeURIComponent(new URL(request.url, 'http://localhost').pathname).replace(/^\/+/, '');
            let path = confined(site, relative);
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

async function main() {
    const opts = { browser: false, wiki: null, shardIndex: 0, shardCount: 1, names: new Set(), timeout: 25000 };
    const args = process.argv.slice(2);
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        if (arg === '--browser') opts.browser = true;
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
}

main().catch(error => {
    console.error(error.stack || error.message);
    process.exitCode = 1;
});
