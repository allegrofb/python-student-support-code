	.align 16
conclusion:
    movq $0, %rax
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 

	.align 16
block.1:
    movq %rbx, %rdi
    callq print_int
    jmp conclusion

	.align 16
block.2:
    addq %rcx, %rbx
    subq $1, %rcx
    jmp block.0

	.align 16
block.3:
    jmp block.1

	.align 16
block.0:
    cmpq $0, %rcx
    jg block.2
    jmp block.3

	.align 16
start:
    movq $0, %rbx
    movq $5, %rcx
    jmp block.0

	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    jmp start


