	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $128, %rsp
    callq read_int
    movq %rax, -8(%rbp)
    movq $2, -16(%rbp)
    negq -16(%rbp)
    movq $38, -24(%rbp)
    movq -16(%rbp), %rax
    addq %rax, -24(%rbp)
    callq read_int
    movq %rax, -32(%rbp)
    movq -24(%rbp), %rax
    movq %rax, -40(%rbp)
    movq -32(%rbp), %rax
    addq %rax, -40(%rbp)
    movq $1, -48(%rbp)
    addq $2, -48(%rbp)
    movq $1, -56(%rbp)
    movq -48(%rbp), %rax
    subq %rax, -56(%rbp)
    movq $1, -64(%rbp)
    negq -64(%rbp)
    movq $1, -72(%rbp)
    addq $2, -72(%rbp)
    movq $2, -80(%rbp)
    negq -80(%rbp)
    movq -72(%rbp), %rax
    movq %rax, -88(%rbp)
    movq -80(%rbp), %rax
    addq %rax, -88(%rbp)
    movq -64(%rbp), %rax
    movq %rax, -96(%rbp)
    movq -88(%rbp), %rax
    subq %rax, -96(%rbp)
    movq -56(%rbp), %rax
    movq %rax, -104(%rbp)
    movq -96(%rbp), %rax
    subq %rax, -104(%rbp)
    movq -8(%rbp), %rax
    movq %rax, -112(%rbp)
    movq -40(%rbp), %rax
    subq %rax, -112(%rbp)
    movq -112(%rbp), %rax
    movq %rax, -120(%rbp)
    movq -104(%rbp), %rax
    addq %rax, -120(%rbp)
    movq -120(%rbp), %rdi
    callq print_int
    addq $128, %rsp
    popq %rbp
    retq 

