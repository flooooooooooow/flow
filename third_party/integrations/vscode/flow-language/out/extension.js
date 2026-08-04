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
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const vscode = __importStar(require("vscode"));
const node_1 = require("vscode-languageclient/node");
let client;
function findFlowRepoRoot(start) {
    let dir = start;
    for (let i = 0; i < 12 && dir; i++) {
        const candidate = path.join(dir, 'src', 'flow', 'lsp_server.py');
        if (fs.existsSync(candidate)) {
            return dir;
        }
        const parent = path.dirname(dir);
        if (parent === dir)
            break;
        dir = parent;
    }
    return undefined;
}
function resolveServerOptions() {
    const config = vscode.workspace.getConfiguration('flow');
    const env = { ...process.env };
    const customLsp = (config.get('lspPath') || '').trim();
    if (customLsp) {
        return {
            command: customLsp,
            args: [],
            transport: node_1.TransportKind.stdio,
            options: { env }
        };
    }
    const python = (config.get('pythonPath') || 'python3').trim();
    let repoPath = (config.get('repoPath') || '').trim();
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
        transport: node_1.TransportKind.stdio,
        options: { env }
    };
}
function clientOptions() {
    return {
        documentSelector: [{ scheme: 'file', language: 'flow' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.flow')
        }
    };
}
async function startClient() {
    client = new node_1.LanguageClient('flowLanguageServer', 'FLOW Language Server', resolveServerOptions(), clientOptions());
    try {
        await client.start();
    }
    catch (err) {
        vscode.window.showWarningMessage(`FLOW LSP did not start (${err}). Syntax highlighting still works. ` +
            `Set flow.repoPath to your Flow checkout, or install the flow Python package. ` +
            `See the FLOW Language extension README.`);
    }
}
function activate(context) {
    context.subscriptions.push(vscode.commands.registerCommand('flow.restartLsp', async () => {
        if (client) {
            await client.stop();
            client = undefined;
        }
        await startClient();
        vscode.window.showInformationMessage('FLOW language server restarted');
    }));
    void startClient();
}
function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
//# sourceMappingURL=extension.js.map