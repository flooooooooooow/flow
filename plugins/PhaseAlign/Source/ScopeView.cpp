#include "ScopeView.h"

namespace
{
constexpr float kFreqMin = 20.0f;
inline float lerp (float a, float b, float t) noexcept { return a + (b - a) * t; }
} // namespace

ScopeView::ScopeView (PhaseAlignAudioProcessor& proc) : processor (proc)
{
    setOpaque (false);
    startTimerHz (60);
}

ScopeView::~ScopeView() { stopTimer(); }

void ScopeView::setMode (Mode m) { if (mode != m) { mode = m; repaint(); } }

void ScopeView::resized() { plot = getLocalBounds().toFloat().reduced (14.0f, 12.0f); }

float ScopeView::freqToX (float hz) const noexcept
{
    const float fMax = (float) (sampleRate * 0.49);
    const float lo = std::log10 (kFreqMin), hi = std::log10 (fMax);
    const float t = (std::log10 (juce::jlimit (kFreqMin, fMax, hz)) - lo) / (hi - lo);
    return plot.getX() + t * plot.getWidth();
}

void ScopeView::timerCallback()
{
    const int order = juce::jlimit (1, schur::kMaxOrder,
                                    processor.snapOrder.load (std::memory_order_relaxed));
    sampleRate   = processor.snapSampleRate.load (std::memory_order_relaxed);
    pivotHz      = processor.snapFreq.load (std::memory_order_relaxed);
    extraDelayMs = processor.snapDelayMs.load (std::memory_order_relaxed);
    inverted     = processor.snapInvert.load (std::memory_order_relaxed);

    float k[schur::kMaxOrder] {};
    for (int i = 0; i < order; ++i)
        k[i] = processor.designK[(size_t) i].load (std::memory_order_relaxed);

    schur::computeResponse (k, order, 1.0f, sampleRate, kNumPoints,
                            freqHz.data(), phaseTgt.data(), delayTgt.data(), nullptr);

    // add the constant delay-line latency to the displayed group delay
    for (int i = 0; i < kNumPoints; ++i)
        delayTgt[(size_t) i] += extraDelayMs;

    float peak = 1.0f;
    for (int i = 0; i < kNumPoints; ++i) peak = juce::jmax (peak, delayTgt[(size_t) i]);
    delayScaleMs = lerp (delayScaleMs, peak * 1.15f, 0.08f);

    const float s = 0.4f;
    for (int i = 0; i < kNumPoints; ++i)
    {
        phaseCur[(size_t) i] = lerp (phaseCur[(size_t) i], phaseTgt[(size_t) i], s);
        delayCur[(size_t) i] = lerp (delayCur[(size_t) i], delayTgt[(size_t) i], s);
    }

    const int got = processor.tap.pop (drainL.data(), drainR.data(), (int) drainL.size());
    if (mode == Mode::Spectrum)
    {
        if (got > 0)
        {
            for (int i = 0; i < got; ++i)
                drainL[(size_t) i] = 0.5f * (drainL[(size_t) i] + drainR[(size_t) i]);
            spectrum.pushSamples (drainL.data(), got);
        }
        spectrum.render();
    }
    repaint();
}

