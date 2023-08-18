	.align 16
tail_sum_conclusion:
    subq $8, %r15
    addq $24, %rsp
    popq %rbx
    popq %rbp
    retq 

	.align 16
block.7:
    movq %rbx, %rax
    jmp tail_sum_conclusion

	.align 16
block.8:
    movq -8(%rbp), %rcx
    subq $1, %rcx
    addq %rbx, -8(%rbp)
    movq -8(%rbp), %rbx
    movq %rcx, %rdi
    movq %rbx, %rsi
    callq tail_sum
    movq %rax, %rcx
    movq %rcx, %rax
    jmp tail_sum_conclusion

	.align 16
tail_sum_start:
    movq %rdi, -8(%rbp)
    movq %rsi, %rbx
    cmpq $0, -8(%rbp)
    je block.7
    jmp block.8

	.align 16
tail_sum:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $24, %rsp
    movq rootstack_begin(%rip), %r15
    movq $0, 0(%r15)
    addq $8, %r15
    jmp tail_sum_start

	.align 16
main_conclusion:
    subq $8, %r15
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 

	.align 16
main_start:
    movq $3, %rdi
    movq $0, %rsi
    callq tail_sum
    movq %rax, %rcx
    addq $36, %rcx
    movq %rcx, %rdi
    callq print_int
    movq $0, %rax
    jmp main_conclusion

	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $8, %rsp
    movq $65536, %rdi
    movq $65536, %rsi
    callq initialize
    movq rootstack_begin(%rip), %r15
    movq $0, 0(%r15)
    addq $8, %r15
    jmp main_start


