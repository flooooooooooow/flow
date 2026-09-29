#include <stdlib.h>
  #define ALLOC(n) malloc(n)
// malloc(1) in a line comment
   // free(p) indented comment
/* free(q) in a block comment still counts */
void f(char *p) {
	sfree(p);
	free (p);
	char *x = malloc	(4);
	printf("hi"); abort();
	my_printf("no");
	__free(p);
	fprintf(stderr, "%s\n", "err");
	gets(buf);
	snprintf(b, 4, "x"); sprintf(b, "y"); scanf("%d", &n);
	p = realloc(p, 8); q = calloc(2, 2);
	char *long_line = malloc(sizeof(struct very_long_structure_name_for_testing) * 1000 + 17 + 42 + 99);
	const char *u = "café ééééééééééééééééééééééééééééééééééééééééééééééééééééééééééé"; free(u);
	éfree(p);
	→free(p);
	abort ();
	xfree(p);
	ymalloc(3);
   	  
}
