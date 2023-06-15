	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $16, %rsp
    movq $1, %rbx
    movq $42, %rcx
    addq $7, %rbx
    movq %rbx, -8(%rbp)
    addq %rcx, -8(%rbp)
    movq %rbx, %rcx
    negq %rcx
    movq -8(%rbp), %rbx
    addq %rcx, %rbx
    movq %rbx, %rdi
    callq print_int
    addq $16, %rsp
    popq %rbx
    popq %rbp
    retq 

