	.align 16
conclusion:
    movq $0, %rax
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 

	.align 16
block.6:
    movq %rcx, %rdi
    callq print_int
    jmp conclusion

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

	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    jmp start


