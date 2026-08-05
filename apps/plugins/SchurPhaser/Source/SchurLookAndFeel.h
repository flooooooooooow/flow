#pragma once

#include <JuceHeader.h>

namespace schurUi
{

struct Palette
{
    static inline const juce::Colour bgTop      { 0xff181b23 };
    static inline const juce::Colour bgBottom   { 0xff0b0d12 };
    static inline const juce::Colour panelEdge  { 0xff2a3040 };
    static inline const juce::Colour scopeBg    { 0xff0a0c11 };
    static inline const juce::Colour grid       { 0xff3a4256 };
    static inline const juce::Colour text       { 0xffeef1f6 };
    static inline const juce::Colour textDim    { 0xff8b93a8 };
    static inline const juce::Colour accent     { 0xff6ee7c8 };  // teal — primary
    static inline const juce::Colour accent2    { 0xffb28dff };  // violet — group delay / negative k
    static inline const juce::Colour accentDim  { 0xff9b8ec4 };
    static inline const juce::Colour track      { 0xff2e3548 };
};

class SchurLookAndFeel : public juce::LookAndFeel_V4
{
public:
    SchurLookAndFeel()
    {
        setColour (juce::Slider::rotarySliderFillColourId, Palette::accent);
        setColour (juce::Slider::rotarySliderOutlineColourId, Palette::track);
        setColour (juce::Slider::thumbColourId, Palette::accent);
        setColour (juce::Slider::textBoxTextColourId, Palette::text);
        setColour (juce::Slider::textBoxBackgroundColourId, juce::Colours::transparentBlack);
        setColour (juce::Slider::textBoxOutlineColourId, juce::Colours::transparentBlack);
        setColour (juce::Label::textColourId, Palette::textDim);
    }

    void drawRotarySlider (juce::Graphics& g,
                           int x, int y, int width, int height,
                           float sliderPosProportional,
                           float rotaryStartAngle,
                           float rotaryEndAngle,
                           juce::Slider& slider) override
    {
        const auto accent = slider.findColour (juce::Slider::rotarySliderFillColourId);
        const auto bounds = juce::Rectangle<float> ((float) x, (float) y, (float) width, (float) height)
                            .reduced (5.0f);
        const float radius = juce::jmin (bounds.getWidth(), bounds.getHeight()) * 0.5f;
        const float cx = bounds.getCentreX();
        const float cy = bounds.getCentreY();
        const float angle = rotaryStartAngle + sliderPosProportional * (rotaryEndAngle - rotaryStartAngle);
        const float bodyR = radius - 4.0f;

        // recessed knob body
        juce::ColourGradient body (Palette::bgTop.brighter (0.12f), cx, cy - bodyR,
                                   Palette::bgBottom, cx, cy + bodyR, false);
        g.setGradientFill (body);
        g.fillEllipse (cx - bodyR, cy - bodyR, bodyR * 2.0f, bodyR * 2.0f);
        g.setColour (Palette::panelEdge.withAlpha (0.8f));
        g.drawEllipse (cx - bodyR, cy - bodyR, bodyR * 2.0f, bodyR * 2.0f, 1.0f);

        // background track
        juce::Path track;
        track.addCentredArc (cx, cy, radius, radius, 0.0f, rotaryStartAngle, rotaryEndAngle, true);
        g.setColour (Palette::track);
        g.strokePath (track, juce::PathStrokeType (3.0f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

        // value arc, with a soft outer glow
        juce::Path valueArc;
        valueArc.addCentredArc (cx, cy, radius, radius, 0.0f, rotaryStartAngle, angle, true);
        g.setColour (accent.withAlpha (0.25f));
        g.strokePath (valueArc, juce::PathStrokeType (6.0f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
        g.setColour (accent);
        g.strokePath (valueArc, juce::PathStrokeType (3.0f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

        // pointer tick from centre outward
        const float a = angle - juce::MathConstants<float>::halfPi;
        const float r0 = bodyR * 0.32f;
        const float r1 = bodyR * 0.86f;
        juce::Line<float> tick (cx + r0 * std::cos (a), cy + r0 * std::sin (a),
                                cx + r1 * std::cos (a), cy + r1 * std::sin (a));
        g.setColour (accent);
        g.drawLine (tick, 2.2f);
        g.fillEllipse (tick.getEndX() - 2.3f, tick.getEndY() - 2.3f, 4.6f, 4.6f);
    }

    juce::Font getLabelFont (juce::Label&) override
    {
        return juce::Font (juce::FontOptions (11.0f));
    }
};

inline void styleKnob (juce::Slider& s, juce::Colour accent, const juce::String& suffix = {})
{
    s.setSliderStyle (juce::Slider::RotaryHorizontalVerticalDrag);
    s.setTextBoxStyle (juce::Slider::TextBoxBelow, false, 52, 14);
    s.setTextBoxIsEditable (false);
    s.setColour (juce::Slider::rotarySliderFillColourId, accent);
    if (suffix.isNotEmpty())
        s.setTextValueSuffix (suffix);
}

inline void styleLabel (juce::Label& l, const juce::String& text)
{
    l.setText (text, juce::dontSendNotification);
    l.setJustificationType (juce::Justification::centred);
    l.setColour (juce::Label::textColourId, Palette::textDim);
    l.setFont (juce::Font (juce::FontOptions (10.5f)));
}

} // namespace schurUi