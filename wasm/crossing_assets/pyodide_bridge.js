// Flow's CPython embedding ABI, implemented against Pyodide.
//
// runtime/flow_python_embed.c reaches CPython through libpython's C API:
// Py_Initialize, PyImport_ImportModule, PyObject_CallNoArgs and friends. That
// file cannot cross to wasm, because there is no libpython.so to dlopen and
// the CPython C API is not a stable ABI you can shim.
//
// The Flow-visible surface is much smaller than the C API it is built on:
// thirteen functions, all of them C-ABI scalars and NUL-terminated strings.
// That surface *can* cross. This file is an Emscripten --js-library that
// defines exactly those thirteen symbols in JavaScript and routes them to
// Pyodide, which
// is CPython compiled to wasm and running as its own module in the same page.
//
// The two wasm modules never share memory. Everything crosses as a string or a
// number, which is all Flow's embedding surface ever asked for.
//
// One thing had to change shape. Pyodide loads asynchronously, and
// python_init() is synchronous. So the page loads Pyodide first and parks it
// on globalThis.flowPyodide; python_init() then only has to check that it is
// there. The Flow program is unchanged.

addToLibrary({
    $FlowPy__deps: ["$UTF8ToString"],
    $FlowPy__postset: "FlowPy.init();",
    $FlowPy: {
        ready: false,
        // Module proxies, addressed by index. Flow holds an opaque ptr<void>,
        // so index + 1 is a perfectly good handle, and 0 stays NULL.
        modules: [],
        lastError: "",
        errorBuf: 0,

        init() {
            FlowPy.modules = [];
            FlowPy.lastError = "";
        },

        py() {
            return globalThis.flowPyodide;
        },

        setError(message) {
            FlowPy.lastError = String(message);
            if (globalThis.flowPyLog) globalThis.flowPyLog("python error: " + FlowPy.lastError);
        },

        // Look up a callable on a module proxy, or record why we could not.
        attr(handle, namePtr) {
            const name = UTF8ToString(namePtr);
            const mod = FlowPy.modules[handle - 1];
            if (!mod) {
                FlowPy.setError("no such module handle: " + handle);
                return null;
            }
            let fn;
            try {
                fn = mod[name];
            } catch (e) {
                FlowPy.setError(e.message);
                return null;
            }
            if (typeof fn !== "function") {
                FlowPy.setError(`module has no callable '${name}'`);
                return null;
            }
            return fn;
        },

        // Every python_call* has the same shape: find the callable, call it,
        // turn a throw into the documented error code.
        call(handle, namePtr, args, onResult) {
            if (!FlowPy.ready) return 1;
            const fn = FlowPy.attr(handle, namePtr);
            if (!fn) return 2;
            let result;
            try {
                result = fn(...args);
            } catch (e) {
                FlowPy.setError(e.message);
                return 3;
            }
            if (onResult) onResult(result);
            // Pyodide hands back proxies for non-primitive returns; releasing
            // them is this side's job, the same way the C path DECREFs.
            if (result && typeof result.destroy === "function") result.destroy();
            return 0;
        },
    },

    // Not a Python call, but part of the same extern block in
    // lib/stdlib/python_embed.flow, so it comes from the same place.
    print_line__deps: ["$UTF8ToString"],
    print_line: (msgPtr) => out(msgPtr ? UTF8ToString(msgPtr) : ""),

    python_init__deps: ["$FlowPy"],
    python_init: () => {
        if (!FlowPy.py()) {
            FlowPy.setError("Pyodide is not loaded: the page must set globalThis.flowPyodide first");
            return 1;
        }
        FlowPy.ready = true;
        return 0;
    },

    python_destroy__deps: ["$FlowPy"],
    python_destroy: () => {
        for (const mod of FlowPy.modules) {
            if (mod && typeof mod.destroy === "function") mod.destroy();
        }
        FlowPy.modules = [];
        FlowPy.ready = false;
        return 0;
    },

    // sys.path is a real list inside Pyodide's CPython, so this is the same
    // operation the C version performs, just spelled through the proxy.
    python_add_to_path__deps: ["$FlowPy", "$UTF8ToString"],
    python_add_to_path: (pathPtr) => {
        if (!FlowPy.ready) return 1;
        const path = UTF8ToString(pathPtr);
        if (!path) return 1;
        try {
            const sys = FlowPy.py().pyimport("sys");
            sys.path.append(path);
            sys.destroy();
            return 0;
        } catch (e) {
            FlowPy.setError(e.message);
            return 2;
        }
    },

    python_import_module__deps: ["$FlowPy", "$UTF8ToString"],
    python_import_module: (namePtr) => {
        if (!FlowPy.ready) return 0;
        const name = UTF8ToString(namePtr);
        try {
            const mod = FlowPy.py().pyimport(name);
            FlowPy.modules.push(mod);
            return FlowPy.modules.length; // handle = index + 1, so never NULL
        } catch (e) {
            FlowPy.setError(e.message);
            return 0;
        }
    },

    python_call0__deps: ["$FlowPy"],
    python_call0: (handle, namePtr) => FlowPy.call(handle, namePtr, []),

    python_call1_str__deps: ["$FlowPy", "$UTF8ToString"],
    python_call1_str: (handle, namePtr, argPtr) =>
        FlowPy.call(handle, namePtr, [UTF8ToString(argPtr)]),

    python_call1_i32__deps: ["$FlowPy"],
    python_call1_i32: (handle, namePtr, arg) => FlowPy.call(handle, namePtr, [arg]),

    python_call1_f32__deps: ["$FlowPy"],
    python_call1_f32: (handle, namePtr, arg) => FlowPy.call(handle, namePtr, [arg]),

    python_call1_bool__deps: ["$FlowPy"],
    python_call1_bool: (handle, namePtr, arg) => FlowPy.call(handle, namePtr, [!!arg]),

    python_call3_i32_f64__deps: ["$FlowPy"],
    python_call3_i32_f64: (handle, namePtr, a, b, c) => {
        let ret = 0.0;   // not named `out`: that is Emscripten's stdout writer
        FlowPy.call(handle, namePtr, [a, b, c], (result) => {
            const value = Number(result);
            if (Number.isFinite(value)) ret = value;
        });
        return ret;
    },

    // Returns a char* the Flow side only reads. One reusable buffer, freed and
    // reallocated per call, so nothing leaks per error.
    // stringToNewUTF8 and free are pulled in explicitly; a JS library only
    // gets what it declares.
    python_last_error__deps: ["$FlowPy", "$stringToNewUTF8", "free"],
    python_last_error: () => {
        const text = FlowPy.lastError || "no error";
        if (FlowPy.errorBuf) _free(FlowPy.errorBuf);
        FlowPy.errorBuf = stringToNewUTF8(text);
        return FlowPy.errorBuf;
    },
});
