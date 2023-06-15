	.align 16
block.3:
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax

	.align 16
block.4:
    movq $42, %rcx
    jmp block.3

	.align 16
block.5:
    movq $0, %rcx
    jmp block.3

	.align 16
start:
    callq read_int
    movq %rax, %rcx
    cmpq $1, %rcx
    je block.4
    jmp block.5
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


