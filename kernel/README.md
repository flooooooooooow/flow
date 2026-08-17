# Flow kernel

This directory is the freestanding kernel substrate for Flow. The first target is x86_64 booted through Multiboot2. Flow owns the kernel entry contract and policy-facing primitives; the architecture layer is restricted to the CPU operations that cannot be expressed portably.

The current base boots in 32-bit Multiboot2 mode, establishes an identity-mapped 1 GiB long-mode address space with 2 MiB pages, enters x86_64 long mode, installs a 64 KiB kernel stack, and calls the stable Flow C ABI entry `flow_export_kernel_main`. The Flow entry validates the Multiboot2 contract and reports boot state over COM1 serial.

Build the ELF with:

```bash
bash kernel/x86_64/build.sh
```

The build requires Flow's normal transpiler dependencies plus `clang` and `ld.lld`. If `grub-file` is installed, the build also validates the resulting ELF as Multiboot2.

Boot it in QEMU with:

```bash
bash kernel/x86_64/run.sh
```

That additionally requires `grub-mkrescue` and `qemu-system-x86_64`. Successful boot reaches the serial message `Flow kernel: boot contract accepted`.

The next kernel layers should remain above this boundary: Multiboot2 memory-map ingestion, a physical page allocator, interrupt/exception tables, timer-driven scheduling, syscall entry, virtual memory ownership, and then the eBPF verifier/interpreter/JIT hooks. eBPF should consume explicit kernel hook surfaces rather than becoming part of the boot substrate.
