	.align 16
conclusion:
    movq $0, %rax
    subq $8, %r15
    addq $8, %rsp
    popq %rbx
    popq %rbp
    retq 

	.align 16
block.11:
    movq free_ptr(%rip), %r11
    addq $16, free_ptr(%rip)
    movq $131, 0(%r11)
    movq %r11, %rcx
    movq %rcx, %r11
    movq %rbx, 8(%r11)
    movq %rcx, %r11
    movq 8(%r11), %rcx
    movq %rcx, %r11
    movq 8(%r11), %rcx
    movq %rcx, %rdi
    callq print_int
    jmp conclusion

	.align 16
block.12:
    movq %r15, %rdi
    movq $16, %rsi
    callq collect
    movq free_ptr(%rip), %r11
    addq $16, free_ptr(%rip)
    movq $131, 0(%r11)
    movq %r11, %rcx
    movq %rcx, %r11
    movq %rbx, 8(%r11)
    movq %rcx, %r11
    movq 8(%r11), %rcx
    movq %rcx, %r11
    movq 8(%r11), %rcx
    movq %rcx, %rdi
    callq print_int
    jmp conclusion

	.align 16
block.13:
    movq free_ptr(%rip), %r11
    addq $16, free_ptr(%rip)
    movq $3, 0(%r11)
    movq %r11, %rcx
    movq %rcx, %r11
    movq %rbx, 8(%r11)
    movq %rcx, %rbx
    movq free_ptr(%rip), %rcx
    addq $16, %rcx
    cmpq fromspace_end(%rip), %rcx
    jl block.11
    jmp block.12

	.align 16
block.14:
    movq %r15, %rdi
    movq $16, %rsi
    callq collect
    movq free_ptr(%rip), %r11
    addq $16, free_ptr(%rip)
    movq $3, 0(%r11)
    movq %r11, %rcx
    movq %rcx, %r11
    movq %rbx, 8(%r11)
    movq %rcx, %rbx
    movq free_ptr(%rip), %rcx
    addq $16, %rcx
    cmpq fromspace_end(%rip), %rcx
    jl block.11
    jmp block.12

	.align 16
start:
    movq $42, %rbx
    movq free_ptr(%rip), %rcx
    addq $16, %rcx
    cmpq fromspace_end(%rip), %rcx
    jl block.13
    jmp block.14

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
    jmp start


