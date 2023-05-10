	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $112, %rsp
    movq $1, -8(%rbp)
    movq $2, -16(%rbp)
    negq -16(%rbp)
    movq $38, -24(%rbp)
    addq -16(%rbp), -24(%rbp)
    movq $1, -32(%rbp)
    addq $2, -32(%rbp)
    movq $1, -40(%rbp)
    subq -32(%rbp), -40(%rbp)
    movq $1, -48(%rbp)
    negq -48(%rbp)
    movq $1, -56(%rbp)
    addq $2, -56(%rbp)
    movq $2, -64(%rbp)
    negq -64(%rbp)
    movq -56(%rbp), %rax
    movq %rax, -72(%rbp)
    addq -64(%rbp), -72(%rbp)
    movq -48(%rbp), %rax
    movq %rax, -80(%rbp)
    subq -72(%rbp), -80(%rbp)
    movq -40(%rbp), %rax
    movq %rax, -88(%rbp)
    subq -80(%rbp), -88(%rbp)
    movq -8(%rbp), %rax
    movq %rax, -96(%rbp)
    subq -24(%rbp), -96(%rbp)
    movq -96(%rbp), %rax
    movq %rax, -104(%rbp)
    addq -88(%rbp), -104(%rbp)
    movq -104(%rbp), %rdi
    callq print_int
    addq $112, %rsp
    popq %rbp
    retq 

