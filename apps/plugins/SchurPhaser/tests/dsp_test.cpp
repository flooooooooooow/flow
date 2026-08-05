// dsp_test — correctness tests for the shared Schur all-pass DSP.
// No JUCE required: compiles against Source/SchurLatticeDSP.{h,cpp} only.
//
//   clang++ -O2 -std=c++17 dsp_test.cpp ../Source/SchurLatticeDSP.cpp -o dsp_test && ./dsp_test
//
// Validates the properties a production all-pass must hold:
//   1. magnitude is flat (0 dB) at every frequency — the defining property
//   2. the analytic group delay matches the numeric derivative of the phase
//   3. Schur design keeps every reflection coefficient stable (|k| < 1)
//   4. a single real pole maps to the expected reflection coefficient

#include "../Source/SchurLatticeDSP.h"
#include <cstdio>
#include <cmath>
#include <vector>

namespace
{
int g_fail = 0;
void check (bool cond, const char* name, const char* detail = "")
{
    printf ("  [%s] %s%s%s\n", cond ? "PASS" : "FAIL", name,
            detail[0] ? " — " : "", detail);
    if (! cond) ++g_fail;
}

constexpr double sr = 48000.0;
constexpr int    NP = 4000;
} // namespace

int main()
{
    printf ("dsp_test — Schur all-pass DSP\n\n");

    // A representative many-pole design.
    float poles[schur::kMaxOrder] {};
    const int order = 8;
    schur::LatticeEngine::designPolesFromParams (order, 0.6f, 0.7f, poles);

    schur::LatticeEngine eng;
    eng.setSampleRate (sr);
    eng.designFromPoles (poles, order);
    const int n = eng.order;
    const float* k = eng.kBase.data();

    std::vector<float> freq (NP), phase (NP), gdMs (NP), notch (NP);
    schur::computeResponse (k, n, /*mix*/ 0.0f, sr, NP,
                            freq.data(), phase.data(), gdMs.data(), notch.data());

    // ---- 1. magnitude flatness (pure all-pass => |H| == 1) ----
    {
        std::vector<float> magDb (NP), ph (NP), fr (NP);
        schur::computeFrequencyResponse (k, n, sr, NP, magDb.data(), ph.data(), fr.data());
        double maxAbsDb = 0.0;
        for (int i = 0; i < NP; ++i) maxAbsDb = std::max (maxAbsDb, (double) std::fabs (magDb[i]));
        char d[64]; snprintf (d, sizeof d, "max |mag| = %.2e dB", maxAbsDb);
        check (maxAbsDb < 1e-3, "magnitude flat to <1e-3 dB", d);
    }

    // ---- 2. analytic group delay == numeric derivative of phase ----
    {
        int good = 0, tested = 0;
        for (int i = 1; i < NP - 1; ++i)
        {
            // skip bins straddling a +/-180 wrap (numeric derivative ill-defined there)
            double dphi = (phase[i + 1] - phase[i - 1]);
            if (std::fabs (dphi) > 180.0) continue;
            const double dw = 2.0 * M_PI * (freq[i + 1] - freq[i - 1]) / sr;   // rad/sample
            const double tauNum = -(dphi * M_PI / 180.0) / dw;                 // samples
            const double tauAna = gdMs[i] * sr / 1000.0;                        // samples
            const double rel = std::fabs (tauNum - tauAna) / std::max (1.0, std::fabs (tauAna));
            ++tested;
            if (rel < 0.03) ++good;
        }
        const double frac = tested ? (double) good / tested : 0.0;
        char d[80]; snprintf (d, sizeof d, "%.1f%% of %d bins within 3%%", 100.0 * frac, tested);
        check (frac > 0.95, "group delay: analytic == numeric", d);
    }

    // ---- 3. stability: every reflection coefficient strictly inside the unit circle ----
    {
        double maxAbsK = 0.0;
        for (int i = 0; i < n; ++i) maxAbsK = std::max (maxAbsK, (double) std::fabs (k[i]));
        char d[48]; snprintf (d, sizeof d, "max |k| = %.4f", maxAbsK);
        check (maxAbsK < 1.0, "all reflection coeffs |k| < 1", d);
    }

    // ---- 4. single real pole p => first-order all-pass coeff k0 == -p ----
    // H(z) = (k + z^-1)/(1 + k z^-1) has its pole at z = -k, so a pole at z = p needs k = -p.
    {
        const float p = 0.7f;
        schur::LatticeEngine e2;
        e2.designFromPoles (&p, 1);
        const float k0 = e2.kBase[0];
        char d[48]; snprintf (d, sizeof d, "k0 = %.4f (expected %.4f)", k0, -p);
        check (std::fabs (k0 - (-p)) < 1e-5f, "single-pole Schur coeff", d);
    }

    printf ("\n%s (%d failure%s)\n", g_fail == 0 ? "ALL PASS" : "FAILED",
            g_fail, g_fail == 1 ? "" : "s");
    return g_fail == 0 ? 0 : 1;
}
