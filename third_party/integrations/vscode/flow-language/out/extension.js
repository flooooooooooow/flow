"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const path = __importStar(require("path"));
const vscode = __importStar(require("vscode"));
const node_1 = require("vscode-languageclient/node");
const debug_1 = require("./debug");
const paths_1 = require("./paths");
const testExplorer_1 = require("./testExplorer");
let client;
let statusBar;
function resolveServerOptions() {
    const config = vscode.workspace.getConfiguration('flow');
    const env = { ...process.env };
    const customLsp = (config.get('lspPath') || '').trim();
    if (customLsp) {
        return {
            command: customLsp,
            args: [],
            transport: node_1.TransportKind.stdio,
            options: { env },
        };
    }
    const python = (config.get('pythonPath') || 'python3').trim();
    const repoPath = (0, paths_1.resolveRepoPath)();
    if (repoPath) {
        const src = path.join(repoPath, 'src');
        env.PYTHONPATH = env.PYTHONPATH ? `${src}${path.delimiter}${env.PYTHONPATH}` : src;
    }
    return {
        command: python,
        args: ['-m', 'flow.lsp_server'],
        transport: node_1.TransportKind.stdio,
        options: { env },
    };
}
function clientOptions() {
    return {
        documentSelector: [{ scheme: 'file', language: 'flow' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.flow'),
        },
    };
}
function setStatus(text, tooltip) {
    if (!statusBar)
        return;
    statusBar.text = text;
    statusBar.tooltip = tooltip;
    statusBar.show();
}
async function startClient() {
    client = new node_1.LanguageClient('flowLanguageServer', 'FLOW Language Server', resolveServerOptions(), clientOptions());
    try {
        await client.start();
        setStatus('$(check) Flow LSP', 'FLOW language server running — click to restart');
    }
    catch (err) {
        setStatus('$(warning) Flow LSP off', String(err));
        vscode.window.showWarningMessage(`FLOW LSP did not start (${err}). Syntax highlighting still works. ` +
            `Set flow.repoPath to your Flow checkout. See the FLOW Language extension README.`);
    }
}
async function runFlowOnActive(subcommand) {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'flow') {
        vscode.window.showWarningMessage('Open a .flow file first.');
        return;
    }
    if (editor.document.isDirty) {
        await editor.document.save();
    }
    const file = editor.document.uri.fsPath;
    const repo = (0, paths_1.resolveRepoPath)();
    const flowBin = (0, paths_1.resolveFlowBinary)(repo);
    const term = vscode.window.terminals.find((t) => t.name === 'Flow') ||
        vscode.window.createTerminal({
            name: 'Flow',
            cwd: repo || path.dirname(file),
        });
    term.show();
    const quoted = `"${file.replace(/"/g, '\\"')}"`;
    term.sendText(`${flowBin} ${subcommand} ${quoted}`);
}
function activate(context) {
    statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.command = 'flow.restartLsp';
    statusBar.text = '$(sync~spin) Flow LSP';
    statusBar.show();
    context.subscriptions.push(statusBar);
    context.subscriptions.push(vscode.commands.registerCommand('flow.restartLsp', async () => {
        setStatus('$(sync~spin) Flow LSP');
        if (client) {
            await client.stop();
            client = undefined;
        }
        await startClient();
        vscode.window.showInformationMessage('FLOW language server restarted');
    }), vscode.commands.registerCommand('flow.runFile', () => runFlowOnActive('run')), vscode.commands.registerCommand('flow.compileFile', () => runFlowOnActive('compile')), vscode.commands.registerCommand('flow.formatFile', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.languageId !== 'flow') {
            vscode.window.showWarningMessage('Open a .flow file first.');
            return;
        }
        await vscode.commands.executeCommand('editor.action.formatDocument');
    }), vscode.commands.registerCommand('flow.openDocs', () => {
        void vscode.env.openExternal(vscode.Uri.parse('https://flooooooooooow.github.io/flow/'));
    }));
    (0, debug_1.registerDebug)(context);
    (0, testExplorer_1.registerTestExplorer)(context);
    // Ensure workspace recommendations pick up repo root even from nested folders
    void (0, paths_1.findFlowRepoRoot)(vscode.workspace.workspaceFolders?.[0]?.uri.fsPath);
    void startClient();
}
function deactivate() {
    if (statusBar) {
        statusBar.dispose();
        statusBar = undefined;
    }
    if (!client) {
        return undefined;
    }
    return client.stop();
}
//# sourceMappingURL=extension.js.map