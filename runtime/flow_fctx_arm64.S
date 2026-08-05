/* arm64 fiber context switch — Darwin (_prefix) and Linux ELF */
#if defined(__APPLE__)
#define SYM(x) _##x
#else
#define SYM(x) x
#endif

.text
.align 2

/* void flow_fctx_swap(flow_fctx *old, flow_fctx *new)
 * x0 = old, x1 = new
 * Layout on stack (160 bytes):
 *   0: x19,x20  16: x21,x22  32: x23,x24  48: x25,x26
 *  64: x27,x28  80: x29,x30  96: d8,d9   112: d10,d11
 * 128: d12,d13 144: d14,d15
 */
.globl SYM(flow_fctx_swap)
SYM(flow_fctx_swap):
    stp x19, x20, [sp, #-160]!
    stp x21, x22, [sp, #16]
    stp x23, x24, [sp, #32]
    stp x25, x26, [sp, #48]
    stp x27, x28, [sp, #64]
    stp x29, x30, [sp, #80]
    stp d8, d9, [sp, #96]
    stp d10, d11, [sp, #112]
    stp d12, d13, [sp, #128]
    stp d14, d15, [sp, #144]
    mov x2, sp
    str x2, [x0]
    ldr x2, [x1]
    mov sp, x2
    ldp x19, x20, [sp, #0]
    ldp x21, x22, [sp, #16]
    ldp x23, x24, [sp, #32]
    ldp x25, x26, [sp, #48]
    ldp x27, x28, [sp, #64]
    ldp x29, x30, [sp, #80]
    ldp d8, d9, [sp, #96]
    ldp d10, d11, [sp, #112]
    ldp d12, d13, [sp, #128]
    ldp d14, d15, [sp, #144]
    add sp, sp, #160
    ret

.globl SYM(flow_fctx_bootstrap)
SYM(flow_fctx_bootstrap):
    mov x0, x20
    blr x19
    b SYM(flow_fiber_asm_done)

#if defined(__APPLE__)
.subsections_via_symbols
#endif