void ScopeView::paint (juce::Graphics& g)
{
    using P = schurUi::Palette;
    const auto bounds = getLocalBounds().toFloat();

    g.setColour (P::scopeBg);
    g.fillRoundedRectangle (bounds, 10.0f);
    g.setColour (P::panelEdge.withAlpha (0.6f));
    g.drawRoundedRectangle (bounds.reduced (0.5f), 10.0f, 1.0f);

    juce::Graphics::ScopedSaveState clip (g);
    juce::Path panelClip; panelClip.addRoundedRectangle (bounds.reduced (1.0f), 9.0f);
    g.reduceClipRegion (panelClip);

    const bool phaseMode    = (mode == Mode::Phase);
    const bool spectrumMode = (mode == Mode::Spectrum);

    // ---- frequency grid ----
    const float decades[] = { 100.0f, 1000.0f, 10000.0f };
    for (int d = 0; d < 3; ++d)
        for (int m = 1; m <= 9; ++m)
        {
            const float f = decades[d] * 0.1f * (float) m;
            if (f < kFreqMin || f > (float) (sampleRate * 0.49)) continue;
            g.setColour (P::grid.withAlpha (m == 1 ? 0.5f : 0.16f));
            g.drawVerticalLine ((int) std::round (freqToX (f)), plot.getY(), plot.getBottom());
        }

    g.setFont (juce::Font (juce::FontOptions (9.5f)));
    g.setColour (P::textDim.withAlpha (0.7f));
    auto flabel = [&] (float f, const char* t)
    { g.drawText (t, (int) freqToX (f) - 16, (int) plot.getBottom() - 12, 32, 12, juce::Justification::centred); };
    flabel (100.0f, "100"); flabel (1000.0f, "1k"); flabel (10000.0f, "10k");

    // ---- 0-degree reference (the "aligned" target) ----
    if (phaseMode)
    {
        const float cy = plot.getCentreY();
        g.setColour (P::text.withAlpha (0.30f));
        const float dashes[] = { 4.0f, 4.0f };
        g.drawDashedLine ({ { plot.getX(), cy }, { plot.getRight(), cy } }, dashes, 2, 1.0f);
        g.setColour (P::textDim.withAlpha (0.55f));
        g.drawText (juce::String::fromUTF8 ("0\xc2\xb0"), (int) plot.getRight() - 26, (int) cy - 12, 22, 12,
                    juce::Justification::centredRight);
        g.setColour (P::grid.withAlpha (0.14f));
        g.drawHorizontalLine ((int) lerp (plot.getY(), cy, 0.5f), plot.getX(), plot.getRight());
        g.drawHorizontalLine ((int) lerp (plot.getBottom(), cy, 0.5f), plot.getX(), plot.getRight());
    }

    // ---- pivot-frequency marker ----
    const float px = freqToX (pivotHz);
    g.setColour (P::accent.withAlpha (0.5f));
    const float pdash[] = { 3.0f, 3.0f };
    g.drawDashedLine ({ { px, plot.getY() }, { px, plot.getBottom() } }, pdash, 2, 1.0f);

    // ---- primary curve ----
    const juce::Colour lineCol = phaseMode ? P::accent : (spectrumMode ? P::accent : P::accent2);
    auto specY = [&] (float db)
    {
        const float n = juce::jlimit (0.0f, 1.0f, (db - (-96.0f)) / (6.0f - (-96.0f)));
        return plot.getBottom() - n * (plot.getHeight() * 0.96f);
    };
    auto yOf = [&] (int i) -> float
    {
        if (phaseMode)
        {
            const float p = juce::jlimit (-180.0f, 180.0f, phaseCur[(size_t) i]);
            return plot.getCentreY() - (p / 180.0f) * (plot.getHeight() * 0.46f);
        }
        if (spectrumMode)
            return specY (spectrum.dbAtFreq (freqHz[(size_t) i], sampleRate));
        const float n = juce::jlimit (0.0f, 1.0f, delayCur[(size_t) i] / juce::jmax (0.001f, delayScaleMs));
        return plot.getBottom() - n * (plot.getHeight() * 0.92f);
    };

    if (spectrumMode)
    {
        juce::Path sp;
        sp.startNewSubPath (plot.getX(), plot.getBottom());
        for (int i = 0; i < kNumPoints; ++i)
            sp.lineTo (freqToX (freqHz[(size_t) i]), yOf (i));
        sp.lineTo (plot.getRight(), plot.getBottom());
        sp.closeSubPath();
        juce::ColourGradient fill (P::accent.withAlpha (0.30f), 0.0f, plot.getY(),
                                   P::accent.withAlpha (0.02f), 0.0f, plot.getBottom(), false);
        g.setGradientFill (fill);
        g.fillPath (sp);

        juce::Path edge;
        for (int i = 0; i < kNumPoints; ++i)
        {
            const float x = freqToX (freqHz[(size_t) i]);
            if (i == 0) edge.startNewSubPath (x, yOf (i)); else edge.lineTo (x, yOf (i));
        }
        g.setColour (P::accent.withAlpha (0.20f));
        g.strokePath (edge, juce::PathStrokeType (3.0f, juce::PathStrokeType::curved));
        g.setColour (P::accent);
        g.strokePath (edge, juce::PathStrokeType (1.3f, juce::PathStrokeType::curved));
    }
    else
    {
        juce::Path curve;
        for (int i = 0; i < kNumPoints; ++i)
        {
            const float x = freqToX (freqHz[(size_t) i]);
            const float y = yOf (i);
            const bool jump = phaseMode && i > 0
                              && std::abs (phaseCur[(size_t) i] - phaseCur[(size_t) i - 1]) > 200.0f;
            if (i == 0 || jump) curve.startNewSubPath (x, y);
            else                curve.lineTo (x, y);
        }
        g.setColour (lineCol.withAlpha (0.18f));
        g.strokePath (curve, juce::PathStrokeType (4.0f, juce::PathStrokeType::curved));
        g.setColour (lineCol);
        g.strokePath (curve, juce::PathStrokeType (1.7f, juce::PathStrokeType::curved));
    }

    // ---- hover scrub ----
    if (hoverX >= plot.getX() && hoverX <= plot.getRight())
    {
        const float t = (hoverX - plot.getX()) / plot.getWidth();
        const int idx = juce::jlimit (0, kNumPoints - 1, (int) std::round (t * (kNumPoints - 1)));
        const float x = freqToX (freqHz[(size_t) idx]);
        g.setColour (P::text.withAlpha (0.22f));
        g.drawVerticalLine ((int) x, plot.getY(), plot.getBottom());
        g.setColour (lineCol);
        g.fillEllipse (x - 3.0f, yOf (idx) - 3.0f, 6.0f, 6.0f);

        const float f = freqHz[(size_t) idx];
        juce::String txt;
        txt << (f >= 1000.0f ? juce::String (f / 1000.0f, 2) + " kHz" : juce::String ((int) f) + " Hz");
        txt << "   ";
        if (phaseMode)         txt << (juce::String (phaseCur[(size_t) idx], 0) + juce::String::fromUTF8 ("\xc2\xb0"));
        else if (spectrumMode) txt << juce::String (spectrum.dbAtFreq (f, sampleRate), 1) << " dB";
        else                   txt << juce::String (delayCur[(size_t) idx], 2) << " ms";

        g.setFont (juce::Font (juce::FontOptions (10.0f)));
        const int tw = juce::jmax (130, (int) (txt.length() * 6.2f) + 16);
        const float bx = juce::jlimit (plot.getX(), plot.getRight() - tw, x - tw * 0.5f);
        juce::Rectangle<float> box (bx, plot.getY() + 4.0f, (float) tw, 18.0f);
        g.setColour (P::panelEdge.withAlpha (0.92f));
        g.fillRoundedRectangle (box, 4.0f);
        g.setColour (P::text);
        g.drawText (txt, box, juce::Justification::centred);
    }

    // ---- corner tags ----
    g.setFont (juce::Font (juce::FontOptions (9.5f).withStyle ("Bold")));
    g.setColour (lineCol.withAlpha (0.85f));
    g.drawText (phaseMode    ? juce::String::fromUTF8 ("ALL-PASS PHASE  \xc2\xb0")
              : spectrumMode ? juce::String ("SPECTRUM  dB")
                             : juce::String ("GROUP DELAY  ms"),
                (int) plot.getX() + 4, (int) plot.getY() + 2, 200, 12, juce::Justification::centredLeft);

    // total corrective latency at the pivot (delay line + all-pass GD)
    float gdAtPivot = 0.0f;
    {
        int best = 0; float bestd = 1e9f;
        for (int i = 0; i < kNumPoints; ++i)
        { const float dd = std::abs (freqHz[(size_t) i] - pivotHz); if (dd < bestd) { bestd = dd; best = i; } }
        gdAtPivot = delayCur[(size_t) best]; // already includes extraDelayMs
    }
    juce::String latency = juce::String::fromUTF8 ("\xce\x94t  ") + juce::String (gdAtPivot, 2) + " ms";
    if (inverted) latency << juce::String::fromUTF8 ("    \xc3\xb8 INV");
    g.setColour (P::textDim);
    g.drawText (latency, (int) plot.getRight() - 184, (int) plot.getY() + 2, 180, 12,
                juce::Justification::centredRight);
}

void ScopeView::mouseMove (const juce::MouseEvent& e) { hoverX = (float) e.position.x; repaint(); }
void ScopeView::mouseExit (const juce::MouseEvent&)   { hoverX = -1.0f; repaint(); }
