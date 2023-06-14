	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $16, %rsp
    movq $1, %rcx
    movq $42, %rbx
    addq $7, %rcx
    movq %rcx, -8(%rbp)
    addq %rbx, -8(%rbp)
    negq %rcx
    movq -8(%rbp), %rbx
    addq %rcx, %rbx
    movq %rbx, %rdi
    callq print_int
    addq $16, %rsp
    popq %rbx
    popq %rbp
    retq 

