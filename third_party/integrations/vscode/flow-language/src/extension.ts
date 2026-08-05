import * as path from 'path';
import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind,
} from 'vscode-languageclient/node';
import { registerDebug } from './debug';
import { findFlowRepoRoot, resolveFlowBinary, resolveRepoPath } from './paths';
import { registerTestExplorer } from './testExplorer';

let client: LanguageClient | undefined;
let statusBar: vscode.StatusBarItem | undefined;

function resolveServerOptions(): ServerOptions {
    const config = vscode.workspace.getConfiguration('flow');
    const env: NodeJS.ProcessEnv = { ...process.env };

    const customLsp = (config.get<string>('lspPath') || '').trim();
    if (customLsp) {
        return {
            command: customLsp,
            args: [],
            transport: TransportKind.stdio,
            options: { env },
        };
    }

    const python = (config.get<string>('pythonPath') || 'python3').trim();
    const repoPath = resolveRepoPath();
    if (repoPath) {
        const src = path.join(repoPath, 'src');
        env.PYTHONPATH = env.PYTHONPATH ? `${src}${path.delimiter}${env.PYTHONPATH}` : src;
    }

    return {
        command: python,
        args: ['-m', 'flow.lsp_server'],
        transport: TransportKind.stdio,
        options: { env },
    };
}

function clientOptions(): LanguageClientOptions {
    return {
        documentSelector: [{ scheme: 'file', language: 'flow' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.flow'),
        },
    };
}

function setStatus(text: string, tooltip?: string): void {
    if (!statusBar) return;
    statusBar.text = text;
    statusBar.tooltip = tooltip;
    statusBar.show();
}

async function startClient(): Promise<void> {
    client = new LanguageClient(
        'flowLanguageServer',
        'FLOW Language Server',
        resolveServerOptions(),
        clientOptions()
    );
    try {
        await client.start();
        setStatus('$(check) Flow LSP', 'FLOW language server running — click to restart');
    } catch (err) {
        setStatus('$(warning) Flow LSP off', String(err));
        vscode.window.showWarningMessage(
            `FLOW LSP did not start (${err}). Syntax highlighting still works. ` +
                `Set flow.repoPath to your Flow checkout. See the FLOW Language extension README.`
        );
    }
}

async function runFlowOnActive(
    subcommand: 'run' | 'compile' | 'fmt'
): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'flow') {
        vscode.window.showWarningMessage('Open a .flow file first.');
        return;
    }
    if (editor.document.isDirty) {
        await editor.document.save();
    }
    const file = editor.document.uri.fsPath;
    const repo = resolveRepoPath();
    const flowBin = resolveFlowBinary(repo);
    const term =
        vscode.window.terminals.find((t) => t.name === 'Flow') ||
        vscode.window.createTerminal({
            name: 'Flow',
            cwd: repo || path.dirname(file),
        });
    term.show();
    const quoted = `"${file.replace(/"/g, '\\"')}"`;
    term.sendText(`${flowBin} ${subcommand} ${quoted}`);
}

export function activate(context: vscode.ExtensionContext) {
    statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.command = 'flow.restartLsp';
    statusBar.text = '$(sync~spin) Flow LSP';
    statusBar.show();
    context.subscriptions.push(statusBar);

    context.subscriptions.push(
        vscode.commands.registerCommand('flow.restartLsp', async () => {
            setStatus('$(sync~spin) Flow LSP');
            if (client) {
                await client.stop();
                client = undefined;
            }
            await startClient();
            vscode.window.showInformationMessage('FLOW language server restarted');
        }),
        vscode.commands.registerCommand('flow.runFile', () => runFlowOnActive('run')),
        vscode.commands.registerCommand('flow.compileFile', () => runFlowOnActive('compile')),
        vscode.commands.registerCommand('flow.formatFile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor || editor.document.languageId !== 'flow') {
                vscode.window.showWarningMessage('Open a .flow file first.');
                return;
            }
            await vscode.commands.executeCommand('editor.action.formatDocument');
        }),
        vscode.commands.registerCommand('flow.openDocs', () => {
            void vscode.env.openExternal(
                vscode.Uri.parse('https://flooooooooooow.github.io/flow/')
            );
        })
    );

    registerDebug(context);
    registerTestExplorer(context);

    // Ensure workspace recommendations pick up repo root even from nested folders
    void findFlowRepoRoot(vscode.workspace.workspaceFolders?.[0]?.uri.fsPath);

    void startClient();
}

export function deactivate(): Thenable<void> | undefined {
    if (statusBar) {
        statusBar.dispose();
        statusBar = undefined;
    }
    if (!client) {
        return undefined;
    }
    return client.stop();
}
