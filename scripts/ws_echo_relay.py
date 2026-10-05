#!/usr/bin/env python3
"""A WebSocket echo relay, in the standard library, for the WASM sockets demo.

A browser cannot open a TCP socket. It can open a WebSocket, which is an HTTP
request that upgrades into a framed, bidirectional byte stream. Emscripten
bridges BSD sockets onto exactly that: `connect(fd, 127.0.0.1:9505)` inside a
WASM module opens `ws://127.0.0.1:9505/`, and every `send`/`recv` becomes a
binary WebSocket frame.

So a Flow program calling the ordinary socket API reaches this relay, which
sends every frame straight back. Nothing here is Flow-specific; any WebSocket
echo server works. It is in the tree so the demo has no dependencies.

    python3 scripts/ws_echo_relay.py --port 9505

Also speaks plain TCP echo on --tcp-port, so the same Flow program can be run
natively against the same relay for comparison.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import socket
import struct
import threading

WS_GUID = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

OP_CONT = 0x0
OP_TEXT = 0x1
OP_BINARY = 0x2
OP_CLOSE = 0x8
OP_PING = 0x9
OP_PONG = 0xA


def recv_exactly(conn: socket.socket, count: int) -> bytes:
    """Read exactly `count` bytes, or return short on a closed connection."""
    chunks = []
    got = 0
    while got < count:
        chunk = conn.recv(count - got)
        if not chunk:
            break
        chunks.append(chunk)
        got += len(chunk)
    return b"".join(chunks)


def read_http_request(conn: socket.socket) -> dict:
    """Read headers up to the blank line. Returns a lower-cased header map."""
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = conn.recv(4096)
        if not chunk:
            return {}
        data += chunk
        if len(data) > 65536:
            return {}
    head = data.split(b"\r\n\r\n", 1)[0].decode("latin-1")
    headers = {}
    for line in head.split("\r\n")[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()
    return headers


def handshake(conn: socket.socket) -> bool:
    headers = read_http_request(conn)
    key = headers.get("sec-websocket-key")
    if not key:
        conn.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
        return False

    accept = base64.b64encode(
        hashlib.sha1(key.encode("latin-1") + WS_GUID).digest()
    ).decode()

    lines = [
        "HTTP/1.1 101 Switching Protocols",
        "Upgrade: websocket",
        "Connection: Upgrade",
        f"Sec-WebSocket-Accept: {accept}",
    ]
    # Emscripten's socket bridge asks for the "binary" subprotocol and expects
    # it echoed back, otherwise the browser rejects the handshake.
    offered = headers.get("sec-websocket-protocol", "")
    wanted = [p.strip() for p in offered.split(",") if p.strip()]
    if "binary" in wanted:
        lines.append("Sec-WebSocket-Protocol: binary")
    elif wanted:
        lines.append(f"Sec-WebSocket-Protocol: {wanted[0]}")

    conn.sendall(("\r\n".join(lines) + "\r\n\r\n").encode("latin-1"))
    return True


def read_frame(conn: socket.socket):
    """Returns (opcode, payload) or None when the peer goes away."""
    header = recv_exactly(conn, 2)
    if len(header) < 2:
        return None
    b0, b1 = header[0], header[1]
    opcode = b0 & 0x0F
    masked = bool(b1 & 0x80)
    length = b1 & 0x7F

    if length == 126:
        ext = recv_exactly(conn, 2)
        if len(ext) < 2:
            return None
        length = struct.unpack("!H", ext)[0]
    elif length == 127:
        ext = recv_exactly(conn, 8)
        if len(ext) < 8:
            return None
        length = struct.unpack("!Q", ext)[0]

    mask = b""
    if masked:
        mask = recv_exactly(conn, 4)
        if len(mask) < 4:
            return None

    payload = recv_exactly(conn, length) if length else b""
    if len(payload) < length:
        return None
    if masked:
        payload = bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload))
    return opcode, payload


def write_frame(conn: socket.socket, opcode: int, payload: bytes) -> None:
    """Server-to-client frames are never masked."""
    header = bytearray([0x80 | opcode])
    length = len(payload)
    if length < 126:
        header.append(length)
    elif length < (1 << 16):
        header.append(126)
        header += struct.pack("!H", length)
    else:
        header.append(127)
        header += struct.pack("!Q", length)
    conn.sendall(bytes(header) + payload)


def serve_ws_client(conn: socket.socket, addr, verbose: bool) -> None:
    try:
        if not handshake(conn):
            return
        if verbose:
            print(f"[ws] {addr} upgraded")
        while True:
            frame = read_frame(conn)
            if frame is None:
                break
            opcode, payload = frame
            if opcode == OP_CLOSE:
                write_frame(conn, OP_CLOSE, b"")
                break
            if opcode == OP_PING:
                write_frame(conn, OP_PONG, payload)
                continue
            if opcode == OP_PONG:
                continue
            if verbose:
                print(f"[ws] {addr} echo {len(payload)} bytes: {payload[:48]!r}")
            write_frame(conn, OP_BINARY if opcode != OP_TEXT else OP_TEXT, payload)
    except OSError:
        pass
    finally:
        conn.close()
        if verbose:
            print(f"[ws] {addr} closed")


def serve_tcp_client(conn: socket.socket, addr, verbose: bool) -> None:
    """Plain TCP echo, so the same Flow program can be run natively."""
    try:
        while True:
            data = conn.recv(65536)
            if not data:
                break
            if verbose:
                print(f"[tcp] {addr} echo {len(data)} bytes")
            conn.sendall(data)
    except OSError:
        pass
    finally:
        conn.close()


def listener(port: int, handler, verbose: bool, label: str) -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(16)
    print(f"{label} echo relay on 127.0.0.1:{port}")
    while True:
        conn, addr = srv.accept()
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        threading.Thread(
            target=handler, args=(conn, addr, verbose), daemon=True
        ).start()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=9505, help="WebSocket port")
    ap.add_argument("--tcp-port", type=int, default=0, help="plain TCP echo port (0 disables)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    if args.tcp_port:
        threading.Thread(
            target=listener,
            args=(args.tcp_port, serve_tcp_client, args.verbose, "TCP"),
            daemon=True,
        ).start()

    listener(args.port, serve_ws_client, args.verbose, "WebSocket")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
