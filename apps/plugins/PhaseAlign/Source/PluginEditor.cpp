#include "PluginEditor.h"

namespace
{
constexpr int kWidth   = 660;
constexpr int kHeight  = 558;
constexpr int kMargin  = 18;
constexpr int kQuilioH = 44;
constexpr int kViewH   = 34;
constexpr int kChrome  = kQuilioH + kViewH;
constexpr int kScopeH  = 232;
constexpr int kMeterH  = 52;
constexpr int kGap     = 12;
constexpr int kLabelH  = 15;
} // namespace

PhaseAlignAudioProcessorEditor::PhaseAlignAudioProcessorEditor (PhaseAlignAudioProcessor& p)
    : AudioProcessorEditor (&p), audioProcessor (p), scope (p), meter (p.snapCorrelation),
      quilioBar (*p.presetManager, *p.abSystem)
{
    setLookAndFeel (&laf);
    setSize (kWidth, kHeight);
    setResizable (false, false);

    addAndMakeVisible (scope);
    addAndMakeVisible (meter);

    // ---- Quilio top bar: A/B · bypass · undo/redo · preset · save ----
    addAndMakeVisible (quilioBar);
    quilioBar.getBypassed    = [this] { return audioProcessor.bypassed.load(); };
    quilioBar.onToggleBypass = [this] { audioProcessor.bypassed.store (! audioProcessor.bypassed.load()); };

    // ---- transparent strip below: plugin name + view tabs + invert ----
    addAndMakeVisible (topBar);
    topBar.setDrawBackground (false);
    topBar.setTitle ("PHASE ALIGN");
    topBar.setSubtitle ("All-Pass Phase Rotator");

    using M = ScopeView::Mode;
    topBar.addTab ("PHASE",    [this] { return scope.getMode() == M::Phase; },      [this] { scope.setMode (M::Phase); topBar.repaint(); });
    topBar.addTab ("SPECTRUM", [this] { return scope.getMode() == M::Spectrum; },   [this] { scope.setMode (M::Spectrum); topBar.repaint(); });
    topBar.addTab ("DELAY",    [this] { return scope.getMode() == M::GroupDelay; }, [this] { scope.setMode (M::GroupDelay); topBar.repaint(); });
    topBar.addTab (juce::String::fromUTF8 ("\xc3\xb8 INV"),
                   [this] { return *audioProcessor.apvts.getRawParameterValue ("invert") > 0.5f; },
                   [this] { toggleInvert(); });

    auto addKnob = [&] (juce::Slider& s, juce::Label& l, const juce::String& name,
                        juce::Colour accent, const juce::String& suffix = {})
    {
        addAndMakeVisible (s);
        addAndMakeVisible (l);
        schurUi::styleKnob (s, accent, suffix);
        schurUi::styleLabel (l, name);
    };

    addKnob (delaySlider,  delayLabel,  "DELAY",  schurUi::Palette::accent, " ms");
    addKnob (freqSlider,   freqLabel,   "FREQ",   schurUi::Palette::accent, " Hz");
    addKnob (stagesSlider, stagesLabel, "STAGES", schurUi::Palette::accent2);
    addKnob (spreadSlider, spreadLabel, "SPREAD", schurUi::Palette::accent2);
    addKnob (mixSlider,    mixLabel,    "MIX",    schurUi::Palette::accent);

    delayAtt  = std::make_unique<SAtt> (audioProcessor.apvts, "delay", delaySlider);
    freqAtt   = std::make_unique<SAtt> (audioProcessor.apvts, "freq", freqSlider);
    stagesAtt = std::make_unique<SAtt> (audioProcessor.apvts, "stages", stagesSlider);
    spreadAtt = std::make_unique<SAtt> (audioProcessor.apvts, "spread", spreadSlider);
    mixAtt    = std::make_unique<SAtt> (audioProcessor.apvts, "mix", mixSlider);
}

void PhaseAlignAudioProcessorEditor::loadProgram (int index)
{
    audioProcessor.setCurrentProgram (index);
    topBar.repaint();
}

void PhaseAlignAudioProcessorEditor::toggleInvert()
{
    if (auto* p = audioProcessor.apvts.getParameter ("invert"))
    {
        const bool now = *audioProcessor.apvts.getRawParameterValue ("invert") > 0.5f;
        p->setValueNotifyingHost (now ? 0.0f : 1.0f);
    }
    topBar.repaint();
}

void PhaseAlignAudioProcessorEditor::paint (juce::Graphics& g)
{
    auto bounds = getLocalBounds().toFloat();
    juce::ColourGradient bg (schurUi::Palette::bgTop, bounds.getCentreX(), (float) kQuilioH,
                             schurUi::Palette::bgBottom, bounds.getCentreX(), bounds.getBottom(), false);
    g.setGradientFill (bg);
    g.fillRect (0, kQuilioH, getWidth(), getHeight() - kQuilioH);
}

void PhaseAlignAudioProcessorEditor::resized()
{
    quilioBar.setBounds (0, 0, getWidth(), kQuilioH);
    topBar.setBounds (0, kQuilioH, getWidth(), kViewH);

    auto area = getLocalBounds();
    area.removeFromTop (kChrome);
    area = area.reduced (kMargin);

    scope.setBounds (area.removeFromTop (kScopeH));
    area.removeFromTop (kGap);
    meter.setBounds (area.removeFromTop (kMeterH));
    area.removeFromTop (kGap + 4);

    juce::Slider* sliders[] = { &delaySlider, &freqSlider, &stagesSlider, &spreadSlider, &mixSlider };
    juce::Label*  labels[]  = { &delayLabel, &freqLabel, &stagesLabel, &spreadLabel, &mixLabel };
    const int count = 5;
    const int cellW = area.getWidth() / count;
    for (int i = 0; i < count; ++i)
    {
        auto cell = area.withWidth (cellW).withX (area.getX() + i * cellW);
        labels[i]->setBounds (cell.removeFromTop (kLabelH));
        sliders[i]->setBounds (cell.reduced (8, 2));
    }
}
