	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $48, %rsp
    movq $1, %rbx
    movq $2, %rcx
    negq %rcx
    movq $38, -8(%rbp)
    addq %rcx, -8(%rbp)
    movq $1, %rcx
    addq $2, %rcx
    movq $1, -16(%rbp)
    subq %rcx, -16(%rbp)
    movq $1, %rcx
    negq %rcx
    movq $1, -24(%rbp)
    addq $2, -24(%rbp)
    movq $2, -32(%rbp)
    negq -32(%rbp)
    movq -32(%rbp), %rax
    addq %rax, -24(%rbp)
    subq -24(%rbp), %rcx
    subq %rcx, -16(%rbp)
    movq %rbx, %rcx
    subq -8(%rbp), %rcx
    addq -16(%rbp), %rcx
    movq %rcx, %rdi
    callq print_int
    addq $48, %rsp
    popq %rbx
    popq %rbp
    retq 

