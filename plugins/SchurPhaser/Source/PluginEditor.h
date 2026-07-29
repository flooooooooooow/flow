#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"
#include "SchurLookAndFeel.h"
#include "PhaseScope.h"
#include "PluginTopBar.h"
#include "TopBar.h"          // SDK shared top bar (QuilioSDK/quilio_ui/components)

class SchurPhaserAudioProcessorEditor : public juce::AudioProcessorEditor
{
public:
    explicit SchurPhaserAudioProcessorEditor (SchurPhaserAudioProcessor&);
    ~SchurPhaserAudioProcessorEditor() override { setLookAndFeel (nullptr); }

    void paint (juce::Graphics& g) override;
    void resized() override;

private:
    void layoutKnobRow (juce::Rectangle<int> area,
                        juce::Slider* sliders[],
                        juce::Label* labels[],
                        int count);

    SchurPhaserAudioProcessor& audioProcessor;
    schurUi::SchurLookAndFeel laf;

    schurUi::PhaseScope        scope;
    schurUi::ReflectionLattice lattice;
    TopBar                     quilioBar;   // A/B · bypass · undo · preset · save
    schurUi::PluginTopBar      topBar;      // transparent strip: title + view tabs

    juce::ComboBox   divBox;
    void loadProgram (int index);
    void toggleSync();

    juce::Slider rateSlider, depthSlider, widthSlider, mixSlider;
    juce::Slider stagesSlider, toneSlider, spreadSlider, emphasisSlider;

    juce::Label rateLabel, depthLabel, widthLabel, mixLabel;
    juce::Label stagesLabel, toneLabel, spreadLabel, emphasisLabel;

    using Att = juce::AudioProcessorValueTreeState::SliderAttachment;
    std::unique_ptr<Att> rateAtt, depthAtt, widthAtt, mixAtt;
    std::unique_ptr<Att> stagesAtt, toneAtt, spreadAtt, emphasisAtt;
    std::unique_ptr<juce::AudioProcessorValueTreeState::ComboBoxAttachment> divAtt;
    std::unique_ptr<juce::ParameterAttachment> syncWatch;   // refresh UI when sync changes (preset/host)

    void updateSyncUI();

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SchurPhaserAudioProcessorEditor)
};
