// Raw-socket client for scripts/ws_echo_relay.sh, used by
// tests/tools/net/run.flow. It writes the handshake and the frames itself
// (masked, as a browser does) and prints one line per reply, so the
// transcript pins down the exact bytes the relay sends back.
//
// usage: node ws_client.js WS_PORT TCP_PORT
const net = require('net');
const crypto = require('crypto');
const [wsPort, tcpPort] = process.argv.slice(2).map(Number);
const out = [];
const log = (s) => out.push(s);

function conn(port) {
  return new Promise((res, rej) => {
    const s = net.createConnection({ host: '127.0.0.1', port }, () => res(s));
    s.on('error', rej);
  });
}

class Reader {
  constructor(sock) {
    this.buf = Buffer.alloc(0); this.waiters = []; this.ended = false;
    sock.on('data', (d) => { this.buf = Buffer.concat([this.buf, d]); this.kick(); });
    sock.on('end', () => { this.ended = true; this.kick(); });
    sock.on('close', () => { this.ended = true; this.kick(); });
  }
  kick() { const w = this.waiters; this.waiters = []; w.forEach((f) => f()); }
  wait() { return new Promise((r) => { this.waiters.push(r); }); }
  async take(n) {
    while (this.buf.length < n) { if (this.ended) return null; await this.wait(); }
    const b = this.buf.subarray(0, n); this.buf = this.buf.subarray(n); return b;
  }
  async head() {
    for (;;) {
      const i = this.buf.indexOf('\r\n\r\n');
      if (i >= 0) { const h = this.buf.subarray(0, i + 4); this.buf = this.buf.subarray(i + 4); return h.toString('latin1'); }
      if (this.ended) { const h = this.buf.toString('latin1'); this.buf = Buffer.alloc(0); return h; }
      await this.wait();
    }
  }
  async rest() { while (!this.ended) await this.wait(); const b = this.buf; this.buf = Buffer.alloc(0); return b; }
  async frame() {
    const h = await this.take(2); if (!h) return null;
    let len = h[1] & 0x7f; let hdr = [h[0], h[1]];
    if (len === 126) { const e = await this.take(2); len = e.readUInt16BE(0); hdr.push(...e); }
    else if (len === 127) { const e = await this.take(8); len = Number(e.readBigUInt64BE(0)); hdr.push(...e); }
    const p = len ? await this.take(len) : Buffer.alloc(0);
    return { hdr: Buffer.from(hdr).toString('hex'), op: h[0] & 0x0f, fin: h[0] >> 7, masked: h[1] >> 7, payload: p };
  }
}

function frame(op, payload, fin = 1) {
  const mask = Buffer.from([0x11, 0x22, 0x33, 0x44]);
  const n = payload.length; let hdr;
  if (n < 126) hdr = Buffer.from([(fin << 7) | op, 0x80 | n]);
  else if (n < 65536) { hdr = Buffer.alloc(4); hdr[0] = (fin << 7) | op; hdr[1] = 0x80 | 126; hdr.writeUInt16BE(n, 2); }
  else { hdr = Buffer.alloc(10); hdr[0] = (fin << 7) | op; hdr[1] = 0x80 | 127; hdr.writeBigUInt64BE(BigInt(n), 2); }
  const m = Buffer.from(payload); for (let i = 0; i < n; i++) m[i] ^= mask[i % 4];
  return Buffer.concat([hdr, mask, m]);
}

const show = (f) => f === null ? 'EOF' :
  `hdr=${f.hdr} op=${f.op} fin=${f.fin} masked=${f.masked} len=${f.payload.length} sha1=${crypto.createHash('sha1').update(f.payload).digest('hex').slice(0, 16)} head=${JSON.stringify(f.payload.subarray(0, 24).toString('latin1'))}`;

async function handshake(req) {
  const s = await conn(wsPort); const r = new Reader(s);
  s.write(req);
  return [s, r, await r.head()];
}

