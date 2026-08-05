#pragma once

#include <JuceHeader.h>
#include <vector>
#include <cmath>
#include <algorithm>
#include <memory>
#include "SchurLatticeDSP.h"   // shared Schur all-pass engine (../SchurPhaser/Source)
#include "AudioTap.h"          // shared lock-free analyser tap
#include "quilio/PresetManager.h"
#include "quilio/ABSystem.h"

//==============================================================================
/** A simple, allocation-free fractional delay line (linear interpolation). */
class FractionalDelay
{
public:
    void prepare (double sampleRate, float maxMs)
    {
        const int n = (int) std::ceil (maxMs * 0.001 * sampleRate) + 4;
        buffer.assign ((size_t) juce::jmax (8, n), 0.0f);
        write = 0;
    }

    void reset() { std::fill (buffer.begin(), buffer.end(), 0.0f); write = 0; }

    float process (float x, float delaySamples) noexcept
    {
        const int size = (int) buffer.size();
        buffer[(size_t) write] = x;

        float rp = (float) write - juce::jlimit (0.0f, (float) (size - 2), delaySamples);
        if (rp < 0.0f) rp += (float) size;

        const int i0 = (int) rp;
        const float frac = rp - (float) i0;
        const int i1 = (i0 + 1) % size;
        const float y = buffer[(size_t) i0] + frac * (buffer[(size_t) i1] - buffer[(size_t) i0]);

        write = (write + 1) % size;
        return y;
    }

private:
    std::vector<float> buffer;
    int write = 0;
};

//==============================================================================
class PhaseAlignAudioProcessor : public juce::AudioProcessor
{
public:
    PhaseAlignAudioProcessor();
    ~PhaseAlignAudioProcessor() override = default;

    void prepareToPlay (double sampleRate, int samplesPerBlock) override;
    void releaseResources() override {}
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override;
    void processBlock (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }

    const juce::String getName() const override { return JucePlugin_Name; }
    bool acceptsMidi() const override { return false; }
    bool producesMidi() const override { return false; }
    bool isMidiEffect() const override { return false; }
    double getTailLengthSeconds() const override { return 0.05; }

    int getNumPrograms() override;
    int getCurrentProgram() override { return currentProgram; }
    void setCurrentProgram (int) override;
    const juce::String getProgramName (int) override;
    void changeProgramName (int, const juce::String&) override {}

    void getStateInformation (juce::MemoryBlock& destData) override;
    void setStateInformation (const void* data, int sizeInBytes) override;

    juce::AudioProcessorValueTreeState apvts;
    void rebuildDesign();
    static juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();

    //==============================================================================
    // Snapshot polled by the editor to draw the phase/delay curves.
    std::array<std::atomic<float>, schur::kMaxOrder> designK {};
    std::atomic<int>    snapOrder      { 4 };
    std::atomic<float>  snapFreq       { 200.0f };
    std::atomic<float>  snapDelayMs    { 0.0f };
    std::atomic<bool>   snapInvert     { false };
    std::atomic<double> snapSampleRate { 48000.0 };
    std::atomic<float>  snapCorrelation { 1.0f };   // L/R phase correlation, -1..+1

    schurUi::AudioTap tap;                            // post-processing samples for the analyser

    std::unique_ptr<PresetManager> presetManager;
    std::unique_ptr<ABSystem>      abSystem;
    std::atomic<bool>              bypassed { false };

private:
    void maybeRebuild();

    std::array<schur::LatticeEngine, 2> engines;
    std::array<FractionalDelay, 2>      delays;

    // Per-sample smoothing (zipper-free) + audio-thread design rebuild (race-free).
    juce::LinearSmoothedValue<float> mixSm, delaySm;
    float lastStages = -1.0f, lastFreq = -1.0f, lastSpread = -1.0f;
    int currentProgram = 0;

    double currentSampleRate = 48000.0;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (PhaseAlignAudioProcessor)
};
