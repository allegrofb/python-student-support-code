	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $32, %rsp
    movq $2, %rcx
    negq %rcx
    movq $38, %rbx
    addq %rcx, %rbx
    movq $2, %rcx
    negq %rcx
    addq %rcx, %rbx
    movq $1, %rcx
    addq $2, %rcx
    movq $1, -8(%rbp)
    subq %rcx, -8(%rbp)
    movq $1, -16(%rbp)
    negq -16(%rbp)
    movq $1, -24(%rbp)
    addq $2, -24(%rbp)
    movq $2, %rcx
    negq %rcx
    addq %rcx, -24(%rbp)
    movq -16(%rbp), %rcx
    subq -24(%rbp), %rcx
    subq %rcx, -8(%rbp)
    movq %rbx, %rcx
    addq -8(%rbp), %rcx
    movq %rcx, %rdi
    callq print_int
    addq $32, %rsp
    popq %rbx
    popq %rbp
    retq 

