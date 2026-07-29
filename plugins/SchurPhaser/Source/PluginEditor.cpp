#include "PluginEditor.h"

namespace
{
constexpr int kWidth   = 720;
constexpr int kHeight  = 722;
constexpr int kMargin  = 18;
constexpr int kQuilioH = 44;    // Quilio top bar
constexpr int kViewH   = 34;    // transparent title + view-tab strip
constexpr int kChrome  = kQuilioH + kViewH;
constexpr int kScopeH  = 262;
constexpr int kLatticeH = 64;
constexpr int kGap     = 12;
constexpr int kLabelH  = 15;

const juce::StringArray kDivLabelsUI {
    "1/1", "1/2.", "1/2", "1/2T", "1/4.", "1/4", "1/4T", "1/8.", "1/8", "1/8T", "1/16", "1/16T" };
} // namespace

SchurPhaserAudioProcessorEditor::SchurPhaserAudioProcessorEditor (SchurPhaserAudioProcessor& p)
    : AudioProcessorEditor (&p), audioProcessor (p),
      scope (p), lattice (p)
{
    setLookAndFeel (&laf);
    setSize (kWidth, kHeight);
    setResizable (false, false);

    addAndMakeVisible (scope);
    addAndMakeVisible (lattice);

    // ---- SDK quilio_ui top bar (compiled from QuilioSDK) ----
    addAndMakeVisible (quilioBar);
    quilioBar.getBypassed    = [this] { return audioProcessor.bypassed.load(); };
    quilioBar.onToggleBypass = [this] { audioProcessor.bypassed.store (! audioProcessor.bypassed.load()); };
    quilioBar.getPresetList = [this]
    {
        juce::StringArray names;
        for (int i = 0; i < audioProcessor.getNumPrograms(); ++i)
            names.add (audioProcessor.getProgramName (i));
        return names;
    };
    quilioBar.getCurrentPresetIndex = [this] { return audioProcessor.getCurrentProgram(); };
    quilioBar.getCurrentPresetName  = [this] { return audioProcessor.getProgramName (audioProcessor.getCurrentProgram()); };
    quilioBar.onLoadPreset          = [this] (int i) { loadProgram (i); };

    // ---- transparent strip below: plugin name + view tabs + sync ----
    addAndMakeVisible (topBar);
    topBar.setDrawBackground (false);
    topBar.setTitle ("SCHUR PHASE");
    topBar.setSubtitle ("All-Pass Lattice Phaser");

    using M = schurUi::PhaseScope::Mode;
    topBar.addTab ("PHASE",    [this] { return scope.getMode() == M::Phase; },      [this] { scope.setMode (M::Phase); topBar.repaint(); });
    topBar.addTab ("SPECTRUM", [this] { return scope.getMode() == M::Spectrum; },   [this] { scope.setMode (M::Spectrum); topBar.repaint(); });
    topBar.addTab ("DELAY",    [this] { return scope.getMode() == M::GroupDelay; }, [this] { scope.setMode (M::GroupDelay); topBar.repaint(); });
    topBar.addTab ("SYNC",     [this] { return *audioProcessor.apvts.getRawParameterValue ("sync") > 0.5f; },
                               [this] { toggleSync(); });
    topBar.setReservedWidth (64);   // division combo slot

    // division combo lives in the top bar's reserved slot
    addAndMakeVisible (divBox);
    divBox.addItemList (kDivLabelsUI, 1);
    divBox.setColour (juce::ComboBox::backgroundColourId, schurUi::Palette::track.withAlpha (0.35f));
    divBox.setColour (juce::ComboBox::textColourId, schurUi::Palette::text);
    divBox.setColour (juce::ComboBox::outlineColourId, schurUi::Palette::panelEdge);
    divBox.setColour (juce::ComboBox::arrowColourId, schurUi::Palette::accent);
    divBox.setJustificationType (juce::Justification::centred);
    divAtt = std::make_unique<juce::AudioProcessorValueTreeState::ComboBoxAttachment> (
        audioProcessor.apvts, "syncdiv", divBox);

    // ---- knobs ----
    auto addKnob = [&] (juce::Slider& s, juce::Label& l, const juce::String& name,
                        juce::Colour accent, const juce::String& suffix = {})
    {
        addAndMakeVisible (s);
        addAndMakeVisible (l);
        schurUi::styleKnob (s, accent, suffix);
        schurUi::styleLabel (l, name);
    };

    addKnob (rateSlider,  rateLabel,  "RATE",  schurUi::Palette::accent, " Hz");
    addKnob (depthSlider, depthLabel, "DEPTH", schurUi::Palette::accent);
    addKnob (widthSlider, widthLabel, "WIDTH", schurUi::Palette::accent);
    addKnob (mixSlider,   mixLabel,   "MIX",   schurUi::Palette::accent);

    addKnob (stagesSlider,   stagesLabel,   "STAGES",   schurUi::Palette::accent2);
    addKnob (toneSlider,     toneLabel,     "TONE",     schurUi::Palette::accent2);
    addKnob (spreadSlider,   spreadLabel,   "SPREAD",   schurUi::Palette::accent2);
    addKnob (emphasisSlider, emphasisLabel, "EMPHASIS", schurUi::Palette::accent2);

    rateAtt     = std::make_unique<Att> (audioProcessor.apvts, "rate", rateSlider);
    depthAtt    = std::make_unique<Att> (audioProcessor.apvts, "depth", depthSlider);
    widthAtt    = std::make_unique<Att> (audioProcessor.apvts, "width", widthSlider);
    mixAtt      = std::make_unique<Att> (audioProcessor.apvts, "mix", mixSlider);
    stagesAtt   = std::make_unique<Att> (audioProcessor.apvts, "sections", stagesSlider);
    toneAtt     = std::make_unique<Att> (audioProcessor.apvts, "color", toneSlider);
    spreadAtt   = std::make_unique<Att> (audioProcessor.apvts, "spread", spreadSlider);
    emphasisAtt = std::make_unique<Att> (audioProcessor.apvts, "emphasis", emphasisSlider);

    if (auto* sp = audioProcessor.apvts.getParameter ("sync"))
        syncWatch = std::make_unique<juce::ParameterAttachment> (
            *sp, [this] (float) { updateSyncUI(); }, nullptr);

    updateSyncUI();
}

