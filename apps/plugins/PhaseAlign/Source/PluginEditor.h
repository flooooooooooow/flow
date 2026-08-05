#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"
#include "SchurLookAndFeel.h"   // shared look-and-feel (../SchurPhaser/Source)
#include "CorrelationMeter.h"   // shared correlation meter
#include "PluginTopBar.h"       // shared house-style top bar
#include "quilio/TopBar.h"      // 1:1 Quilio top bar
#include "ScopeView.h"

class PhaseAlignAudioProcessorEditor : public juce::AudioProcessorEditor
{
public:
    explicit PhaseAlignAudioProcessorEditor (PhaseAlignAudioProcessor&);
    ~PhaseAlignAudioProcessorEditor() override { setLookAndFeel (nullptr); }

    void paint (juce::Graphics& g) override;
    void resized() override;

private:
    PhaseAlignAudioProcessor& audioProcessor;
    schurUi::SchurLookAndFeel laf;

    ScopeView scope;
    schurUi::CorrelationMeter meter;
    TopBar                    quilioBar;   // A/B · bypass · undo · preset · save
    schurUi::PluginTopBar     topBar;      // transparent strip: title + view tabs

    void loadProgram (int index);
    void toggleInvert();

    juce::Slider delaySlider, freqSlider, stagesSlider, spreadSlider, mixSlider;
    juce::Label  delayLabel, freqLabel, stagesLabel, spreadLabel, mixLabel;

    using SAtt = juce::AudioProcessorValueTreeState::SliderAttachment;
    std::unique_ptr<SAtt> delayAtt, freqAtt, stagesAtt, spreadAtt, mixAtt;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (PhaseAlignAudioProcessorEditor)
};
