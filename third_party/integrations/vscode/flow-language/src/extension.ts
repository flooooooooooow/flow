import * as path from 'path';
import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind
} from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    // Get LSP path from settings or use default
    const config = vscode.workspace.getConfiguration('flow');
    let lspPath = config.get<string>('lspPath');
    
    if (!lspPath) {
        // Try to find flow-lsp in PATH or use python module
        lspPath = 'python3';
    }

    const serverOptions: ServerOptions = {
        command: lspPath,
        args: ['-m', 'flow.lsp_server'],
        transport: TransportKind.stdio,
        options: {
            env: {
                ...process.env,
                PYTHONPATH: path.join(context.extensionPath, '..', '..', '..', 'src')
            }
        }
    };

    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'flow' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.flow')
        }
    };

    client = new LanguageClient(
        'flowLanguageServer',
        'FLOW Language Server',
        serverOptions,
        clientOptions
    );

    client.start();
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
