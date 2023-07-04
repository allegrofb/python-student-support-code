	.align 16
conclusion:
    movq $0, %rax
    subq $8, %r15
    addq $24, %rsp
    popq %rbx
    popq %rbp
    retq 

	.align 16
block.7:
    movq %rcx, %r11
    movq 8(%r11), %rcx
    movq %rcx, %rdi
    callq print_int
    jmp conclusion

	.align 16
block.8:
    movq free_ptr(%rip), %r11
    addq $32, free_ptr(%rip)
    movq $6, 0(%r11)
    movq %r11, %rcx
    movq %rcx, %r11
    movq -8(%rbp), %rax
    movq %rax, 8(%r11)
    movq %rcx, %r11
    movq -16(%rbp), %rax
    movq %rax, 16(%r11)
    movq %rcx, %r11
    movq %rbx, 24(%r11)
    jmp block.7

	.align 16
block.9:
    movq %r15, %rdi
    movq $32, %rsi
    callq collect
    movq free_ptr(%rip), %r11
    addq $32, free_ptr(%rip)
    movq $6, 0(%r11)
    movq %r11, %rcx
    movq %rcx, %r11
    movq -8(%rbp), %rax
    movq %rax, 8(%r11)
    movq %rcx, %r11
    movq -16(%rbp), %rax
    movq %rax, 16(%r11)
    movq %rcx, %r11
    movq %rbx, 24(%r11)
    jmp block.7

	.align 16
start:
    movq $42, -8(%rbp)
    movq $1, -16(%rbp)
    movq $2, %rbx
    movq free_ptr(%rip), %rcx
    addq $32, %rcx
    cmpq fromspace_end(%rip), %rcx
    jl block.8
    jmp block.9

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


