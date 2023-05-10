	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $112, %rsp
    movq $1, -8(%rbp)
    movq $2, -16(%rbp)
    negq -16(%rbp)
    movq $38, -24(%rbp)
    movq -16(%rbp), %rax
    addq %rax, -24(%rbp)
    movq $1, -32(%rbp)
    addq $2, -32(%rbp)
    movq $1, -40(%rbp)
    movq -32(%rbp), %rax
    subq %rax, -40(%rbp)
    movq $1, -48(%rbp)
    negq -48(%rbp)
    movq $1, -56(%rbp)
    addq $2, -56(%rbp)
    movq $2, -64(%rbp)
    negq -64(%rbp)
    movq -56(%rbp), %rax
    movq %rax, -72(%rbp)
    movq -64(%rbp), %rax
    addq %rax, -72(%rbp)
    movq -48(%rbp), %rax
    movq %rax, -80(%rbp)
    movq -72(%rbp), %rax
    subq %rax, -80(%rbp)
    movq -40(%rbp), %rax
    movq %rax, -88(%rbp)
    movq -80(%rbp), %rax
    subq %rax, -88(%rbp)
    movq -8(%rbp), %rax
    movq %rax, -96(%rbp)
    movq -24(%rbp), %rax
    subq %rax, -96(%rbp)
    movq -96(%rbp), %rax
    movq %rax, -104(%rbp)
    movq -88(%rbp), %rax
    addq %rax, -104(%rbp)
    movq -104(%rbp), %rdi
    callq print_int
    addq $112, %rsp
    popq %rbp
    retq 

