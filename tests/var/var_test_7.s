	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    callq read_int
    movq %rax, %rcx
    callq read_int
    movq %rax, %rbx
    addq %rbx, %rcx
    addq $42, %rcx
    movq %rcx, %rdi
    callq print_int
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 

