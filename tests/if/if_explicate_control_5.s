	.align 16
conclusion:
    movq $0, %rax
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 

	.align 16
block.17:
    movq %rcx, %rdi
    callq print_int
    jmp conclusion

	.align 16
block.18:
    callq read_int
    movq %rax, %rcx
    addq $2, %rcx
    jmp block.17

	.align 16
block.19:
    movq %rbx, %rcx
    addq $10, %rcx
    jmp block.17

	.align 16
block.20:
    cmpq $0, %rcx
    je block.18
    jmp block.19

	.align 16
block.21:
    cmpq $2, %rcx
    je block.18
    jmp block.19

	.align 16
start:
    callq read_int
    movq %rax, %rcx
    callq read_int
    movq %rax, %rbx
    cmpq $1, %rcx
    jl block.20
    jmp block.21

	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    jmp start


