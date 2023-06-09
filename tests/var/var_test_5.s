	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $16, %rsp
    movq $42, a
    movq a, b
    movq b, %rdi
    callq print_int
    addq $16, %rsp
    popq %rbx
    popq %rbp
    retq 

