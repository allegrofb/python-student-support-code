#include <stdio.h>
#include <inttypes.h>

// Read an integer from stdin
int64_t read_int() {
    int64_t i;
    scanf("%" SCNd64, &i);
    return i;
}

// Print an integer to stdout
void print_int(int64_t x) {
    printf("%" PRId64 "\n", x);
}



// gcc -m64 -no-pie -o program program.s
// gcc -c functions.c -o functions.o
// gcc -m64 -no-pie -o program program.o functions.o
// gcc -m64 -no-pie -o program program.s functions.o


// gcc -c -g -std=c99 functions.c
// gcc -g -no-pie -o program program.s functions.o
