	.align 16
conclusion:
    movq $0, %rax
    subq $8, %r15
    addq $24, %rsp
    popq %rbx
    popq %rbp
    retq 

	.align 16
block.10:
    movq $0, %rdi
    callq print_int
    jmp conclusion

	.align 16
block.11:
    movq free_ptr(%rip), %r11
    addq $24, free_ptr(%rip)
    movq $5, 0(%r11)
    movq %r11, %rcx
    movq %rcx, %r11
    movq -16(%rbp), %rax
    movq %rax, 8(%r11)
    movq %rcx, %r11
    movq -16(%rbp), %rax
    movq %rax, 16(%r11)
    jmp block.10

	.align 16
block.12:
    movq %r15, %rdi
    movq $24, %rsi
    callq collect
    movq free_ptr(%rip), %r11
    addq $24, free_ptr(%rip)
    movq $5, 0(%r11)
    movq %r11, %rcx
    movq %rcx, %r11
    movq -16(%rbp), %rax
    movq %rax, 8(%r11)
    movq %rcx, %r11
    movq -16(%rbp), %rax
    movq %rax, 16(%r11)
    jmp block.10

	.align 16
block.13:
    movq -16(%rbp), %rcx
    movq $1, -16(%rbp)
    movq $7, -16(%rbp)
    movq free_ptr(%rip), %rcx
    addq $24, %rcx
    cmpq fromspace_end(%rip), %rcx
    jl block.11
    jmp block.12

	.align 16
block.14:
    movq free_ptr(%rip), %r11
    addq $24, free_ptr(%rip)
    movq $5, 0(%r11)
    movq %r11, -16(%rbp)
    movq -16(%rbp), %r11
    movq %rbx, 8(%r11)
    movq -16(%rbp), %r11
    movq -8(%rbp), %rax
    movq %rax, 16(%r11)
    jmp block.13

	.align 16
block.15:
    movq %r15, %rdi
    movq $24, %rsi
    callq collect
    movq free_ptr(%rip), %r11
    addq $24, free_ptr(%rip)
    movq $5, 0(%r11)
    movq %r11, -16(%rbp)
    movq -16(%rbp), %r11
    movq %rbx, 8(%r11)
    movq -16(%rbp), %r11
    movq -8(%rbp), %rax
    movq %rax, 16(%r11)
    jmp block.13

	.align 16
start:
    movq $3, %rbx
    movq $7, -8(%rbp)
    movq free_ptr(%rip), %rcx
    addq $24, %rcx
    cmpq fromspace_end(%rip), %rcx
    jl block.14
    jmp block.15

	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $24, %rsp
    movq $65536, %rdi
    movq $65536, %rsi
    callq initialize
    movq rootstack_begin(%rip), %r15
    movq $0, 0(%r15)
    addq $8, %r15
    jmp start


