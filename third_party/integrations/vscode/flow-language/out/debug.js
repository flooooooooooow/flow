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
exports.registerDebug = registerDebug;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const child_process_1 = require("child_process");
const vscode = __importStar(require("vscode"));
const paths_1 = require("./paths");
/** Compile with debug info and launch CodeLLDB / cppdbg / terminal LLDB. */
function registerDebug(context) {
    context.subscriptions.push(vscode.commands.registerCommand('flow.debugFile', () => debugActiveFile()), vscode.commands.registerCommand('flow.debugBuildOnly', () => buildDebugActive()));
}
async function activeFlowPath() {
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
function run(cmd, args, opts) {
    return new Promise((resolve, reject) => {
        const child = (0, child_process_1.spawn)(cmd, args, opts);
        let err = '';
        child.stderr.on('data', (d) => (err += d.toString()));
        child.stdout.on('data', () => undefined);
        child.on('error', reject);
        child.on('close', (code) => {
            if (code === 0)
                resolve();
            else
                reject(new Error(err || `${cmd} exit ${code}`));
        });
    });
}
async function buildDebugBinary(flowFile) {
    const repo = (0, paths_1.resolveRepoPath)();
    const base = path.basename(flowFile, '.flow');
    const buildDir = path.join(repo || path.dirname(flowFile), 'build');
    fs.mkdirSync(buildDir, { recursive: true });
    const cFile = path.join(buildDir, `${base}.debug.c`);
    const exe = path.join(buildDir, `${base}.debug`);
    const py = vscode.workspace.getConfiguration('flow').get('pythonPath') || 'python3';
    const env = { ...process.env };
    if (repo) {
        env.PYTHONPATH = path.join(repo, 'src') + path.delimiter + (env.PYTHONPATH || '');
    }
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `Flow debug build: ${base}`,
        cancellable: false,
    }, async () => {
        await run(py, ['-m', 'flow.transpiler', flowFile, '--c', '--debug-info', '--lenient', '-o', cFile], { cwd: repo || path.dirname(flowFile), env });
        await run('clang', ['-g', '-O0', '-fno-omit-frame-pointer', cFile, '-o', exe, '-lm'], {
            cwd: buildDir,
            env,
        });
    });
    if (!fs.existsSync(exe)) {
        throw new Error(`Debug binary not found: ${exe}`);
    }
    return exe;
}
async function buildDebugActive() {
    const file = await activeFlowPath();
    if (!file)
        return;
    try {
        const exe = await buildDebugBinary(file);
        vscode.window.showInformationMessage(`Debug binary ready: ${exe}`);
    }
    catch (err) {
        vscode.window.showErrorMessage(`Flow debug build failed: ${err}`);
    }
}
async function debugActiveFile() {
    const file = await activeFlowPath();
    if (!file)
        return;
    const repo = (0, paths_1.resolveRepoPath)();
    const flowBin = (0, paths_1.resolveFlowBinary)(repo);
    let exe;
    try {
        exe = await buildDebugBinary(file);
    }
    catch (err) {
        vscode.window.showWarningMessage(`Integrated debug build failed (${err}); falling back to \`flow debug\`.`);
        const term = vscode.window.terminals.find((t) => t.name === 'Flow Debug') ||
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
    const term = vscode.window.terminals.find((t) => t.name === 'Flow Debug') ||
        vscode.window.createTerminal({ name: 'Flow Debug', cwd: path.dirname(exe) });
    term.show();
    term.sendText(`lldb "${exe.replace(/"/g, '\\"')}"`);
    vscode.window.showInformationMessage('LLDB started in terminal. Install the CodeLLDB extension for integrated breakpoints.');
}
//# sourceMappingURL=debug.js.map