	.align 16
conclusion:
    movq $0, %rax
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 

	.align 16
block.25:
    movq %rcx, %rdi
    callq print_int
    jmp conclusion

	.align 16
block.26:
    movq $42, %rcx
    jmp block.25

	.align 16
block.27:
    movq $0, %rcx
    jmp block.25

	.align 16
start:
    callq read_int
    movq %rax, %rcx
    cmpq $1, %rcx
    je block.26
    jmp block.27

	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    jmp start


