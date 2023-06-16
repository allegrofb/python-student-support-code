#    .globl	main
#main:
#	pushq	%rbp
#	movq	%rsp, %rbp
#	subq	$16, %rsp
#	movl	$0, %eax
#	call	read_int@PLT
#	movq	%rax, -8(%rbp)
#	movq	-8(%rbp), %rax
#	movq	%rax, %rdi
#	call	print_int@PLT
#	movl	$0, %eax
#    addq $16, %rsp
#    popq %rbp
#	retq





	.globl main
    .align 16    
main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rax         # bug ??? rbx ???
    pushq %rbx
    #subq	$8, %rsp
    #subq $16, %rsp    
    #movl	$0, %eax
    call	read_int@PLT
    movq %rax, %rdi
    #movq %rax, %rcx
    #movq %rcx, %rdi
    call	print_int@PLT
    movl	$0, %eax
    #addq $8, %rsp
    popq %rbx
    popq %rax
    popq %rbp
    retq 

