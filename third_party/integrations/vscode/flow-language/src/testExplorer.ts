import * as path from 'path';
import { spawn } from 'child_process';
import * as vscode from 'vscode';
import { LanguageClient } from 'vscode-languageclient/node';
import { resolveFlowBinary, resolveRepoPath } from './paths';

export function registerTestExplorer(context: vscode.ExtensionContext): void {
    const ctrl = vscode.tests.createTestController('flowTests', 'Flow Tests');
    context.subscriptions.push(ctrl);

    const runProfile = ctrl.createRunProfile(
        'Run',
        vscode.TestRunProfileKind.Run,
        (request, token) => runHandler(ctrl, request, token),
        true
    );
    context.subscriptions.push(runProfile);

    const refresh = async () => {
        ctrl.items.replace([]);
        const folder = vscode.workspace.workspaceFolders?.[0];
        if (!folder) return;
        const repo = resolveRepoPath() || folder.uri.fsPath;

        const flowTests = await vscode.workspace.findFiles(
            new vscode.RelativePattern(repo, 'tests/**/*.flow'),
            '**/build/**'
        );
        const unitPy = await vscode.workspace.findFiles(
            new vscode.RelativePattern(repo, 'tests/unit/**/test_*.py')
        );

        const flowRoot = ctrl.createTestItem('flow-tier', 'Flow transpile tests', folder.uri);
        ctrl.items.add(flowRoot);
        for (const uri of flowTests.sort((a, b) => a.fsPath.localeCompare(b.fsPath))) {
            const label = path.relative(repo, uri.fsPath);
            const item = ctrl.createTestItem(uri.fsPath, label, uri);
            flowRoot.children.add(item);
        }

        const pyRoot = ctrl.createTestItem('python-unit', 'Python unit tests', folder.uri);
        ctrl.items.add(pyRoot);
        for (const uri of unitPy.sort((a, b) => a.fsPath.localeCompare(b.fsPath))) {
            const label = path.relative(repo, uri.fsPath);
            const item = ctrl.createTestItem(uri.fsPath, label, uri);
            pyRoot.children.add(item);
        }

        const suites = ctrl.createTestItem('suites', 'Suites (CLI)', folder.uri);
        for (const [id, label] of [
            ['suite-test', 'flow test'],
            ['suite-test-strict', 'flow test --strict'],
            ['suite-test-runtime', 'flow test-runtime'],
            ['suite-test-python', 'flow test-python'],
            ['suite-test-all', 'flow test-all'],
        ] as const) {
            suites.children.add(ctrl.createTestItem(id, label, folder.uri));
        }
        ctrl.items.add(suites);
    };

    ctrl.refreshHandler = () => refresh();
    void refresh();
    context.subscriptions.push(
        vscode.commands.registerCommand('flow.refreshTests', () => refresh())
    );
}

async function runHandler(
    ctrl: vscode.TestController,
    request: vscode.TestRunRequest,
    token: vscode.CancellationToken
): Promise<void> {
    const run = ctrl.createTestRun(request);
    const queue: vscode.TestItem[] = [];
    if (request.include) {
        request.include.forEach((t) => queue.push(t));
    } else {
        ctrl.items.forEach((t) => queue.push(t));
    }

    const repo = resolveRepoPath() || vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '';
    const flowBin = resolveFlowBinary(repo);

    while (queue.length && !token.isCancellationRequested) {
        const item = queue.shift()!;
        if (item.children.size > 0) {
            item.children.forEach((c) => queue.push(c));
            continue;
        }
        run.started(item);
        const start = Date.now();
        try {
            const result = await executeTest(item, repo, flowBin);
            const duration = Date.now() - start;
            if (result.ok) {
                run.passed(item, duration);
            } else {
                run.failed(item, new vscode.TestMessage(result.message || 'failed'), duration);
            }
            if (result.output) {
                run.appendOutput(result.output.replace(/\n/g, '\r\n') + '\r\n', undefined, item);
            }
        } catch (err) {
            run.failed(item, new vscode.TestMessage(String(err)));
        }
    }
    run.end();
}

function executeTest(
    item: vscode.TestItem,
    repo: string,
    flowBin: string
): Promise<{ ok: boolean; message?: string; output?: string }> {
    return new Promise((resolve) => {
        let cmd = flowBin;
        let args: string[] = [];
        const id = item.id;

        if (id === 'suite-test') args = ['test'];
        else if (id === 'suite-test-strict') args = ['test', '--strict'];
        else if (id === 'suite-test-runtime') args = ['test-runtime'];
        else if (id === 'suite-test-python') args = ['test-python'];
        else if (id === 'suite-test-all') args = ['test-all'];
        else if (id.endsWith('.py')) {
            cmd = 'python3';
            args = ['-m', 'pytest', id, '-q'];
        } else if (id.endsWith('.flow')) {
            args = ['compile', id];
        } else {
            resolve({ ok: true, output: 'nothing to run' });
            return;
        }

        const env = { ...process.env };
        if (repo) {
            env.PYTHONPATH = path.join(repo, 'src') + path.delimiter + (env.PYTHONPATH || '');
        }

        const child = spawn(cmd, args, { cwd: repo || undefined, env });
        let out = '';
        child.stdout.on('data', (d) => (out += d.toString()));
        child.stderr.on('data', (d) => (out += d.toString()));
        child.on('error', (err) => resolve({ ok: false, message: String(err), output: out }));
        child.on('close', (code) => {
            resolve({
                ok: code === 0,
                message: code === 0 ? undefined : `exit ${code}`,
                output: out.slice(-8000),
            });
        });
    });
}

// Keep LanguageClient type imported for future LSP-driven test discovery.
export type { LanguageClient };
