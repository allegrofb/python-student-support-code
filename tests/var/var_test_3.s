	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $48, %rsp
    movq $1, -16(%rbp)
    movq $2, %rcx
    negq %rcx
    movq $38, -8(%rbp)
    addq %rcx, -8(%rbp)
    movq $1, %rbx
    addq $2, %rbx
    movq $1, %rcx
    subq %rbx, %rcx
    movq $1, %rbx
    negq %rbx
    movq $1, -24(%rbp)
    addq $2, -24(%rbp)
    movq $2, -32(%rbp)
    negq -32(%rbp)
    movq -32(%rbp), %rax
    addq %rax, -24(%rbp)
    subq -24(%rbp), %rbx
    subq %rbx, %rcx
    movq -16(%rbp), %rbx
    subq -8(%rbp), %rbx
    addq %rcx, %rbx
    movq %rbx, %rdi
    callq print_int
    addq $48, %rsp
    popq %rbx
    popq %rbp
    retq 

