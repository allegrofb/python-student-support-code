	.align 16
block.1:
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax

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
    cmpq $1, $3
    jg block.2
    jmp block.3
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


