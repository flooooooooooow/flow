import * as fs from 'fs';
import * as path from 'path';
import { spawn } from 'child_process';
import * as vscode from 'vscode';
import { resolveFlowBinary, resolveRepoPath } from './paths';

/** Compile with debug info and launch CodeLLDB / cppdbg / terminal LLDB. */
export function registerDebug(context: vscode.ExtensionContext): void {
    context.subscriptions.push(
        vscode.commands.registerCommand('flow.debugFile', () => debugActiveFile()),
        vscode.commands.registerCommand('flow.debugBuildOnly', () => buildDebugActive())
    );
}

async function activeFlowPath(): Promise<string | undefined> {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'flow') {
        vscode.window.showWarningMessage('Open a .flow file first.');
        return undefined;
    }
    if (editor.document.isDirty) {
        await editor.document.save();
    }
    return editor.document.uri.fsPath;
}

function run(
    cmd: string,
    args: string[],
    opts: { cwd?: string; env?: NodeJS.ProcessEnv }
): Promise<void> {
    return new Promise((resolve, reject) => {
        const child = spawn(cmd, args, opts);
        let err = '';
        child.stderr.on('data', (d) => (err += d.toString()));
        child.stdout.on('data', () => undefined);
        child.on('error', reject);
        child.on('close', (code) => {
            if (code === 0) resolve();
            else reject(new Error(err || `${cmd} exit ${code}`));
        });
    });
}

async function buildDebugBinary(flowFile: string): Promise<string> {
    const repo = resolveRepoPath();
    const base = path.basename(flowFile, '.flow');
    const buildDir = path.join(repo || path.dirname(flowFile), 'build');
    fs.mkdirSync(buildDir, { recursive: true });
    const cFile = path.join(buildDir, `${base}.debug.c`);
    const exe = path.join(buildDir, `${base}.debug`);
    const py = vscode.workspace.getConfiguration('flow').get<string>('pythonPath') || 'python3';
    const env = { ...process.env };
    if (repo) {
        env.PYTHONPATH = path.join(repo, 'src') + path.delimiter + (env.PYTHONPATH || '');
    }

    await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: `Flow debug build: ${base}`,
            cancellable: false,
        },
        async () => {
            await run(
                py,
                ['-m', 'flow.transpiler', flowFile, '--c', '--debug-info', '--lenient', '-o', cFile],
                { cwd: repo || path.dirname(flowFile), env }
            );
            await run('clang', ['-g', '-O0', '-fno-omit-frame-pointer', cFile, '-o', exe, '-lm'], {
                cwd: buildDir,
                env,
            });
        }
    );

    if (!fs.existsSync(exe)) {
        throw new Error(`Debug binary not found: ${exe}`);
    }
    return exe;
}

async function buildDebugActive(): Promise<void> {
    const file = await activeFlowPath();
    if (!file) return;
    try {
        const exe = await buildDebugBinary(file);
        vscode.window.showInformationMessage(`Debug binary ready: ${exe}`);
    } catch (err) {
        vscode.window.showErrorMessage(`Flow debug build failed: ${err}`);
    }
}

async function debugActiveFile(): Promise<void> {
    const file = await activeFlowPath();
    if (!file) return;

    const repo = resolveRepoPath();
    const flowBin = resolveFlowBinary(repo);

    let exe: string;
    try {
        exe = await buildDebugBinary(file);
    } catch (err) {
        vscode.window.showWarningMessage(
            `Integrated debug build failed (${err}); falling back to \`flow debug\`.`
        );
        const term =
            vscode.window.terminals.find((t) => t.name === 'Flow Debug') ||
            vscode.window.createTerminal({ name: 'Flow Debug', cwd: repo || path.dirname(file) });
        term.show();
        term.sendText(`${flowBin} debug "${file.replace(/"/g, '\\"')}"`);
        return;
    }

    const hasCodeLLDB = !!vscode.extensions.getExtension('vadimcn.vscode-lldb');
    const hasCppTools = !!vscode.extensions.getExtension('ms-vscode.cpptools');

    if (hasCodeLLDB) {
        await vscode.debug.startDebugging(undefined, {
            type: 'lldb',
            request: 'launch',
            name: 'Flow (CodeLLDB)',
            program: exe,
            cwd: path.dirname(exe),
        });
        return;
    }

    if (hasCppTools) {
        await vscode.debug.startDebugging(undefined, {
            type: 'cppdbg',
            request: 'launch',
            name: 'Flow (cppdbg)',
            program: exe,
            cwd: path.dirname(exe),
            MIMode: 'lldb',
        });
        return;
    }

    const term =
        vscode.window.terminals.find((t) => t.name === 'Flow Debug') ||
        vscode.window.createTerminal({ name: 'Flow Debug', cwd: path.dirname(exe) });
    term.show();
    term.sendText(`lldb "${exe.replace(/"/g, '\\"')}"`);
    vscode.window.showInformationMessage(
        'LLDB started in terminal. Install the CodeLLDB extension for integrated breakpoints.'
    );
}
