#pragma once

#include <JuceHeader.h>
#include <atomic>
#include "SchurLookAndFeel.h"

namespace schurUi
{

//==============================================================================
/** Horizontal L/R phase-correlation meter, -1 (out of phase / mono-cancelling)
    through 0 (decorrelated) to +1 (mono-compatible). The essential readout for a
    phase-alignment tool: watch it climb toward +1 as you dial the alignment. */
class CorrelationMeter : public juce::Component,
                         private juce::Timer
{
public:
    explicit CorrelationMeter (const std::atomic<float>& src) : source (src)
    {
        startTimerHz (45);
    }
    ~CorrelationMeter() override { stopTimer(); }

    void paint (juce::Graphics& g) override
    {
        using P = Palette;
        const auto bounds = getLocalBounds().toFloat();
        g.setColour (P::scopeBg);
        g.fillRoundedRectangle (bounds, 10.0f);
        g.setColour (P::panelEdge.withAlpha (0.6f));
        g.drawRoundedRectangle (bounds.reduced (0.5f), 10.0f, 1.0f);

        auto area = bounds.reduced (14.0f, 10.0f);

        g.setFont (juce::Font (juce::FontOptions (8.5f).withStyle ("Bold")));
        g.setColour (P::textDim.withAlpha (0.7f));
        g.drawText ("CORRELATION", (int) area.getX(), (int) bounds.getY() + 4, 140, 11,
                    juce::Justification::centredLeft);
        g.setColour (value < 0.0f ? juce::Colour (0xffe8705a) : P::accent);
        g.drawText (juce::String (value, 2), (int) area.getRight() - 60, (int) bounds.getY() + 4, 60, 11,
                    juce::Justification::centredRight);

        auto track = area.withTrimmedTop (14.0f).withHeight (14.0f);
        // zoned backdrop: red (left / anti-phase) -> neutral -> teal (right / mono-safe)
        juce::ColourGradient grad (juce::Colour (0xffe8705a).withAlpha (0.30f), track.getX(), 0.0f,
                                   P::accent.withAlpha (0.30f), track.getRight(), 0.0f, false);
        grad.addColour (0.5, P::grid.withAlpha (0.25f));
        g.setGradientFill (grad);
        g.fillRoundedRectangle (track, 3.0f);
        g.setColour (P::panelEdge.withAlpha (0.7f));
        g.drawRoundedRectangle (track, 3.0f, 1.0f);

        // ticks at -1, 0, +1
        auto xFor = [&] (float v) { return track.getX() + (v * 0.5f + 0.5f) * track.getWidth(); };
        g.setColour (P::grid.withAlpha (0.5f));
        g.drawVerticalLine ((int) xFor (0.0f), track.getY(), track.getBottom());
        g.setColour (P::textDim.withAlpha (0.6f));
        g.setFont (juce::Font (juce::FontOptions (8.0f)));
        g.drawText ("-1", (int) track.getX() - 2, (int) track.getBottom() + 1, 20, 10, juce::Justification::centredLeft);
        g.drawText ("0",  (int) xFor (0.0f) - 10, (int) track.getBottom() + 1, 20, 10, juce::Justification::centred);
        g.drawText ("+1", (int) track.getRight() - 18, (int) track.getBottom() + 1, 20, 10, juce::Justification::centredRight);

        // indicator: bar from centre to the current value, plus a bright tab
        const float x0 = xFor (0.0f);
        const float x  = xFor (juce::jlimit (-1.0f, 1.0f, value));
        const juce::Colour c = value < 0.0f ? juce::Colour (0xffe8705a) : P::accent;
        juce::Rectangle<float> bar (juce::jmin (x0, x), track.getY(), std::abs (x - x0), track.getHeight());
        g.setColour (c.withAlpha (0.35f));
        g.fillRoundedRectangle (bar, 2.0f);
        g.setColour (c);
        g.fillRoundedRectangle (x - 2.0f, track.getY() - 2.0f, 4.0f, track.getHeight() + 4.0f, 2.0f);
    }

private:
    void timerCallback() override
    {
        value += 0.3f * (source.load (std::memory_order_relaxed) - value);
        repaint();
    }

    const std::atomic<float>& source;
    float value = 1.0f;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (CorrelationMeter)
};

} // namespace schurUi