async function main() {
  // 1. RFC 6455 sample key, binary subprotocol offered among others.
  let [s, r, head] = await handshake('GET / HTTP/1.1\r\nHost: x\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Protocol: chat, binary\r\nSec-WebSocket-Version: 13\r\n\r\n');
  log('handshake1:\n' + head.replace(/\r\n/g, '\\r\\n\n'));
  const cases = [
    ['text', 1, Buffer.from('hello relay')],
    ['binary', 2, Buffer.from([0, 1, 2, 255, 254, 10, 13])],
    ['empty-binary', 2, Buffer.alloc(0)],
    ['len125', 2, Buffer.alloc(125, 0x41)],
    ['len126', 1, Buffer.alloc(126, 0x42)],
    ['len65535', 2, Buffer.from(Array.from({ length: 65535 }, (_, i) => i & 255))],
    ['len70000', 2, Buffer.from(Array.from({ length: 70000 }, (_, i) => (i * 7) & 255))],
    ['ping', 9, Buffer.from('are you there')],
    ['continuation', 0, Buffer.from('cont')],
  ];
  for (const [name, op, p] of cases) {
    s.write(frame(op, p));
    log(`${name}: ${show(await r.frame())}`);
  }
  // A pong gets no answer; the next text frame is the next thing back.
  s.write(frame(10, Buffer.from('unsolicited')));
  s.write(frame(1, Buffer.from('after pong')));
  log(`after-pong: ${show(await r.frame())}`);
  // Split a frame across writes.
  const f = frame(1, Buffer.from('split frame'));
  s.write(f.subarray(0, 3)); await new Promise((z) => setTimeout(z, 50)); s.write(f.subarray(3));
  log(`split: ${show(await r.frame())}`);
  s.write(frame(8, Buffer.from([0x03, 0xe8])));
  log(`close: ${show(await r.frame())}`);
  log(`after-close: ${show(await r.frame())}`);
  s.destroy();

  // 2. Only a non-binary subprotocol: the first one is echoed.
  [s, r, head] = await handshake('GET /x HTTP/1.1\r\nsec-websocket-key: AAAAAAAAAAAAAAAAAAAAAA==\r\nSec-WebSocket-Protocol:  chat ,superchat\r\n\r\n');
  log('handshake2:\n' + head.replace(/\r\n/g, '\\r\\n\n'));
  s.destroy();

  // 3. No protocol header at all.
  [s, r, head] = await handshake('GET / HTTP/1.1\r\nSec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==\r\n\r\n');
  log('handshake3:\n' + head.replace(/\r\n/g, '\\r\\n\n'));
  s.destroy();

  // 4. No key: 400 and the connection closes.
  [s, r, head] = await handshake('GET / HTTP/1.1\r\nHost: x\r\n\r\n');
  log('handshake4:\n' + head.replace(/\r\n/g, '\\r\\n\n'));
  log(`handshake4-rest: ${JSON.stringify((await r.rest()).toString('latin1'))}`);
  s.destroy();

  // 5. Peer vanishes mid-frame; relay must keep serving others.
  [s, r, head] = await handshake('GET / HTTP/1.1\r\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n\r\n');
  s.write(Buffer.from([0x82, 0x85, 1])); s.destroy();

  // 6. Two clients at once.
  const [a, ra] = await handshake('GET / HTTP/1.1\r\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n\r\n');
  const [b, rb] = await handshake('GET / HTTP/1.1\r\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n\r\n');
  b.write(frame(1, Buffer.from('from b'))); a.write(frame(1, Buffer.from('from a')));
  log(`concurrent-b: ${show(await rb.frame())}`);
  log(`concurrent-a: ${show(await ra.frame())}`);
  a.destroy(); b.destroy();

  // 7. Plain TCP echo.
  if (tcpPort) {
    const t = await conn(tcpPort); const rt = new Reader(t);
    const big = Buffer.from(Array.from({ length: 200000 }, (_, i) => (i * 13) & 255));
    t.write('tcp hello\n');
    log(`tcp1: ${JSON.stringify((await rt.take(10)).toString('latin1'))}`);
    t.write(big);
    const back = await rt.take(big.length);
    log(`tcp2: len=${back.length} equal=${Buffer.compare(back, big) === 0}`);
    t.end();
    log(`tcp-eof: ${(await rt.rest()).length}`);
  }
  process.stdout.write(out.join('\n') + '\n');
  process.exit(0);
}
main().catch((e) => { process.stdout.write(out.join('\n') + '\nERROR ' + e.message + '\n'); process.exit(1); });
