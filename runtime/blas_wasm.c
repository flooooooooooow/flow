/* Minimal BLAS/LAPACK shim for wasm gallery pages (runtime/blas_wasm.c).
 *
 * The stdlib's externs (lib/stdlib/blas.flow) are backed by Accelerate on
 * macOS and OpenBLAS on other native platforms; neither is linkable into a
 * wasm page. This file provides plain, numerically correct implementations of
 * exactly the routines the gallery examples call — the Level-1/2/3 subset
 * plus dgesv_ (LU with partial pivoting) — for demo-sized matrices. Only
 * row-major layout and CblasNoTrans are exercised by the stdlib (the CBLAS
 * constants are CblasRowMajor=101, CblasNoTrans=111); the transpose cases are
 * handled anyway for completeness.
 *
 * Like runtime/gfx_wasm.c, this file is linked only by the wasm build via an
 * explicit path; the native launcher's explicit runtime list never includes
 * it, so native builds keep using the platform BLAS.
 */

void cblas_daxpy(int n, double alpha, const double* x, int incx,
                 double* y, int incy) {
    int i;
    for (i = 0; i < n; i++) {
        y[i * incy] += alpha * x[i * incx];
    }
}

double cblas_ddot(int n, const double* x, int incx,
                  const double* y, int incy) {
    double acc = 0.0;
    int i;
    for (i = 0; i < n; i++) {
        acc += x[i * incx] * y[i * incy];
    }
    return acc;
}

double cblas_dnrm2(int n, const double* x, int incx) {
    double acc = 0.0;
    int i;
    for (i = 0; i < n; i++) {
        acc += x[i * incx] * x[i * incx];
    }
    return __builtin_sqrt(acc);
}

void cblas_dscal(int n, double alpha, double* x, int incx) {
    int i;
    for (i = 0; i < n; i++) {
        x[i * incx] *= alpha;
    }
}

void cblas_dcopy(int n, const double* x, int incx, double* y, int incy) {
    int i;
    for (i = 0; i < n; i++) {
        y[i * incy] = x[i * incx];
    }
}

/* y = alpha * A * x + beta * y  (row-major; trans=111 is CblasNoTrans) */
void cblas_dgemv(int order, int trans, int m, int n, double alpha,
                 const double* A, int lda, const double* x, int incx,
                 double beta, double* y, int incy) {
    int i, j;
    (void)order;
    for (i = 0; i < m; i++) {
        double acc = 0.0;
        for (j = 0; j < n; j++) {
            double av = (trans == 111) ? A[i * lda + j] : A[j * lda + i];
            acc += av * x[j * incx];
        }
        y[i * incy] = alpha * acc + beta * y[i * incy];
    }
}

/* C = alpha * A * B + beta * C  (row-major; 111 = CblasNoTrans) */
void cblas_dgemm(int order, int transA, int transB, int m, int n, int k,
                 double alpha, const double* A, int lda,
                 const double* B, int ldb, double beta, double* C, int ldc) {
    int i, j, l;
    (void)order;
    for (i = 0; i < m; i++) {
        for (j = 0; j < n; j++) {
            double acc = 0.0;
            for (l = 0; l < k; l++) {
                double av = (transA == 111) ? A[i * lda + l] : A[l * lda + i];
                double bv = (transB == 111) ? B[l * ldb + j] : B[j * ldb + l];
                acc += av * bv;
            }
            C[i * ldc + j] = alpha * acc + beta * C[i * ldc + j];
        }
    }
}

/* LU factorization with partial pivoting (Fortran dgetrf). A is overwritten
 * with the factored form, ipiv is 1-based, info = 0 on success. A and B are
 * column-major (LAPACK convention): element (i, j) lives at A[i + j*lda].
 * The stdlib hands over row-major Mat data with lda = rows, so this reads
 * the transpose — identical to what Accelerate would do with this call. */
void dgetrf_(int* mp, int* np, double* A, int* ldap, int* ipiv, int* infop) {
    int m = *mp, n = *np, lda = *ldap;
    int i, j, k;
    for (k = 0; k < m && k < n; k++) {
        int p = k;
        double maxv = A[k + k * lda] < 0 ? -A[k + k * lda] : A[k + k * lda];
        for (i = k + 1; i < m; i++) {
            double v = A[i + k * lda] < 0 ? -A[i + k * lda] : A[i + k * lda];
            if (v > maxv) {
                maxv = v;
                p = i;
            }
        }
        if (maxv == 0.0) {
            *infop = k + 1; /* singular pivot */
            return;
        }
        ipiv[k] = p + 1;
        if (p != k) {
            for (j = 0; j < n; j++) {
                double t = A[k + j * lda];
                A[k + j * lda] = A[p + j * lda];
                A[p + j * lda] = t;
            }
        }
        for (i = k + 1; i < m; i++) {
            double f = A[i + k * lda] / A[k + k * lda];
            A[i + k * lda] = f;
            for (j = k + 1; j < n; j++) {
                A[i + j * lda] -= f * A[k + j * lda];
            }
        }
    }
    *infop = 0;
}

/* Solve A * X = B via LU with partial pivoting (Fortran dgesv). A is
 * overwritten with the factored form, ipiv is 1-based, info = 0 on success.
 * A and B are column-major (LAPACK convention): element (i, j) of B lives at
 * B[i + j*ldb], so with nrhs = 1 the B loop never leaves the n-element
 * column (the earlier row-major B indexing wrote out of bounds here). */
void dgesv_(int* np, int* nrhsp, double* A, int* ldap, int* ipiv,
            double* B, int* ldbp, int* infop) {
    int n = *np, nrhs = *nrhsp, lda = *ldap, ldb = *ldbp;
    int i, j, k;
    *infop = 0;
    for (k = 0; k < n; k++) {
        int p = k;
        double maxv = A[k + k * lda] < 0 ? -A[k + k * lda] : A[k + k * lda];
        for (i = k + 1; i < n; i++) {
            double v = A[i + k * lda] < 0 ? -A[i + k * lda] : A[i + k * lda];
            if (v > maxv) {
                maxv = v;
                p = i;
            }
        }
        if (maxv == 0.0) {
            *infop = k + 1; /* singular pivot */
            return;
        }
        ipiv[k] = p + 1;
        if (p != k) {
            for (j = 0; j < n; j++) {
                double t = A[k + j * lda];
                A[k + j * lda] = A[p + j * lda];
                A[p + j * lda] = t;
            }
            for (j = 0; j < nrhs; j++) {
                double t = B[k + j * ldb];
                B[k + j * ldb] = B[p + j * ldb];
                B[p + j * ldb] = t;
            }
        }
        for (i = k + 1; i < n; i++) {
            double f = A[i + k * lda] / A[k + k * lda];
            A[i + k * lda] = f;
            for (j = k + 1; j < n; j++) {
                A[i + j * lda] -= f * A[k + j * lda];
            }
        }
    }
    /* Forward substitution with the unit lower factor (pivoting already
     * applied to B above). */
    for (k = 0; k < n; k++) {
        for (i = k + 1; i < n; i++) {
            double f = A[i + k * lda];
            for (j = 0; j < nrhs; j++) {
                B[i + j * ldb] -= f * B[k + j * ldb];
            }
        }
    }
    /* Back substitution with the upper factor. */
    for (k = n - 1; k >= 0; k--) {
        for (j = 0; j < nrhs; j++) {
            double s = B[k + j * ldb];
            for (i = k + 1; i < n; i++) {
                s -= A[k + i * lda] * B[i + j * ldb];
            }
            B[k + j * ldb] = s / A[k + k * lda];
        }
    }
}
