typedef long long LL;
extern LL n_allocs;

void* my_malloc(long long sz, char* t);
void* my_realloc(void* ptr, long long size, char* t);
void my_free(void* ptr, char* t);

