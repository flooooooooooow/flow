/* Input for `flow analyze` (the MISRA/CERT scan over C). */
#include <stdio.h>

int main(void) {
    int x = 3;
    goto done;
done:
    printf("%d\n", x);
    return 0;
}
