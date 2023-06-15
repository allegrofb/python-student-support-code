	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $48, %rsp
    callq read_int
    movq %rax, %rcx
    movq $2, %rbx
    negq %rbx
    movq $38, -8(%rbp)
    addq %rbx, -8(%rbp)
    callq read_int
    movq %rax, %rbx
    addq %rbx, -8(%rbp)
    movq $1, -16(%rbp)
    addq $2, -16(%rbp)
    movq $1, %rbx
    subq -16(%rbp), %rbx
    movq $1, -16(%rbp)
    negq -16(%rbp)
    movq $1, -24(%rbp)
    addq $2, -24(%rbp)
    movq $2, -32(%rbp)
    negq -32(%rbp)
    movq -32(%rbp), %rax
    addq %rax, -24(%rbp)
    movq -24(%rbp), %rax
    subq %rax, -16(%rbp)
    subq -16(%rbp), %rbx
    subq -8(%rbp), %rcx
    addq %rbx, %rcx
    movq %rcx, %rdi
    callq print_int
    addq $48, %rsp
    popq %rbx
    popq %rbp
    retq 

