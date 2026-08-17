const WASM_PAGE_BYTES = 65536;
const DEFAULT_ALIGNMENT = 16;

function alignUp(value, alignment = DEFAULT_ALIGNMENT) {
    return Math.ceil(value / alignment) * alignment;
}

export function createFlowWasmRuntime() {
    let memory = null;
    let heapOffset = 0;

    function malloc(size) {
        if (!(memory instanceof WebAssembly.Memory)) {
            throw new Error("Flow wasm runtime must be attached before allocation");
        }

        const bytes = Number(size) >>> 0;
        const ptr = alignUp(heapOffset || memory.buffer.byteLength);
        const end = ptr + bytes;

        if (end > memory.buffer.byteLength) {
            const missing = end - memory.buffer.byteLength;
            memory.grow(Math.ceil(missing / WASM_PAGE_BYTES));
        }

        heapOffset = end;
        return ptr;
    }

    return {
        imports: {
            env: {
                malloc,
            },
        },

        attach(instance) {
            const exportedMemory = instance?.exports?.memory;
            if (!(exportedMemory instanceof WebAssembly.Memory)) {
                throw new Error("Flow wasm module must export linear memory");
            }
            memory = exportedMemory;
            heapOffset = alignUp(memory.buffer.byteLength);
            return instance;
        },
    };
}
