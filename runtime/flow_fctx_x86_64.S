/* x86_64 fiber context switch — Darwin (_prefix) and Linux ELF */
#if defined(__APPLE__)
#define SYM(x) _##x
#else
#define SYM(x) x
#endif

.text
.align 4

/* void flow_fctx_swap(flow_fctx *old, flow_fctx *new)
 * SysV/Darwin: rdi=old, rsi=new
 * Stack layout (64 bytes, 16-aligned):
 *   0: rbx  8: rbp  16: r12  24: r13  32: r14  40: r15  48: rip
 *   (56: pad)
 */
.globl SYM(flow_fctx_swap)
SYM(flow_fctx_swap):
    pushq %rbp
    movq %rsp, %rbp
    /* save callee-saved; return address already on stack from call */
    pushq %rbx
    pushq %r12
    pushq %r13
    pushq %r14
    pushq %r15
    /* stack now: r15,r14,r13,r12,rbx,rbp,ret */
    movq %rsp, (%rdi)
    movq (%rsi), %rsp
    popq %r15
    popq %r14
    popq %r13
    popq %r12
    popq %rbx
    popq %rbp
    ret

.globl SYM(flow_fctx_bootstrap)
SYM(flow_fctx_bootstrap):
#if defined(__APPLE__)
    /* Darwin: arg in r12 (we stash), fn in r13 */
    movq %r12, %rdi
    callq *%r13
#else
    movq %r12, %rdi
    callq *%r13
#endif
    jmp SYM(flow_fiber_asm_done)

#if defined(__APPLE__)
.subsections_via_symbols
#endif
