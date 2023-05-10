	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $32, %rsp
    movq $2, -8(%rbp)
    negq -8(%rbp)
    movq $40, -16(%rbp)
    addq -8(%rbp), -16(%rbp)
    movq -16(%rbp), %rdi
    callq print_int
    addq $32, %rsp
    popq %rbp
    retq 

