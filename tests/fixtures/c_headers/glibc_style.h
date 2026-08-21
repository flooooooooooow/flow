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
