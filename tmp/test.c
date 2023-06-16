
// #include "runtime.h"
// #include <inttypes.h>
// #include <stdlib.h>
// #include <stdio.h>
// #include <assert.h>

// int main()
// {
//   int64_t t = read_int();
//   printf("%" PRId64, t);
//   return 0;
// }



#include <inttypes.h>

// Read an integer from stdin
extern int64_t read_int();

// Print an integer to stdout
extern void print_int(int64_t x);
int main()
{
  int64_t t = read_int();
  print_int(t);
  return 0;
}