void SchurPhaserAudioProcessorEditor::updateSyncUI()
{
    const bool synced = *audioProcessor.apvts.getRawParameterValue ("sync") > 0.5f;
    divBox.setVisible (synced);
    // When locked to tempo the Rate knob is inert — dim it to make that obvious.
    rateSlider.setEnabled (! synced);
    rateSlider.setAlpha (synced ? 0.35f : 1.0f);
    rateLabel.setText (synced ? juce::String::fromUTF8 ("RATE \xe2\x86\x92 SYNC") : juce::String ("RATE"),
                       juce::dontSendNotification);
    topBar.setReservedWidth (synced ? 64 : 0);
    divBox.setBounds (topBar.reservedBounds().translated (topBar.getX(), topBar.getY()));
    topBar.repaint();
}

void SchurPhaserAudioProcessorEditor::toggleSync()
{
    if (auto* p = audioProcessor.apvts.getParameter ("sync"))
    {
        const bool now = *audioProcessor.apvts.getRawParameterValue ("sync") > 0.5f;
        p->setValueNotifyingHost (now ? 0.0f : 1.0f);
    }
    updateSyncUI();
}

void SchurPhaserAudioProcessorEditor::loadProgram (int index)
{
    audioProcessor.setCurrentProgram (index);
    updateSyncUI();
    topBar.repaint();
}

void SchurPhaserAudioProcessorEditor::paint (juce::Graphics& g)
{
    auto bounds = getLocalBounds().toFloat();

    juce::ColourGradient bg (schurUi::Palette::bgTop, bounds.getCentreX(), (float) kQuilioH,
                             schurUi::Palette::bgBottom, bounds.getCentreX(), bounds.getBottom(), false);
    g.setGradientFill (bg);
    g.fillRect (0, kQuilioH, getWidth(), getHeight() - kQuilioH);
}

void SchurPhaserAudioProcessorEditor::layoutKnobRow (juce::Rectangle<int> area,
                                                     juce::Slider* sliders[],
                                                     juce::Label* labels[],
                                                     int count)
{
    if (count <= 0)
        return;

    const int cellW = area.getWidth() / count;
    for (int i = 0; i < count; ++i)
    {
        auto cell = area.withWidth (cellW).withX (area.getX() + i * cellW);
        labels[i]->setBounds (cell.removeFromTop (kLabelH));
        sliders[i]->setBounds (cell.reduced (8, 2));
    }
}

void SchurPhaserAudioProcessorEditor::resized()
{
    quilioBar.setBounds (0, 0, getWidth(), kQuilioH);
    topBar.setBounds (0, kQuilioH, getWidth(), kViewH);
    divBox.setBounds (topBar.reservedBounds().translated (topBar.getX(), topBar.getY()));

    auto area = getLocalBounds();
    area.removeFromTop (kChrome);
    area = area.reduced (kMargin);

    scope.setBounds (area.removeFromTop (kScopeH));

    area.removeFromTop (kGap);
    lattice.setBounds (area.removeFromTop (kLatticeH));

    area.removeFromTop (kGap + 6);

    const int rowH = (area.getHeight() - kGap) / 2;
    auto mainRow = area.removeFromTop (rowH);
    area.removeFromTop (kGap);
    auto charRow = area;

    juce::Slider* mainSliders[] = { &rateSlider, &depthSlider, &widthSlider, &mixSlider };
    juce::Label*  mainLabels[]  = { &rateLabel, &depthLabel, &widthLabel, &mixLabel };
    layoutKnobRow (mainRow, mainSliders, mainLabels, 4);

    juce::Slider* charSliders[] = { &stagesSlider, &toneSlider, &spreadSlider, &emphasisSlider };
    juce::Label*  charLabels[]  = { &stagesLabel, &toneLabel, &spreadLabel, &emphasisLabel };
    layoutKnobRow (charRow, charSliders, charLabels, 4);
}
