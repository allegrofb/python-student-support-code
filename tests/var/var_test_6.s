	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    callq read_int
    movq %rax, %rcx
    movq %rcx, %rdi
    callq print_int
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 

