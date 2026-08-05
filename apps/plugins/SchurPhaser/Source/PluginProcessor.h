#pragma once

#include <JuceHeader.h>
#include <memory>
#include "SchurLatticeDSP.h"
#include "AudioTap.h"

class SchurPhaserAudioProcessor : public juce::AudioProcessor
{
public:
    SchurPhaserAudioProcessor();
    ~SchurPhaserAudioProcessor() override = default;

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
    // Lock-free snapshot the editor polls at frame rate to animate the visualiser.
    std::array<std::atomic<float>, schur::kMaxOrder> liveK {};   // LFO-modulated k_i (ch 0)
    std::array<std::atomic<float>, schur::kMaxOrder> baseK {};   // design k_i (no modulation)
    std::atomic<int>    snapOrder    { 4 };
    std::atomic<float>  snapMix      { 0.75f };
    std::atomic<float>  snapDepth    { 0.12f };
    std::atomic<double> snapSampleRate { 48000.0 };
    std::atomic<bool>   snapActive   { false };   // true while audio is flowing
    std::atomic<float>  snapRateHz   { 0.8f };    // effective LFO rate (post-sync)

    schurUi::AudioTap tap;                          // post-processing samples for the analyser
    std::atomic<bool> bypassed { false };           // soft bypass driven by the top bar

private:
    std::array<schur::LatticeEngine, 2> engines;
    std::array<float, schur::kMaxOrder> kScratch {};

    double currentSampleRate = 48000.0;
    double phaseTime = 0.0;
    int currentProgram = 0;

    // Per-sample smoothing to remove zipper noise on the audible controls.
    juce::LinearSmoothedValue<float> mixSm, depthSm, widthSm;

    // Design is rebuilt on the audio thread when these change (no cross-thread race).
    float lastSections = -1.0f, lastColor = -1.0f, lastSpread = -1.0f, lastEmphasis = -999.0f;
    void maybeRebuild();

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SchurPhaserAudioProcessor)
};