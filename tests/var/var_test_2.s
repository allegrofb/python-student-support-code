	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $32, %rsp
    movq $2, %rbx
    negq %rbx
    movq $38, %rcx
    addq %rbx, %rcx
    movq $2, %rbx
    negq %rbx
    addq %rbx, %rcx
    movq $1, %rbx
    addq $2, %rbx
    movq $1, -8(%rbp)
    subq %rbx, -8(%rbp)
    movq $1, %rbx
    negq %rbx
    movq $1, -16(%rbp)
    addq $2, -16(%rbp)
    movq $2, -24(%rbp)
    negq -24(%rbp)
    movq -24(%rbp), %rax
    addq %rax, -16(%rbp)
    subq -16(%rbp), %rbx
    subq %rbx, -8(%rbp)
    addq -8(%rbp), %rcx
    movq %rcx, %rdi
    callq print_int
    addq $32, %rsp
    popq %rbx
    popq %rbp
    retq 

