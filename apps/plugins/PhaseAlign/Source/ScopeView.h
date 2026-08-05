#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"
#include "SchurLookAndFeel.h"   // shared palette + look-and-feel (../SchurPhaser/Source)
#include "SpectrumEngine.h"     // shared FFT analyser

//==============================================================================
/** The alignment visualiser: the all-pass network's phase (the thing you are
    dialling) against a 0-degree reference, or its group delay, on a log-freq
    axis. A vertical marker tracks the pivot frequency and a readout reports the
    total corrective latency (delay line + all-pass group delay at the pivot). */
class ScopeView : public juce::Component,
                  private juce::Timer
{
public:
    enum class Mode { Phase, Spectrum, GroupDelay };

    explicit ScopeView (PhaseAlignAudioProcessor& proc);
    ~ScopeView() override;

    void setMode (Mode m);
    Mode getMode() const noexcept { return mode; }

    void paint (juce::Graphics& g) override;
    void resized() override;
    void mouseMove (const juce::MouseEvent& e) override;
    void mouseExit (const juce::MouseEvent&) override;

private:
    void timerCallback() override;
    float freqToX (float hz) const noexcept;

    static constexpr int kNumPoints = 480;

    PhaseAlignAudioProcessor& processor;
    Mode mode = Mode::Phase;

    std::array<float, kNumPoints> freqHz {};
    std::array<float, kNumPoints> phaseTgt {}, phaseCur {};
    std::array<float, kNumPoints> delayTgt {}, delayCur {};

    schurUi::SpectrumEngine spectrum;
    std::array<float, 4096> drainL {}, drainR {};

    float delayScaleMs = 4.0f;
    double sampleRate = 48000.0;
    float pivotHz = 200.0f;
    float extraDelayMs = 0.0f;
    bool  inverted = false;
    float hoverX = -1.0f;

    juce::Rectangle<float> plot;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (ScopeView)
};
