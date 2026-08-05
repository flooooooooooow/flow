#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"
#include "SchurLookAndFeel.h"
#include "SpectrumEngine.h"

namespace schurUi
{

//==============================================================================
/** The main visualiser: a live, log-frequency analysis of the Schur all-pass
    cascade. Shows the audible notch comb (filled), plus a switchable primary
    curve — the all-pass phase or its group delay — animated from a lock-free
    snapshot the audio thread publishes each block. */
class PhaseScope : public juce::Component,
                   private juce::Timer
{
public:
    enum class Mode { Phase, Spectrum, GroupDelay };

    explicit PhaseScope (SchurPhaserAudioProcessor& proc);
    ~PhaseScope() override;

    void setMode (Mode m);
    Mode getMode() const noexcept { return mode; }

    void paint (juce::Graphics& g) override;
    void resized() override;

    void mouseMove  (const juce::MouseEvent& e) override;
    void mouseExit  (const juce::MouseEvent& e) override;

private:
    void timerCallback() override;

    float freqToX (float hz) const noexcept;
    float xToFreq (float x)  const noexcept;

    static constexpr int kNumPoints = 480;

    SchurPhaserAudioProcessor& processor;
    Mode mode = Mode::Phase;

    // target (freshly computed) and displayed (smoothed) curves
    std::array<float, kNumPoints> freqHz {};
    std::array<float, kNumPoints> phaseTgt {}, phaseCur {};
    std::array<float, kNumPoints> delayTgt {}, delayCur {};
    std::array<float, kNumPoints> notchTgt {}, notchCur {};

    float delayScaleMs = 6.0f;     // smoothed autoscale for group delay
    float idlePhase    = 0.0f;     // fallback LFO when transport is stopped
    double sampleRate  = 48000.0;

    SpectrumEngine spectrum;
    std::array<float, 4096> drainL {}, drainR {};

    float hoverX = -1.0f;          // cursor scrub position, <0 = hidden

    juce::Rectangle<float> plot;   // inner plotting area

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (PhaseScope)
};

//==============================================================================
/** A compact meter of the Schur reflection coefficients k_i. Each section is a
    vertical bar from the centre line to ±k_i; the faint marker is the design
    value, the bright bar the live modulated value. This is the lattice's
    signature — the numbers that actually define the all-pass. */
class ReflectionLattice : public juce::Component,
                          private juce::Timer
{
public:
    explicit ReflectionLattice (SchurPhaserAudioProcessor& proc);
    ~ReflectionLattice() override;

    void paint (juce::Graphics& g) override;

private:
    void timerCallback() override;

    SchurPhaserAudioProcessor& processor;
    std::array<float, schur::kMaxOrder> liveCur {}, baseCur {};
    int order = 4;
    float idlePhase = 0.0f;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (ReflectionLattice)
};

} // namespace schurUi
