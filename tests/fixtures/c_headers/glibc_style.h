/* Declaration forms glibc uses that macOS does not. */
#define __THROW __attribute__ ((__nothrow__ __LEAF))
#define __nonnull(params) __attribute__ ((__nonnull__ params))
#define __wur __attribute__ ((__warn_unused_result__))

extern int open (const char *__file, int __oflag, ...) __nonnull ((1));
extern int openat (int __fd, const char *__file, int __oflag, ...) __nonnull ((2));
extern int creat (const char *__file, unsigned int __mode) __nonnull ((1));
extern int fcntl (int __fd, int __cmd, ...);
extern long lseek (int __fd, long __offset, int __whence) __THROW;
