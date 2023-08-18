	.align 16
conclusion:
    movq $0, %rax
    subq $8, %r15
    addq $56, %rsp
    popq %rbx
    popq %rbp
    retq 

	.align 16
block.16:
    movq %rcx, %rdi
    callq print_int
    jmp conclusion

	.align 16
block.17:
    movq %rbx, %r11
    addq $1, -8(%rbp)
    imull $8, -8(%rbp)
    addq -8(%rbp), %r11
    movq 0(%r11), %rax
    movq %rax, -24(%rbp)
    movq -32(%rbp), %r11
    addq $1, -8(%rbp)
    imull $8, -8(%rbp)
    addq -8(%rbp), %r11
    movq 0(%r11), %rax
    movq %rax, -40(%rbp)
    movq -40(%rbp), %rax
    imull %rax, -24(%rbp)
    addq -24(%rbp), %rcx
    addq $1, -8(%rbp)
    jmp block.15

	.align 16
block.18:
    jmp block.16

	.align 16
block.15:
    movq -16(%rbp), %rax
    cmpq %rax, -8(%rbp)
    jne block.17
    jmp block.18

	.align 16
block.19:
    movq free_ptr(%rip), %r11
    addq $24, free_ptr(%rip)
    movq $4611686018427387913, 0(%r11)
    movq %r11, %rcx
    movq %rcx, %r11
    movq -8(%rbp), %rax
    movq %rax, 8(%r11)
    movq %rcx, %r11
    movq -16(%rbp), %rax
    movq %rax, 16(%r11)
    movq %rcx, -32(%rbp)
    movq $0, -8(%rbp)
    movq $0, %rcx
    movq %rbx, %r11
    movq 0(%r11), %rax
    movq %rax, -16(%rbp)
    jmp block.15

	.align 16
block.20:
    movq %r15, %rdi
    movq $24, %rsi
    callq collect
    movq free_ptr(%rip), %r11
    addq $24, free_ptr(%rip)
    movq $4611686018427387913, 0(%r11)
    movq %r11, %rcx
    movq %rcx, %r11
    movq -8(%rbp), %rax
    movq %rax, 8(%r11)
    movq %rcx, %r11
    movq -16(%rbp), %rax
    movq %rax, 16(%r11)
    movq %rcx, -32(%rbp)
    movq $0, -8(%rbp)
    movq $0, %rcx
    movq %rbx, %r11
    movq 0(%r11), %rax
    movq %rax, -16(%rbp)
    jmp block.15

	.align 16
block.21:
    movq free_ptr(%rip), %r11
    addq $24, free_ptr(%rip)
    movq $4611686018427387913, 0(%r11)
    movq %r11, %rcx
    movq %rcx, %r11
    movq -8(%rbp), %rax
    movq %rax, 8(%r11)
    movq %rcx, %r11
    movq %rbx, 16(%r11)
    movq %rcx, %rbx
    movq $3, -8(%rbp)
    movq $3, -16(%rbp)
    movq free_ptr(%rip), %rcx
    addq $24, %rcx
    cmpq fromspace_end(%rip), %rcx
    jl block.19
    jmp block.20

	.align 16
block.22:
    movq %r15, %rdi
    movq $24, %rsi
    callq collect
    movq free_ptr(%rip), %r11
    addq $24, free_ptr(%rip)
    movq $4611686018427387913, 0(%r11)
    movq %r11, %rcx
    movq %rcx, %r11
    movq -8(%rbp), %rax
    movq %rax, 8(%r11)
    movq %rcx, %r11
    movq %rbx, 16(%r11)
    movq %rcx, %rbx
    movq $3, -8(%rbp)
    movq $3, -16(%rbp)
    movq free_ptr(%rip), %rcx
    addq $24, %rcx
    cmpq fromspace_end(%rip), %rcx
    jl block.19
    jmp block.20

	.align 16
start:
    movq $2, -8(%rbp)
    movq $2, %rbx
    movq free_ptr(%rip), %rcx
    addq $24, %rcx
    cmpq fromspace_end(%rip), %rcx
    jl block.21
    jmp block.22

	.globl main
	.align 16
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    subq $56, %rsp
    movq $65536, %rdi
    movq $65536, %rsi
    callq initialize
    movq rootstack_begin(%rip), %r15
    movq $0, 0(%r15)
    addq $8, %r15
    jmp start


