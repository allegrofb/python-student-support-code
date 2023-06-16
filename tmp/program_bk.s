.section .data
message: .asciz "Enter an integer: "
message_len = . - message

.section .text
.globl main

.extern read_int
.extern print_int

main:
    # Prompt the user to enter an integer
    mov $1, %edi            # File descriptor for stdout
    mov $message, %esi      # Address of the message
    mov $message_len, %edx  # Length of the message
    mov $4, %eax            # System call number for write
    syscall

    # Read an integer from stdin using read_int
    call read_int@PLT            # Call the read_int function

    # Print the integer using print_int
    mov %rax, %rdi            # Move the integer value to RDI
    call print_int           # Call the print_int function

    # Exit the program
    xor %edi, %edi           # Exit status code (0)
    mov $60, %eax            # System call number for exit
    syscall
