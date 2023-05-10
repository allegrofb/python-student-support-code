	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $112, %rsp
    movq $2, -8(%rbp)
    negq -8(%rbp)
    movq $38, -16(%rbp)
    movq -8(%rbp), %rax
    addq %rax, -16(%rbp)
    movq $2, -24(%rbp)
    negq -24(%rbp)
    movq -16(%rbp), %rax
    movq %rax, -32(%rbp)
    movq -24(%rbp), %rax
    addq %rax, -32(%rbp)
    movq $1, -40(%rbp)
    addq $2, -40(%rbp)
    movq $1, -48(%rbp)
    movq -40(%rbp), %rax
    subq %rax, -48(%rbp)
    movq $1, -56(%rbp)
    negq -56(%rbp)
    movq $1, -64(%rbp)
    addq $2, -64(%rbp)
    movq $2, -72(%rbp)
    negq -72(%rbp)
    movq -64(%rbp), %rax
    movq %rax, -80(%rbp)
    movq -72(%rbp), %rax
    addq %rax, -80(%rbp)
    movq -56(%rbp), %rax
    movq %rax, -88(%rbp)
    movq -80(%rbp), %rax
    subq %rax, -88(%rbp)
    movq -48(%rbp), %rax
    movq %rax, -96(%rbp)
    movq -88(%rbp), %rax
    subq %rax, -96(%rbp)
    movq -32(%rbp), %rax
    movq %rax, -104(%rbp)
    movq -96(%rbp), %rax
    addq %rax, -104(%rbp)
    movq -104(%rbp), %rdi
    callq print_int
    addq $112, %rsp
    popq %rbp
    retq 

