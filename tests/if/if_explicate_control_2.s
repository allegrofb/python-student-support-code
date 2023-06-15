	.align 16
conclusion:
    movq $0, %rax
    addq $16, %rsp
    popq %rbx
    popq %rbp
    retq 

	.align 16
block.1:
    movq %rcx, %rdi
    callq print_int
    jmp conclusion

	.align 16
block.2:
    movq $2, %rcx
    jmp block.1

	.align 16
block.3:
    movq $10, %rcx
    jmp block.1

	.align 16
start:
    movq $3, %rax
    cmpq $1, %rax
    jg block.2
    jmp block.3

	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $16, %rsp
    jmp start


