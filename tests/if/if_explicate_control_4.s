	.align 16
conclusion:
    movq $0, %rax
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 

	.align 16
block.10:
    movq %rcx, %rdi
    callq print_int
    jmp conclusion

	.align 16
block.11:
    movq %rbx, %rcx
    addq $2, %rcx
    jmp block.10

	.align 16
block.12:
    movq %rbx, %rcx
    addq $10, %rcx
    jmp block.10

	.align 16
block.13:
    cmpq $0, %rcx
    je block.11
    jmp block.12

	.align 16
block.14:
    cmpq $2, %rcx
    je block.11
    jmp block.12

	.align 16
start:
    callq read_int
    movq %rax, %rcx
    callq read_int
    movq %rax, %rbx
    cmpq $1, %rcx
    jl block.13
    jmp block.14

	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    jmp start


