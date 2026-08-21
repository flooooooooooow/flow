/* Declaration forms glibc uses that macOS does not. */
#define __THROW __attribute__ ((__nothrow__ __LEAF))
#define __nonnull(params) __attribute__ ((__nonnull__ params))
#define __wur __attribute__ ((__warn_unused_result__))

extern int open (const char *__file, int __oflag, ...) __nonnull ((1));
extern int openat (int __fd, const char *__file, int __oflag, ...) __nonnull ((2));
extern int creat (const char *__file, unsigned int __mode) __nonnull ((1));
extern int fcntl (int __fd, int __cmd, ...);
typedef long __off_t;
typedef long __ssize_t;

extern __off_t lseek (int __fd, __off_t __offset, int __whence) __THROW;
extern __ssize_t read (int __fd, void *__buf, unsigned long __nbytes) __wur;

/* glibc spells the pthread objects as unions over a layout struct and a
   size-named char array, not as plain structs or simple aliases. See
   bits/pthreadtypes.h and bits/struct_mutex.h. */
#define __SIZEOF_PTHREAD_MUTEX_T 40
#define __SIZEOF_PTHREAD_COND_T 48
#define __SIZEOF_PTHREAD_RWLOCK_T 56

typedef unsigned long int pthread_t;

struct __pthread_mutex_s
{
  int __lock;
  unsigned int __count;
  int __owner;
  unsigned int __nusers;
  int __kind;
};

typedef union
{
  struct __pthread_mutex_s __data;
  char __size[__SIZEOF_PTHREAD_MUTEX_T];
  long int __align;
} pthread_mutex_t;

typedef union
{
  char __size[__SIZEOF_PTHREAD_COND_T];
  __extension__ long long int __align;
} pthread_cond_t;

typedef union
{
  char __size[__SIZEOF_PTHREAD_RWLOCK_T];
  long int __align;
} pthread_rwlock_t;

extern int pthread_mutex_lock (pthread_mutex_t *__mutex) __THROW __nonnull ((1));
extern pthread_t pthread_self (void) __THROW;
