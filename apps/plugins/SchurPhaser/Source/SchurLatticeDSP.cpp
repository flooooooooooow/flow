#include "SchurLatticeDSP.h"
#include <complex>

namespace schur
{

static float clampK (float k) noexcept
{
    if (! std::isfinite (k)) return 0.0f;   // NaN/Inf-safe: never let a bad coeff propagate
    return std::clamp (k, -0.999f, 0.999f);
}

void LatticeEngine::reset() noexcept
{
    xPrev.fill (0.0f);
    yPrev.fill (0.0f);
}

void LatticeEngine::setBaseReflections (const float* k, int count) noexcept
{
    updateReflections (k, count);
    reset();
}

void LatticeEngine::updateReflections (const float* k, int count) noexcept
{
    order = std::clamp (count, 1, kMaxOrder);
    for (int i = 0; i < order; ++i)
        kBase[(size_t) i] = clampK (k[i]);
}

static void denomMulMonic (const float* d1, int o1, const float* d2, int o2, float* out) noexcept
{
    const int outOrder = o1 + o2;
    for (int i = 0; i < outOrder; ++i)
        out[i] = 0.0f;

    for (int k = 1; k <= outOrder; ++k)
    {
        float sum = 0.0f;
        if (k <= o2) sum += d2[k - 1];
        if (k <= o1) sum += d1[k - 1];
        for (int i = 1; i <= o1; ++i)
        {
            const int j = k - i;
            if (j >= 1 && j <= o2)
                sum += d1[i - 1] * d2[j - 1];
        }
        out[k - 1] = sum;
    }
}

int LatticeEngine::schurStepDown (const float* a, int n, float* kOut) noexcept
{
    float work[kMaxOrder] {};
    for (int i = 0; i < n; ++i)
        work[i] = a[i];

    int stage = n;
    while (stage > 0)
    {
        const int idx = stage - 1;
        const float kn = clampK (work[idx]);
        kOut[idx] = kn;
        const float denom = 1.0f - kn * kn;
        if (stage > 1)
        {
            for (int m = 0; m < stage - 1; ++m)
            {
                const int rev = stage - 2 - m;
                work[m] = (work[m] - kn * work[rev]) / denom;
            }
        }
        --stage;
    }
    return n;
}

void LatticeEngine::designFromPoles (const float* poles, int count) noexcept
{
    float acc[kMaxOrder] {};
    float tmp[kMaxOrder] {};
    float one[1] {};
    int ord = 0;

    const int n = std::clamp (count, 1, kMaxOrder);
    for (int p = 0; p < n; ++p)
    {
        one[0] = -poles[p];
        if (ord == 0)
        {
            acc[0] = one[0];
            ord = 1;
        }
        else
        {
            const int newOrd = ord + 1;
            denomMulMonic (acc, ord, one, 1, tmp);
            for (int i = 0; i < newOrd; ++i)
                acc[i] = tmp[i];
            ord = newOrd;
        }
    }

    float k[kMaxOrder] {};
    schurStepDown (acc, ord, k);
    updateReflections (k, ord);   // no state reset — safe for live audio-thread rebuilds
}

void LatticeEngine::designPolesFromParams (int orderIn,
                                           float color,
                                           float spread,
                                           float* polesOut) noexcept
{
    const int n = std::clamp (orderIn, 2, kMaxOrder);
    const float r = std::clamp (color, 0.15f, 0.92f);
    for (int i = 0; i < n; ++i)
    {
        const float t = (n <= 1) ? 0.0f : (float) i / (float) (n - 1);
        polesOut[i] = r * (1.0f - spread * t * 0.85f);
    }
}

void LatticeEngine::fillModulatedK (float timeSec,
                                    float depth,
                                    float rateHz,
                                    float stereoPhase,
                                    float* kOut,
                                    int n) const noexcept
{
    constexpr float twoPi = 6.28318530718f;
    const float omega = twoPi * rateHz;
    for (int i = 0; i < n; ++i)
    {
        const float sectionPhase = (float) i * 0.31f + stereoPhase;
        const float wobble = depth * std::sin (omega * timeSec + sectionPhase);
        kOut[i] = clampK (kBase[(size_t) i] + wobble);
    }
}

float LatticeEngine::processSample (float input,
                                    const float* kLive,
                                    int n) noexcept
{
    float inp = input;
    for (int i = 0; i < n; ++i)
    {
        const float ki = kLive[i];
        const float y = ki * inp + xPrev[(size_t) i] - ki * yPrev[(size_t) i];
        xPrev[(size_t) i] = inp;
        yPrev[(size_t) i] = y;
        inp = y;
    }
    return inp;
}

void computeFrequencyResponse (const float* k,
                             int order,
                             double sampleRate,
                             int numPoints,
                             float* magDb,
                             float* phaseDeg,
                             float* frequenciesHz) noexcept
{
    const float fMin = 30.0f;
    const float fMax = (float) (sampleRate * 0.45);
    const float logMin = std::log10 (fMin);
    const float logMax = std::log10 (fMax);

    for (int i = 0; i < numPoints; ++i)
    {
        const float t = (numPoints <= 1) ? 0.0f : (float) i / (float) (numPoints - 1);
        const float freq = std::pow (10.0f, logMin + t * (logMax - logMin));
        frequenciesHz[i] = freq;

        const float w = 6.28318530718f * freq / (float) sampleRate;
        std::complex<float> z { std::cos (w), std::sin (w) };
        std::complex<float> H { 1.0f, 0.0f };

        for (int s = 0; s < order; ++s)
        {
            const float ki = k[s];
            // H(z) = (k + z^-1)/(1 + k z^-1); at z = e^{jw} the denominator uses e^{-jw}.
            const std::complex<float> zc = std::conj (z);
            const std::complex<float> num = ki + zc;
            const std::complex<float> den = 1.0f + ki * zc;
            H *= num / den;
        }

        magDb[i] = 20.0f * std::log10 (std::abs (H) + 1e-12f);
        phaseDeg[i] = std::atan2 (H.imag(), H.real()) * 57.2957795f;
    }
}

void computeResponse (const float* k,
                      int order,
                      float mix,
                      double sampleRate,
                      int numPoints,
                      float* frequenciesHz,
                      float* phaseDeg,
                      float* groupDelayMs,
                      float* notchDb) noexcept
{
    const float fMin = 20.0f;
    const float fMax = (float) (sampleRate * 0.49);
    const float logMin = std::log10 (fMin);
    const float logMax = std::log10 (fMax);
    const float sr     = (float) sampleRate;
    const float m      = std::clamp (mix, 0.0f, 1.0f);

    for (int i = 0; i < numPoints; ++i)
    {
        const float t = (numPoints <= 1) ? 0.0f : (float) i / (float) (numPoints - 1);
        const float freq = std::pow (10.0f, logMin + t * (logMax - logMin));
        if (frequenciesHz != nullptr)
            frequenciesHz[i] = freq;

        const float w    = 6.28318530718f * freq / sr;
        const float cosw = std::cos (w);
        const float sinw = std::sin (w);
        const std::complex<float> zc { cosw, -sinw };        // e^{-jw}

        std::complex<float> H { 1.0f, 0.0f };
        float tau = 0.0f;                                    // group delay in samples
        for (int s = 0; s < order; ++s)
        {
            const float ki = k[s];
            H *= (ki + zc) / (1.0f + ki * zc);   // denominator uses e^{-jw}, matching H(z)
            // exact first-order all-pass group delay (pole at z = -ki)
            tau += (1.0f - ki * ki) / (1.0f + 2.0f * ki * cosw + ki * ki + 1e-9f);
        }

        if (phaseDeg != nullptr)
            phaseDeg[i] = std::atan2 (H.imag(), H.real()) * 57.2957795f;

        if (groupDelayMs != nullptr)
            groupDelayMs[i] = tau * 1000.0f / sr;

        if (notchDb != nullptr)
        {
            const std::complex<float> mixed = (1.0f - m) + m * H;    // dry + wet
            notchDb[i] = 20.0f * std::log10 (std::abs (mixed) + 1e-9f);
        }
    }
}

} // namespace schur