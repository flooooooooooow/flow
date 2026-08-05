# http_json_cache

Small end-to-end Flow app: URL-keyed **JSON response cache**.

Uses in-tree registry packages:

| Package | Path |
|---------|------|
| `json` | `registry/packages/json` |
| `http` | `registry/packages/http` (libcurl; optional live path) |

Patterns follow `examples/ecosystem/http_get` and `examples/ecosystem/app_cache` (checkpoint / package demos).

## Offline demo (default)

No network, no libcurl. Canned JSON bodies are stored in a 4-slot cache and
queried with `json_validate` / `json_get_*`:

```bash
# from repo root
./flow run apps/http_json_cache/src/main.flow
```

Exit `0` means cache miss/store/hit and JSON field checks all passed.

`flow.toml` maps imports via `[paths]`:

```toml
[paths]
json = "../../registry/packages/json/src"
http = "../../registry/packages/http/src"
```

So `import json.lib { ... }` resolves without copying into `flow_packages/`.

## Optional: path-deps install

```bash
cd apps/http_json_cache
../../flow pkg install   # copies path deps into ./flow_packages/
```

`[dependencies]` already lists path specs for `json` and `http`.

## Live HTTP (libcurl)

`src/live_http.flow` uses owned `HttpBody` (`http_get` / `http_body_free`) —
no caller buffer allocate/free ceremony — then runs a local JSON check:

```bash
cd apps/http_json_cache
../../flow run-native src/live_http.flow
```

```flow
let body: HttpBody = http_get("https://example.com")
# ... status / body_len / ok ...
http_body_free(body)
```

Requires system libcurl. The app `[native]` section points at
`registry/packages/http/native/flow_http.c`.

## Layout

```
apps/http_json_cache/
├── README.md
├── flow.toml
└── src/
    ├── main.flow       # offline cache + json (flow run)
    └── live_http.flow  # optional live GET (run-native)
```
