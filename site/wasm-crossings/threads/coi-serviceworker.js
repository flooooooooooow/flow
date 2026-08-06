// Cross-origin isolation from a static host, via a service worker.
//
// WebAssembly threads are pthreads over SharedArrayBuffer. Since Spectre,
// browsers only hand a page a SharedArrayBuffer when that page is
// "cross-origin isolated", and a page only becomes isolated when the *server*
// sends two response headers:
//
//     Cross-Origin-Opener-Policy:   same-origin
//     Cross-Origin-Embedder-Policy: require-corp
//
// GitHub Pages will not send them. Neither will `python3 -m http.server`.
// That is the whole reason people believe threaded WASM cannot be shipped on a
// static host.
//
// A service worker sits between the page and the network and gets to rewrite
// responses, so it can add the headers the server refused to. The dance:
//
//   1st load  no worker controls the page, so the page is not isolated. This
//             script registers the worker and reloads once.
//   2nd load  the worker controls the page. Every request, including the page
//             itself and the .wasm, goes out to the network and comes back
//             through the worker, which re-wraps the response with COOP/COEP.
//             crossOriginIsolated flips to true and SharedArrayBuffer appears.
//
// Requires a secure context: https, or localhost. Both are satisfied by
// GitHub Pages and by a local http.server on 127.0.0.1.
//
// The reload is guarded by sessionStorage so a browser that refuses to install
// the worker degrades to "threads unavailable" instead of a reload loop.

if (typeof self !== "undefined" && typeof window === "undefined") {
    // ---- service worker context -------------------------------------------
    self.addEventListener("install", () => self.skipWaiting());
    self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));

    self.addEventListener("fetch", (event) => {
        const request = event.request;

        // A navigation preload / "only-if-cached" request outside same-origin
        // mode cannot be re-issued; leave it to the browser.
        if (request.cache === "only-if-cached" && request.mode !== "same-origin") return;

        event.respondWith(
            fetch(request)
                .then((response) => {
                    // Opaque responses (status 0) have no readable body or
                    // headers, so there is nothing to rewrite.
                    if (response.status === 0) return response;

                    const headers = new Headers(response.headers);
                    headers.set("Cross-Origin-Embedder-Policy", "require-corp");
                    headers.set("Cross-Origin-Opener-Policy", "same-origin");
                    // Lets our own subresources satisfy require-corp.
                    headers.set("Cross-Origin-Resource-Policy", "cross-origin");

                    return new Response(response.body, {
                        status: response.status,
                        statusText: response.statusText,
                        headers,
                    });
                })
                .catch((err) => {
                    console.error("coi-serviceworker:", err);
                    return new Response("coi-serviceworker fetch failed", { status: 502 });
                })
        );
    });
} else if (typeof window !== "undefined") {
    // ---- page context ------------------------------------------------------
    (function registerCoi() {
        if (window.crossOriginIsolated) return; // already isolated, nothing to do
        if (!window.isSecureContext) {
            console.warn("coi-serviceworker: not a secure context; serve over https or localhost");
            return;
        }
        if (!("serviceWorker" in navigator)) {
            console.warn("coi-serviceworker: no service worker support");
            return;
        }

        const scriptUrl = document.currentScript && document.currentScript.src;
        if (!scriptUrl) return;

        navigator.serviceWorker
            .register(scriptUrl, { scope: "./" })
            .then((registration) => {
                if (!navigator.serviceWorker.controller) {
                    // The worker is installed but not yet driving this page.
                    // One reload puts it in control. Guard so a browser that
                    // silently refuses control cannot loop.
                    if (sessionStorage.getItem("coiReloaded") === "1") {
                        console.warn("coi-serviceworker: reloaded once and still not isolated");
                        return;
                    }
                    sessionStorage.setItem("coiReloaded", "1");
                    window.location.reload();
                    return;
                }
                sessionStorage.removeItem("coiReloaded");
                void registration;
            })
            .catch((err) => console.error("coi-serviceworker: registration failed", err));
    })();
}
