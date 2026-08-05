#pragma once

#include <array>
#include <cmath>
#include <algorithm>

namespace schur
{

constexpr int kMaxOrder = 16;

/** Schur step-down + cascade all-pass H_i(z)=(k_i+z^-1)/(1+k_i z^-1). */
class LatticeEngine
{
public:
    void setSampleRate (double sr) noexcept { sampleRate = sr; }

    void designFromPoles (const float* poles, int count) noexcept;

    /** Set coefficients and clear filter state (use at prepare / structural reset). */
    void setBaseReflections (const float* k, int count) noexcept;

    /** Update coefficients in place WITHOUT clearing state — click-free for live
        parameter changes on the audio thread. */
    void updateReflections (const float* k, int count) noexcept;

    void reset() noexcept;

    /** Per-sample: modulate k_i then cascade. */
    float processSample (float input,
                         const float* kLive,
                         int order) noexcept;

    void fillModulatedK (float timeSec,
                         float depth,
                         float rateHz,
                         float stereoPhase,
                         float* kOut,
                         int order) const noexcept;

    static void designPolesFromParams (int order,
                                     float color,
                                     float spread,
                                     float* polesOut) noexcept;

    static int schurStepDown (const float* a, int order, float* kOut) noexcept;

    std::array<float, kMaxOrder> kBase {};
    int order = 4;

private:
    std::array<float, kMaxOrder> xPrev {};
    std::array<float, kMaxOrder> yPrev {};
    double sampleRate = 48000.0;
};

/** Magnitude/phase of cascade at frequency f (for UI). */
void computeFrequencyResponse (const float* k,
                             int order,
                             double sampleRate,
                             int numPoints,
                             float* magDb,
                             float* phaseDeg,
                             float* frequenciesHz) noexcept;

/** Full analysis curves for the visualiser, sampled on a log-frequency axis.
    Any of the output pointers may be null. `mix` (0..1) folds the all-pass
    against the dry path so `notchDb` shows the audible comb the ear hears.   */
void computeResponse (const float* k,
                      int order,
                      float mix,
                      double sampleRate,
                      int numPoints,
                      float* frequenciesHz,   // log-spaced bin centres
                      float* phaseDeg,        // wrapped all-pass phase, [-180,180]
                      float* groupDelayMs,    // exact cascade group delay
                      float* notchDb) noexcept; // magnitude of dry+wet mix

} // namespace schur