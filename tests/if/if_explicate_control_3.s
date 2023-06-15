	.align 16
block.6:
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax

	.align 16
block.7:
    movq %rbx, %rcx
    addq $2, %rcx
    jmp block.6

	.align 16
block.8:
    movq %rbx, %rcx
    addq $10, %rcx
    jmp block.6

	.align 16
start:
    callq read_int
    movq %rax, %rcx
    callq read_int
    movq %rax, %rbx
    cmpq $1, %rcx
    jg block.7
    jmp block.8
    jmp conclusion

	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $16, %rsp
    jmp start

	.align 16
conclusion:
    addq $16, %rsp
    popq %rbx
    popq %rbp
    retq 


