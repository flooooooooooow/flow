#!/usr/bin/env python3
"""
Scripted JSON-RPC test harness for the FLOW LSP server.

Drives src/flow/lsp_server.py as a subprocess over stdio (no editor needed):
  initialize -> didOpen (broken file) -> expect publishDiagnostics (parser Error)
  didChange (type error)              -> expect publishDiagnostics (typecheck Warning)
  didChange (clean file)              -> expect empty diagnostics
  textDocument/references             -> expect symbol locations
  textDocument/prepareRename          -> symbol range, null on keywords
  textDocument/rename                 -> WorkspaceEdit across open files,
                                         errors on invalid/reserved names

Run:  python3 scripts/test_lsp_server.py
Exits non-zero on any failed check.
"""

import json
import os
import subprocess
import sys
import threading
import time
import queue

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(REPO_ROOT, 'src')

PASS = 0
FAIL = 0


def check(label, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}  {detail}")


class LspClient:
    """Minimal LSP stdio client: frames requests, collects responses and
    server-initiated notifications on a background reader thread."""

    def __init__(self):
        env = dict(os.environ)
        env['PYTHONPATH'] = SRC_DIR
        self.proc = subprocess.Popen(
            [sys.executable, '-m', 'flow.lsp_server'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=env,
        )
        self.next_id = 1
        self.responses = {}          # id -> message
        self.notifications = queue.Queue()  # server-initiated messages
        self._lock = threading.Lock()
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    def _read_loop(self):
        f = self.proc.stdout
        while True:
            header = b''
            while not header.endswith(b'\r\n\r\n'):
                b = f.read(1)
                if not b:
                    return
                header += b
            length = int(header.split(b'Content-Length:')[1].split(b'\r\n')[0])
            body = f.read(length)
            msg = json.loads(body.decode('utf-8'))
            if 'id' in msg and 'method' not in msg:
                with self._lock:
                    self.responses[msg['id']] = msg
            else:
                self.notifications.put(msg)

    def _send(self, msg):
        body = json.dumps(msg).encode('utf-8')
        self.proc.stdin.write(
            f'Content-Length: {len(body)}\r\n\r\n'.encode('ascii') + body)
        self.proc.stdin.flush()

    def request(self, method, params, timeout=5.0):
        msg_id = self.next_id
        self.next_id += 1
        self._send({'jsonrpc': '2.0', 'id': msg_id,
                    'method': method, 'params': params})
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                if msg_id in self.responses:
                    return self.responses.pop(msg_id)
            time.sleep(0.01)
        raise TimeoutError(f'no response to {method}')

    def notify(self, method, params):
        self._send({'jsonrpc': '2.0', 'method': method, 'params': params})

    def wait_notification(self, method, timeout=5.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                msg = self.notifications.get(timeout=deadline - time.time())
            except queue.Empty:
                break
            if msg.get('method') == method:
                return msg
        raise TimeoutError(f'no {method} notification received')

    def close(self):
        try:
            self.request('shutdown', None, timeout=2.0)
            self.notify('exit', None)
        except Exception:
            pass
        try:
            self.proc.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            self.proc.kill()


BROKEN_FILE = """function add(a: i32, b: i32) -> i32 {
    return a + b
"""  # missing closing brace -> parser error

TYPE_ERROR_FILE = """function add(a: i32, b: i32) -> i32 {
    return a + undefined_thing
}
"""

CLEAN_FILE = """struct Point {
    x: f64
    y: f64
}

function norm(p: Point) -> f64 {
    return sqrt(p.x * p.x + p.y * p.y)
}

function main() -> i32 {
    let p = Point { x: 3.0, y: 4.0 }
    let n = norm(p)
    return 0
}
"""

OTHER_FILE = """function use_norm() -> f64 {
    let q = Point { x: 1.0, y: 2.0 }
    return norm(q)
}
"""

URI = 'file:///test/main.flow'
URI2 = 'file:///test/other.flow'


def test_diagnostics(c):
    print("\n== Diagnostics ==")

    # didOpen with a syntactically broken file -> parser Error diagnostic
    c.notify('textDocument/didOpen', {'textDocument': {
        'uri': URI, 'languageId': 'flow', 'version': 1, 'text': BROKEN_FILE}})
    msg = c.wait_notification('textDocument/publishDiagnostics')
    diags = msg['params']['diagnostics']
    print(f"  didOpen(broken) -> {json.dumps(msg['params'], indent=2)}")
    check('didOpen broken file publishes diagnostics', len(diags) >= 1)
    check('parser error severity is Error(1)',
          diags and diags[0]['severity'] == 1, str(diags))
    check('diagnostic has a range with line info',
          diags and 'range' in diags[0]
          and diags[0]['range']['start']['line'] >= 0)
    check('source labeled flow-parser',
          diags and diags[0].get('source') == 'flow-parser')

    # didChange to a file with a type error -> Warning diagnostic (debounced)
    c.notify('textDocument/didChange', {
        'textDocument': {'uri': URI, 'version': 2},
        'contentChanges': [{'text': TYPE_ERROR_FILE}]})
    msg = c.wait_notification('textDocument/publishDiagnostics')
    diags = msg['params']['diagnostics']
    print(f"  didChange(type error) -> {json.dumps(msg['params'], indent=2)}")
    check('type error produces diagnostic', len(diags) >= 1)
    check('type finding severity is Warning(2)',
          diags and all(d['severity'] == 2 for d in diags), str(diags))
    check("range points at 'undefined_thing'",
          diags and diags[0]['range']['start']['line'] == 1, str(diags))
    check('source labeled flow-typecheck',
          diags and diags[0].get('source') == 'flow-typecheck')

    # didChange to a clean file -> diagnostics cleared
    c.notify('textDocument/didChange', {
        'textDocument': {'uri': URI, 'version': 3},
        'contentChanges': [{'text': CLEAN_FILE}]})
    msg = c.wait_notification('textDocument/publishDiagnostics')
    diags = msg['params']['diagnostics']
    print(f"  didChange(clean) -> diagnostics: {diags}")
    check('clean file publishes empty diagnostics', diags == [])

    # Debounce: 3 rapid keystrokes -> only ONE publish, for the final text
    for i, txt in enumerate([BROKEN_FILE, TYPE_ERROR_FILE, CLEAN_FILE]):
        c.notify('textDocument/didChange', {
            'textDocument': {'uri': URI, 'version': 10 + i},
            'contentChanges': [{'text': txt}]})
    first = c.wait_notification('textDocument/publishDiagnostics')
    time.sleep(0.6)  # longer than the debounce window
    extra = 0
    while not c.notifications.empty():
        if c.notifications.get().get('method') == 'textDocument/publishDiagnostics':
            extra += 1
    print(f"  3 rapid didChange -> 1 publish (diags={first['params']['diagnostics']}), "
          f"{extra} extra")
    check('rapid edits coalesce into one publish', extra == 0)
    check('coalesced publish reflects final (clean) text',
          first['params']['diagnostics'] == [])


def test_references(c):
    print("\n== References ==")

    # CLEAN_FILE is open as URI from the diagnostics test; open a second
    # file that calls norm() and uses Point to exercise cross-file refs.
    c.notify('textDocument/didOpen', {'textDocument': {
        'uri': URI2, 'languageId': 'flow', 'version': 1, 'text': OTHER_FILE}})
    c.wait_notification('textDocument/publishDiagnostics')

    def lines_of(refs, uri):
        return sorted(r['range']['start']['line'] for r in refs
                      if r['uri'] == uri)

    # function references: cursor on 'norm' declaration (line 5, col 9)
    resp = c.request('textDocument/references', {
        'textDocument': {'uri': URI},
        'position': {'line': 5, 'character': 9},
        'context': {'includeDeclaration': True}})
    refs = resp['result']
    print(f"  references(norm) -> {json.dumps(refs, indent=2)}")
    check('function refs: decl + call in main found (same file)',
          lines_of(refs, URI) == [5, 11], str(lines_of(refs, URI)))
    check('function refs: cross-file call found',
          lines_of(refs, URI2) == [2], str(lines_of(refs, URI2)))

    # includeDeclaration False drops the declaration
    resp = c.request('textDocument/references', {
        'textDocument': {'uri': URI},
        'position': {'line': 5, 'character': 9},
        'context': {'includeDeclaration': False}})
    refs = resp['result']
    check('function refs: includeDeclaration=false drops declaration',
          lines_of(refs, URI) == [11], str(lines_of(refs, URI)))

    # struct references: cursor on 'Point' usage in main (line 10 'Point {')
    resp = c.request('textDocument/references', {
        'textDocument': {'uri': URI},
        'position': {'line': 10, 'character': 13},
        'context': {'includeDeclaration': True}})
    refs = resp['result']
    print(f"  references(Point) -> {len(refs)} locations: "
          f"{[(r['uri'].split('/')[-1], r['range']['start']['line']) for r in refs]}")
    check('struct refs: decl, param type, literal found (same file)',
          lines_of(refs, URI) == [0, 5, 10], str(lines_of(refs, URI)))
    check('struct refs: cross-file literal found',
          lines_of(refs, URI2) == [1], str(lines_of(refs, URI2)))

    # local variable references: cursor on 'p' in main (line 10 'let p =')
    resp = c.request('textDocument/references', {
        'textDocument': {'uri': URI},
        'position': {'line': 10, 'character': 8},
        'context': {'includeDeclaration': True}})
    refs = resp['result']
    print(f"  references(p) -> {json.dumps(refs, indent=2)}")
    check('variable refs: local var stays in same file only',
          refs and all(r['uri'] == URI for r in refs), str(refs))
    check('variable refs: both p occurrences in main found',
          {10, 11} <= set(lines_of(refs, URI)), str(lines_of(refs, URI)))
    # Note: 'p' is also norm()'s parameter; the token scan is file-wide,
    # not function-scoped, so norm's p (lines 5-6) appears too by design.

    # references inside comments/strings must NOT match (token-based scan)
    commented = CLEAN_FILE + "\n# norm in a comment should not count\n"
    c.notify('textDocument/didChange', {
        'textDocument': {'uri': URI, 'version': 20},
        'contentChanges': [{'text': commented}]})
    c.wait_notification('textDocument/publishDiagnostics')
    resp = c.request('textDocument/references', {
        'textDocument': {'uri': URI},
        'position': {'line': 5, 'character': 9},
        'context': {'includeDeclaration': True}})
    refs = resp['result']
    check('comment mention of norm is not a reference',
          lines_of(refs, URI) == [5, 11], str(lines_of(refs, URI)))


def apply_edits(text, edits):
    """Apply single-line LSP TextEdits to a document (last edit first so
    earlier ranges stay valid)."""
    lines = text.split('\n')
    ordered = sorted(edits, key=lambda e: (e['range']['start']['line'],
                                           e['range']['start']['character']),
                     reverse=True)
    for e in ordered:
        ln = e['range']['start']['line']
        s = e['range']['start']['character']
        t = e['range']['end']['character']
        lines[ln] = lines[ln][:s] + e['newText'] + lines[ln][t:]
    return '\n'.join(lines)


def flow_compiles(text):
    """Parse + type-check text with the real Flow compiler; return
    (ok, detail)."""
    sys.path.insert(0, SRC_DIR)
    from flow.parser import Lexer, Parser
    from flow.type_checker import TypeChecker
    try:
        decls = Parser(Lexer(text), source=text).parse()
    except Exception as e:
        return False, f'parse error: {e}'
    try:
        result = TypeChecker().check(decls)
    except Exception as e:
        return False, f'type-check crash: {e}'
    errors = list(getattr(result, 'errors', []) or [])
    return not errors, f'type errors: {errors}' if errors else 'ok'


def test_rename(c):
    print("\n== Rename ==")

    # State from the previous tests: URI holds CLEAN_FILE plus a trailing
    # comment mentioning norm (line 15); URI2 holds OTHER_FILE.

    # prepareRename on the norm declaration -> range + placeholder
    resp = c.request('textDocument/prepareRename', {
        'textDocument': {'uri': URI},
        'position': {'line': 5, 'character': 9}})
    prep = resp['result']
    print(f"  prepareRename(norm) -> {json.dumps(prep)}")
    check('prepareRename on symbol returns its range',
          prep and prep['range']['start'] == {'line': 5, 'character': 9}
          and prep['range']['end'] == {'line': 5, 'character': 13}, str(prep))
    check('prepareRename placeholder is the symbol name',
          prep and prep.get('placeholder') == 'norm', str(prep))

    # prepareRename on a keyword ('function' at line 5 col 0) -> null
    resp = c.request('textDocument/prepareRename', {
        'textDocument': {'uri': URI},
        'position': {'line': 5, 'character': 0}})
    check('prepareRename on keyword returns null',
          resp.get('result') is None, str(resp.get('result')))

    # prepareRename on whitespace (blank line 4) -> null
    resp = c.request('textDocument/prepareRename', {
        'textDocument': {'uri': URI},
        'position': {'line': 4, 'character': 0}})
    check('prepareRename on whitespace returns null',
          resp.get('result') is None, str(resp.get('result')))

    # prepareRename on the comment mention of norm (line 15) -> null
    resp = c.request('textDocument/prepareRename', {
        'textDocument': {'uri': URI},
        'position': {'line': 15, 'character': 3}})
    check('prepareRename inside a comment returns null',
          resp.get('result') is None, str(resp.get('result')))

    # rename to a reserved keyword -> JSON-RPC error, no result
    resp = c.request('textDocument/rename', {
        'textDocument': {'uri': URI},
        'position': {'line': 5, 'character': 9},
        'newName': 'while'})
    print(f"  rename(norm -> while) -> {json.dumps(resp.get('error'))}")
    check('rename to keyword is rejected with an error',
          'error' in resp and not resp.get('result'), str(resp))
    check("rejection message names the keyword",
          'while' in resp.get('error', {}).get('message', ''), str(resp))

    # rename to an invalid identifier -> error
    resp = c.request('textDocument/rename', {
        'textDocument': {'uri': URI},
        'position': {'line': 5, 'character': 9},
        'newName': '123abc'})
    check('rename to invalid identifier is rejected',
          'error' in resp and not resp.get('result'), str(resp))

    # rename ON a keyword -> error
    resp = c.request('textDocument/rename', {
        'textDocument': {'uri': URI},
        'position': {'line': 5, 'character': 0},
        'newName': 'whatever'})
    check('rename on a keyword is rejected',
          'error' in resp and not resp.get('result'), str(resp))

    # successful cross-file rename: norm -> magnitude
    resp = c.request('textDocument/rename', {
        'textDocument': {'uri': URI},
        'position': {'line': 5, 'character': 9},
        'newName': 'magnitude'})
    edit = resp['result']
    print(f"  rename(norm -> magnitude) -> {json.dumps(edit, indent=2)}")
    changes = edit['changes']
    check('WorkspaceEdit contains edits for both files',
          set(changes) == {URI, URI2}, str(set(changes)))

    def lines_of(uri):
        return sorted(e['range']['start']['line'] for e in changes.get(uri, []))

    check('main file edits hit declaration + call, not the comment',
          lines_of(URI) == [5, 11], str(lines_of(URI)))
    check('other file edit hits the cross-file call',
          lines_of(URI2) == [2], str(lines_of(URI2)))
    check('all edits insert the new name',
          all(e['newText'] == 'magnitude'
              for es in changes.values() for e in es))

    # apply the WorkspaceEdit and verify the renamed program compiles
    main_text = CLEAN_FILE + "\n# norm in a comment should not count\n"
    renamed_main = apply_edits(main_text, changes[URI])
    renamed_other = apply_edits(OTHER_FILE, changes[URI2])
    check("renamed main no longer calls 'norm'",
          'norm(' not in renamed_main and 'magnitude(p)' in renamed_main)
    check("renamed other file calls 'magnitude'",
          'magnitude(q)' in renamed_other, renamed_other)
    ok, detail = flow_compiles(renamed_main + '\n' + renamed_other)
    print(f"  combined renamed program -> {detail}")
    check('renamed program parses and type-checks cleanly', ok, detail)

    # local variable rename stays in the current file only
    resp = c.request('textDocument/rename', {
        'textDocument': {'uri': URI},
        'position': {'line': 10, 'character': 8},
        'newName': 'origin'})
    changes = resp['result']['changes']
    print(f"  rename(p -> origin) -> files: {sorted(changes)}")
    check('local rename touches the current file only',
          set(changes) == {URI}, str(set(changes)))
    # Note: like references, the token scan is file-wide, not function-
    # scoped, so norm()'s parameter p is renamed together with main()'s p.


def main():
    c = LspClient()
    try:
        resp = c.request('initialize', {'processId': None, 'rootUri': None,
                                        'capabilities': {}})
        caps = resp['result']['capabilities']
        print("== Initialize ==")
        check('initialize returns capabilities', bool(caps))
        check('referencesProvider advertised', caps.get('referencesProvider') is True)
        check('renameProvider advertised with prepareProvider',
              caps.get('renameProvider') == {'prepareProvider': True},
              str(caps.get('renameProvider')))

        test_diagnostics(c)
        test_references(c)
        test_rename(c)
    finally:
        c.close()

    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == '__main__':
    main()
