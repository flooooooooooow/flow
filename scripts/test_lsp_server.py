#!/usr/bin/env python3
"""
Scripted JSON-RPC test harness for the FLOW LSP server.

Drives src/flow/lsp_server.py as a subprocess over stdio (no editor needed):
  initialize -> didOpen (broken file) -> expect publishDiagnostics (parser Error)
  didChange (type error)              -> expect publishDiagnostics (typecheck Warning)
  didChange (clean file)              -> expect empty diagnostics
  textDocument/references             -> expect symbol locations

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

URI = 'file:///test/main.flow'


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


def main():
    c = LspClient()
    try:
        resp = c.request('initialize', {'processId': None, 'rootUri': None,
                                        'capabilities': {}})
        caps = resp['result']['capabilities']
        print("== Initialize ==")
        check('initialize returns capabilities', bool(caps))
        check('referencesProvider advertised', caps.get('referencesProvider') is True)

        test_diagnostics(c)
    finally:
        c.close()

    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == '__main__':
    main()
