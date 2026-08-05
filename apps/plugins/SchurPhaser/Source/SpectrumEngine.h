#pragma once

#include <JuceHeader.h>
#include <array>
#include <cmath>

namespace schurUi
{

//==============================================================================
/** Rolling FFT magnitude analyser for the visualisers. Fed a mono stream on the
    editor timer; produces a smoothed, log-frequency magnitude curve in dB. */
class SpectrumEngine
{
public:
    static constexpr int fftOrder = 11;
    static constexpr int fftSize  = 1 << fftOrder;   // 2048
    static constexpr int numBins  = fftSize / 2;

    SpectrumEngine()
        : fft (fftOrder),
          window ((size_t) fftSize, juce::dsp::WindowingFunction<float>::hann)
    {
        ring.fill (0.0f);
        magDb.fill (-120.0f);
    }

    /** Push freshly drained samples into the rolling ring buffer. */
    void pushSamples (const float* mono, int n) noexcept
    {
        for (int i = 0; i < n; ++i)
        {
            ring[(size_t) widx] = mono[i];
            widx = (widx + 1) & (fftSize - 1);
        }
        primed = true;
    }

    /** Recompute the magnitude spectrum from the current ring contents. */
    void render (float attack = 0.5f, float release = 0.28f) noexcept
    {
        if (! primed) return;

        for (int i = 0; i < fftSize; ++i)
            fftData[(size_t) i] = ring[(size_t) ((widx + i) & (fftSize - 1))];
        for (int i = fftSize; i < 2 * fftSize; ++i)
            fftData[(size_t) i] = 0.0f;

        window.multiplyWithWindowingTable (fftData.data(), (size_t) fftSize);
        fft.performFrequencyOnlyForwardTransform (fftData.data());

        const float norm = 2.0f / (float) fftSize;
        for (int b = 0; b < numBins; ++b)
        {
            const float mag = fftData[(size_t) b] * norm;
            const float db = juce::Decibels::gainToDecibels (mag + 1.0e-9f, -120.0f);
            const float prev = magDb[(size_t) b];
            const float coeff = (db > prev) ? attack : release;   // peak-ish ballistics
            magDb[(size_t) b] = prev + coeff * (db - prev);
        }
    }

    /** Interpolated magnitude (dB) at an arbitrary frequency. */
    float dbAtFreq (float hz, double sampleRate) const noexcept
    {
        const float binF = hz * (float) fftSize / (float) sampleRate;
        if (binF <= 0.0f) return magDb[0];
        if (binF >= (float) (numBins - 1)) return magDb[(size_t) (numBins - 1)];
        const int b0 = (int) binF;
        const float f = binF - (float) b0;
        return magDb[(size_t) b0] + f * (magDb[(size_t) (b0 + 1)] - magDb[(size_t) b0]);
    }

private:
    juce::dsp::FFT fft;
    juce::dsp::WindowingFunction<float> window;
    std::array<float, fftSize> ring {};
    std::array<float, 2 * fftSize> fftData {};
    std::array<float, numBins> magDb {};
    int widx = 0;
    bool primed = false;
};

} // namespace schurUi
