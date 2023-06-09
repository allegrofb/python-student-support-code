	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $16, %rsp
    callq read_int
    movq %rbx, y
    movq y, %rcx
    callq print_int
    addq $16, %rsp
    popq %rbx
    popq %rbp
    retq 

