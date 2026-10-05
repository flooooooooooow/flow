import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

export function findFlowRepoRoot(start: string | undefined): string | undefined {
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

export function resolveRepoPath(): string {
    const config = vscode.workspace.getConfiguration('flow');
    let repoPath = (config.get<string>('repoPath') || '').trim();
    if (!repoPath) {
        const folder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        repoPath = findFlowRepoRoot(folder) || findFlowRepoRoot(__dirname) || '';
    }
    return repoPath;
}

export function resolveFlowBinary(repoPath: string): string {
    const local = path.join(repoPath, 'flow');
    if (repoPath && fs.existsSync(local)) {
        return local;
    }
    return 'flow';
}
