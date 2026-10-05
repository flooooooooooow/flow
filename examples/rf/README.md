# RF / SDR Examples

Programs demonstrating complex number arithmetic (`c64`/`c128`) for
RF and software-defined radio applications.

## Programs

| Program | Description |
|---------|-------------|
| `dft.flow` | 8-point DFT using complex exponentials. Verifies spectral peaks. |
| `iq_mixer.flow` | Quadrature mixer: multiplies a baseband signal by a complex carrier. |
| `sdr_receiver.flow` | SDR receiver: tone generation, LO mixing, baseband output. Uses `stdlib/rf.flow`. |

## Running

```bash
FLOW_HOST=python ./flow run examples/rf/dft.flow
FLOW_HOST=python ./flow run examples/rf/iq_mixer.flow
```

## Complex types

- `c64` maps to C99 `float complex` (two f32s)
- `c128` maps to C99 `double complex` (two f64s)
- Constructors: `c64(re, im)`, `c128(re, im)`, or `c64(x)` for a real-only value
- Math: `creal`, `cimag`, `cabs`, `carg`, `conj`, `cexp`, `clog`, `csqrt`, `cpow`
- Arithmetic: `+`, `-`, `*`, `/` work on complex types with automatic promotion
