import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind
} from 'vscode-languageclient/node';

let client: LanguageClient | undefined;

function findFlowRepoRoot(start: string | undefined): string | undefined {
    let dir = start;
    for (let i = 0; i < 12 && dir; i++) {
        const candidate = path.join(dir, 'src', 'flow', 'lsp_server.py');
        if (fs.existsSync(candidate)) {
            return dir;
        }
        const parent = path.dirname(dir);
        if (parent === dir) break;
        dir = parent;
    }
    return undefined;
}

function resolveServerOptions(): ServerOptions {
    const config = vscode.workspace.getConfiguration('flow');
    const env: NodeJS.ProcessEnv = { ...process.env };

    const customLsp = (config.get<string>('lspPath') || '').trim();
    if (customLsp) {
        return {
            command: customLsp,
            args: [],
            transport: TransportKind.stdio,
            options: { env }
        };
    }

    const python = (config.get<string>('pythonPath') || 'python3').trim();
    let repoPath = (config.get<string>('repoPath') || '').trim();
    if (!repoPath) {
        const folder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        repoPath = findFlowRepoRoot(folder) || findFlowRepoRoot(__dirname) || '';
    }
    if (repoPath) {
        const src = path.join(repoPath, 'src');
        env.PYTHONPATH = env.PYTHONPATH ? `${src}${path.delimiter}${env.PYTHONPATH}` : src;
    }

    return {
        command: python,
        args: ['-m', 'flow.lsp_server'],
        transport: TransportKind.stdio,
        options: { env }
    };
}

function clientOptions(): LanguageClientOptions {
    return {
        documentSelector: [{ scheme: 'file', language: 'flow' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.flow')
        }
    };
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
    } catch (err) {
        vscode.window.showWarningMessage(
            `FLOW LSP did not start (${err}). Syntax highlighting still works. ` +
                `Set flow.repoPath to your Flow checkout, or install the flow Python package. ` +
                `See the FLOW Language extension README.`
        );
    }
}

export function activate(context: vscode.ExtensionContext) {
    context.subscriptions.push(
        vscode.commands.registerCommand('flow.restartLsp', async () => {
            if (client) {
                await client.stop();
                client = undefined;
            }
            await startClient();
            vscode.window.showInformationMessage('FLOW language server restarted');
        })
    );

    void startClient();
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
