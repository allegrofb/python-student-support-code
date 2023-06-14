	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $16, %rsp
    movq $40, %rcx
    addq $2, %rcx
    movq %rcx, %rdi
    callq print_int
    addq $16, %rsp
    popq %rbx
    popq %rbp
    retq 

