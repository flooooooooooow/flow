/* Record creation benchmark - test memory allocation
 * Creates 8,388,608 records (same as the standardized benchmark)
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define NUM_RECORDS 8388608

typedef struct {
    double x;
    double y;
    double z;
} Record;

int main(void) {
    clock_t start = clock();
    
    /* Allocate flat array of records */
    Record* records = (Record*)malloc(NUM_RECORDS * sizeof(Record));
    
    /* Create records */
    for (int i = 0; i < NUM_RECORDS; i++) {
        records[i].x = i * 1.0;
        records[i].y = i * 2.0;
        records[i].z = i * 3.0;
    }
    
    /* Verify (prevent optimization) */
    double sum = 0.0;
    for (int i = 0; i < NUM_RECORDS; i++) {
        sum += records[i].x + records[i].y + records[i].z;
    }
    
    /* Cleanup */
    free(records);
    
    clock_t end = clock();
    double elapsed_us = (double)(end - start) / CLOCKS_PER_SEC * 1000000.0;
    
    printf("%.1f µs (checksum: %.0f)\n", elapsed_us, sum);
    
    return 0;
}
