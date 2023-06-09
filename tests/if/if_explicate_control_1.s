	.align 16
start:
    movq $2, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax
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


