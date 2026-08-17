.section .multiboot,"a"
.align 8
multiboot_header:
    .long 0xe85250d6
    .long 0
    .long multiboot_header_end - multiboot_header
    .long -(0xe85250d6 + 0 + (multiboot_header_end - multiboot_header))
    .short 0
    .short 0
    .long 8
multiboot_header_end:

.section .boot.data,"aw"
.align 8
boot_magic:
    .long 0
boot_info:
    .long 0

.align 4096
pml4:
    .skip 4096
.align 4096
pdpt:
    .skip 4096
.align 4096
pd:
    .skip 4096

.section .boot.bss,"aw",@nobits
.align 16
stack_bottom:
    .skip 65536
stack_top:

.section .boot.text,"ax"
.code32
.global _start
.type _start, @function
_start:
    cli
    movl %eax, boot_magic
    movl %ebx, boot_info
    movl $stack_top, %esp

    movl $pdpt, %eax
    orl $0x3, %eax
    movl %eax, pml4

    movl $pd, %eax
    orl $0x3, %eax
    movl %eax, pdpt

    xorl %ecx, %ecx
1:
    movl %ecx, %eax
    shll $21, %eax
    orl $0x83, %eax
    movl %eax, pd(,%ecx,8)
    movl $0, pd+4(,%ecx,8)
    incl %ecx
    cmpl $512, %ecx
    jne 1b

    movl %cr4, %eax
    orl $(1 << 5), %eax
    movl %eax, %cr4

    movl $pml4, %eax
    movl %eax, %cr3

    movl $0xc0000080, %ecx
    rdmsr
    orl $(1 << 8), %eax
    wrmsr

    movl %cr0, %eax
    orl $(1 << 31), %eax
    movl %eax, %cr0

    lgdt gdt64_ptr
    ljmp $0x08, $long_mode_start

.code64
long_mode_start:
    movw $0x10, %ax
    movw %ax, %ds
    movw %ax, %es
    movw %ax, %ss
    xorw %ax, %ax
    movw %ax, %fs
    movw %ax, %gs

    movq $stack_top, %rsp
    xorq %rbp, %rbp

    movl boot_magic(%rip), %edi
    movl boot_info(%rip), %esi
    call flow_export_kernel_main

2:
    cli
    hlt
    jmp 2b
.size _start, . - _start

.align 8
gdt64:
    .quad 0x0000000000000000
    .quad 0x00af9a000000ffff
    .quad 0x00cf92000000ffff
gdt64_end:

gdt64_ptr:
    .word gdt64_end - gdt64 - 1
    .long gdt64
