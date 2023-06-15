
#include "runtime.h"
#include <inttypes.h>
#include <stdlib.h>
#include <stdio.h>
#include <assert.h>

int main()
{
  int64_t t = read_int();
  printf("%" PRId64, t);
  return 0;
}

