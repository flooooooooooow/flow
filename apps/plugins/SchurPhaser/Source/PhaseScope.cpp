#include "PhaseScope.h"

namespace schurUi
{

namespace
{
constexpr float kFreqMin = 20.0f;

inline float lerp (float a, float b, float t) noexcept { return a + (b - a) * t; }

// Draw a log-frequency grid line + optional label.
void gridLine (juce::Graphics& g, juce::Rectangle<float> plot,
               float x, juce::Colour c) noexcept
{
    g.setColour (c);
    g.drawVerticalLine ((int) std::round (x), plot.getY(), plot.getBottom());
}
} // namespace

//==============================================================================
PhaseScope::PhaseScope (SchurPhaserAudioProcessor& proc)
    : processor (proc)
{
    setOpaque (false);
    startTimerHz (60);
}

PhaseScope::~PhaseScope() { stopTimer(); }

void PhaseScope::setMode (Mode m)
{
    if (mode != m) { mode = m; repaint(); }
}

void PhaseScope::resized()
{
    plot = getLocalBounds().toFloat().reduced (14.0f, 12.0f);
}

float PhaseScope::freqToX (float hz) const noexcept
{
    const float fMax = (float) (sampleRate * 0.49);
    const float lo = std::log10 (kFreqMin);
    const float hi = std::log10 (fMax);
    const float t = (std::log10 (juce::jlimit (kFreqMin, fMax, hz)) - lo) / (hi - lo);
    return plot.getX() + t * plot.getWidth();
}

float PhaseScope::xToFreq (float x) const noexcept
{
    const float fMax = (float) (sampleRate * 0.49);
    const float lo = std::log10 (kFreqMin);
    const float hi = std::log10 (fMax);
    const float t = juce::jlimit (0.0f, 1.0f, (x - plot.getX()) / plot.getWidth());
    return std::pow (10.0f, lo + t * (hi - lo));
}

//==============================================================================
void PhaseScope::timerCallback()
{
    const int order = juce::jlimit (1, schur::kMaxOrder,
                                    processor.snapOrder.load (std::memory_order_relaxed));
    const float mix   = processor.snapMix.load (std::memory_order_relaxed);
    const float depth = processor.snapDepth.load (std::memory_order_relaxed);
    sampleRate = processor.snapSampleRate.load (std::memory_order_relaxed);
    const bool active = processor.snapActive.load (std::memory_order_relaxed);

    idlePhase += 0.6f / 60.0f * juce::MathConstants<float>::twoPi; // ~0.6 Hz idle sweep

    float k[schur::kMaxOrder] {};
    for (int i = 0; i < order; ++i)
    {
        if (active)
        {
            k[i] = processor.liveK[(size_t) i].load (std::memory_order_relaxed);
        }
        else
        {
            const float base = processor.baseK[(size_t) i].load (std::memory_order_relaxed);
            k[i] = juce::jlimit (-0.999f, 0.999f,
                                 base + depth * std::sin (idlePhase + (float) i * 0.31f));
        }
    }

    schur::computeResponse (k, order, mix, sampleRate, kNumPoints,
                            freqHz.data(), phaseTgt.data(), delayTgt.data(), notchTgt.data());

    // Autoscale group delay to a smoothed peak so the curve always fills the view.
    float peak = 1.0f;
    for (int i = 0; i < kNumPoints; ++i)
        peak = juce::jmax (peak, delayTgt[(size_t) i]);
    delayScaleMs = lerp (delayScaleMs, peak * 1.12f, 0.08f);

    // Smooth every curve toward its target for fluid, non-jittery motion.
    const float s = 0.35f;
    for (int i = 0; i < kNumPoints; ++i)
    {
        phaseCur[(size_t) i] = lerp (phaseCur[(size_t) i], phaseTgt[(size_t) i], s);
        delayCur[(size_t) i] = lerp (delayCur[(size_t) i], delayTgt[(size_t) i], s);
        notchCur[(size_t) i] = lerp (notchCur[(size_t) i], notchTgt[(size_t) i], s);
    }

    // Drain the audio tap; run the FFT only when the spectrum view is showing.
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

//==============================================================================
void PhaseScope::paint (juce::Graphics& g)
{
    const auto bounds = getLocalBounds().toFloat();

    // panel
    g.setColour (Palette::scopeBg);
    g.fillRoundedRectangle (bounds, 10.0f);
    g.setColour (Palette::panelEdge.withAlpha (0.6f));
    g.drawRoundedRectangle (bounds.reduced (0.5f), 10.0f, 1.0f);

    juce::Graphics::ScopedSaveState clip (g);
    juce::Path panelClip;
    panelClip.addRoundedRectangle (bounds.reduced (1.0f), 9.0f);
    g.reduceClipRegion (panelClip);

    // ---- frequency grid ----
    const float decades[] = { 100.0f, 1000.0f, 10000.0f };
    for (int d = 0; d < 3; ++d)
    {
        for (int m = 1; m <= 9; ++m)
        {
            const float f = decades[d] * 0.1f * (float) m; // 10..90, 100..900, ...
            if (f < kFreqMin || f > (float) (sampleRate * 0.49)) continue;
            const bool major = (m == 1);
            gridLine (g, plot, freqToX (f),
                      Palette::grid.withAlpha (major ? 0.5f : 0.16f));
        }
    }

    // horizontal reference lines
    g.setColour (Palette::grid.withAlpha (0.28f));
    if (mode == Mode::Phase)
    {
        const float cy = plot.getCentreY();
        g.drawHorizontalLine ((int) cy, plot.getX(), plot.getRight());
        g.setColour (Palette::grid.withAlpha (0.12f));
        g.drawHorizontalLine ((int) lerp (plot.getY(), cy, 0.5f), plot.getX(), plot.getRight());
        g.drawHorizontalLine ((int) lerp (plot.getBottom(), cy, 0.5f), plot.getX(), plot.getRight());
    }

    // frequency labels
    g.setFont (juce::Font (juce::FontOptions (9.5f)));
    g.setColour (Palette::textDim.withAlpha (0.7f));
    auto label = [&] (float f, const char* t)
    {
        g.drawText (t, (int) freqToX (f) - 16, (int) plot.getBottom() - 12, 32, 12,
                    juce::Justification::centred);
    };
    label (100.0f, "100"); label (1000.0f, "1k"); label (10000.0f, "10k");

    const bool phaseMode    = (mode == Mode::Phase);
    const bool spectrumMode = (mode == Mode::Spectrum);
    const juce::Colour lineCol = (mode == Mode::GroupDelay) ? Palette::accent2 : Palette::accent;

    // dB -> y mappings for the two different scales in play
    auto notchY = [&] (float db)
    {
        const float n = juce::jlimit (0.0f, 1.0f, (db - (-30.0f)) / (3.0f - (-30.0f)));
        return plot.getBottom() - n * plot.getHeight();
    };
    auto specY = [&] (float db)
    {
        const float n = juce::jlimit (0.0f, 1.0f, (db - (-96.0f)) / (6.0f - (-96.0f)));
        return plot.getBottom() - n * (plot.getHeight() * 0.96f);
    };
    auto valueY = [&] (int i) -> float
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
        // ---- live FFT spectrum, filled ----
        juce::Path sp;
        sp.startNewSubPath (plot.getX(), plot.getBottom());
        for (int i = 0; i < kNumPoints; ++i)
            sp.lineTo (freqToX (freqHz[(size_t) i]), valueY (i));
        sp.lineTo (plot.getRight(), plot.getBottom());
        sp.closeSubPath();
        juce::ColourGradient fill (Palette::accent.withAlpha (0.30f), 0.0f, plot.getY(),
                                   Palette::accent.withAlpha (0.02f), 0.0f, plot.getBottom(), false);
        g.setGradientFill (fill);
        g.fillPath (sp);

        juce::Path edge;
        for (int i = 0; i < kNumPoints; ++i)
        {
            const float x = freqToX (freqHz[(size_t) i]);
            if (i == 0) edge.startNewSubPath (x, valueY (i)); else edge.lineTo (x, valueY (i));
        }
        g.setColour (Palette::accent.withAlpha (0.20f));
        g.strokePath (edge, juce::PathStrokeType (3.0f, juce::PathStrokeType::curved));
        g.setColour (Palette::accent);
        g.strokePath (edge, juce::PathStrokeType (1.3f, juce::PathStrokeType::curved));

        // ---- the phaser's filter shape, overlaid so notches read against the audio ----
        juce::Path shape;
        for (int i = 0; i < kNumPoints; ++i)
        {
            const float x = freqToX (freqHz[(size_t) i]);
            const float y = specY (notchCur[(size_t) i]);   // notch dB on the spectrum axis
            if (i == 0) shape.startNewSubPath (x, y); else shape.lineTo (x, y);
        }
        g.setColour (Palette::accent2.withAlpha (0.65f));
        g.strokePath (shape, juce::PathStrokeType (1.2f, juce::PathStrokeType::curved));
    }
    else
    {
        // ---- notch comb backdrop ----
        juce::Path notch;
        notch.startNewSubPath (plot.getX(), plot.getBottom());
        for (int i = 0; i < kNumPoints; ++i)
            notch.lineTo (freqToX (freqHz[(size_t) i]), notchY (notchCur[(size_t) i]));
        notch.lineTo (plot.getRight(), plot.getBottom());
        notch.closeSubPath();
        juce::ColourGradient fill (Palette::accent.withAlpha (0.22f), 0.0f, plot.getY(),
                                   Palette::accent.withAlpha (0.02f), 0.0f, plot.getBottom(), false);
        g.setGradientFill (fill);
        g.fillPath (notch);

        juce::Path notchEdge;
        for (int i = 0; i < kNumPoints; ++i)
        {
            const float x = freqToX (freqHz[(size_t) i]);
            if (i == 0) notchEdge.startNewSubPath (x, notchY (notchCur[(size_t) i]));
            else        notchEdge.lineTo (x, notchY (notchCur[(size_t) i]));
        }
        g.setColour (Palette::accent.withAlpha (0.55f));
        g.strokePath (notchEdge, juce::PathStrokeType (1.0f));

        // ---- primary curve: phase or group delay ----
        juce::Path curve;
        for (int i = 0; i < kNumPoints; ++i)
        {
            const float x = freqToX (freqHz[(size_t) i]);
            const bool jump = phaseMode && i > 0
                              && std::abs (phaseCur[(size_t) i] - phaseCur[(size_t) i - 1]) > 200.0f;
            if (i == 0 || jump) curve.startNewSubPath (x, valueY (i));
            else                curve.lineTo (x, valueY (i));
        }
        g.setColour (lineCol.withAlpha (0.18f));
        g.strokePath (curve, juce::PathStrokeType (4.0f, juce::PathStrokeType::curved));
        g.setColour (lineCol);
        g.strokePath (curve, juce::PathStrokeType (1.6f, juce::PathStrokeType::curved));
    }

    // ---- hover scrub readout ----
    if (hoverX >= plot.getX() && hoverX <= plot.getRight())
    {
        const float t = (hoverX - plot.getX()) / plot.getWidth();
        const int idx = juce::jlimit (0, kNumPoints - 1, (int) std::round (t * (kNumPoints - 1)));
        const float x = freqToX (freqHz[(size_t) idx]);

        g.setColour (Palette::text.withAlpha (0.25f));
        g.drawVerticalLine ((int) x, plot.getY(), plot.getBottom());

        const float py = valueY (idx);
        g.setColour (lineCol);
        g.fillEllipse (x - 3.0f, py - 3.0f, 6.0f, 6.0f);
        g.setColour (Palette::scopeBg);
        g.fillEllipse (x - 1.5f, py - 1.5f, 3.0f, 3.0f);

        juce::String txt;
        const float f = freqHz[(size_t) idx];
        txt << (f >= 1000.0f ? juce::String (f / 1000.0f, 2) + " kHz"
                             : juce::String ((int) f) + " Hz");
        txt << "   ";
        if (phaseMode)         txt << (juce::String (phaseCur[(size_t) idx], 0) + juce::String::fromUTF8 ("\xc2\xb0"));
        else if (spectrumMode) txt << juce::String (spectrum.dbAtFreq (f, sampleRate), 1) << " dB";
        else                   txt << juce::String (delayCur[(size_t) idx], 2) << " ms";

        g.setFont (juce::Font (juce::FontOptions (10.0f)));
        const int tw = juce::jmax (140, (int) (txt.length() * 6.2f) + 16);
        float bx = juce::jlimit (plot.getX(), plot.getRight() - tw, x - tw * 0.5f);
        juce::Rectangle<float> box (bx, plot.getY() + 4.0f, (float) tw, 18.0f);
        g.setColour (Palette::panelEdge.withAlpha (0.92f));
        g.fillRoundedRectangle (box, 4.0f);
        g.setColour (Palette::text);
        g.drawText (txt, box, juce::Justification::centred);
    }

    // ---- corner tag ----
    g.setFont (juce::Font (juce::FontOptions (9.5f).withStyle ("Bold")));
    g.setColour (lineCol.withAlpha (0.85f));
    juce::String tag = phaseMode    ? juce::String::fromUTF8 ("PHASE  \xc2\xb0")
                     : spectrumMode ? juce::String ("SPECTRUM  dB")
                                    : juce::String ("GROUP DELAY  ms");
    g.drawText (tag, (int) plot.getX() + 4, (int) plot.getY() + 2, 160, 12,
                juce::Justification::centredLeft);
}

void PhaseScope::mouseMove (const juce::MouseEvent& e)
{
    hoverX = (float) e.position.x;
    repaint();
}

void PhaseScope::mouseExit (const juce::MouseEvent&)
{
    hoverX = -1.0f;
    repaint();
}

//==============================================================================
ReflectionLattice::ReflectionLattice (SchurPhaserAudioProcessor& proc)
    : processor (proc)
{
    startTimerHz (60);
}

ReflectionLattice::~ReflectionLattice() { stopTimer(); }

void ReflectionLattice::timerCallback()
{
    order = juce::jlimit (1, schur::kMaxOrder,
                          processor.snapOrder.load (std::memory_order_relaxed));
    const bool active = processor.snapActive.load (std::memory_order_relaxed);
    const float depth = processor.snapDepth.load (std::memory_order_relaxed);
    idlePhase += 0.6f / 60.0f * juce::MathConstants<float>::twoPi;

    for (int i = 0; i < order; ++i)
    {
        const float base = processor.baseK[(size_t) i].load (std::memory_order_relaxed);
        const float live = active
            ? processor.liveK[(size_t) i].load (std::memory_order_relaxed)
            : juce::jlimit (-0.999f, 0.999f, base + depth * std::sin (idlePhase + (float) i * 0.31f));
        baseCur[(size_t) i] = lerp (baseCur[(size_t) i], base, 0.3f);
        liveCur[(size_t) i] = lerp (liveCur[(size_t) i], live, 0.4f);
    }
    repaint();
}

void ReflectionLattice::paint (juce::Graphics& g)
{
    const auto bounds = getLocalBounds().toFloat();
    g.setColour (Palette::scopeBg);
    g.fillRoundedRectangle (bounds, 10.0f);
    g.setColour (Palette::panelEdge.withAlpha (0.6f));
    g.drawRoundedRectangle (bounds.reduced (0.5f), 10.0f, 1.0f);

    auto area = bounds.reduced (12.0f, 10.0f);
    const float cy = area.getCentreY();

    g.setColour (Palette::grid.withAlpha (0.35f));
    g.drawHorizontalLine ((int) cy, area.getX(), area.getRight());

    g.setFont (juce::Font (juce::FontOptions (8.5f).withStyle ("Bold")));
    g.setColour (Palette::textDim.withAlpha (0.7f));
    g.drawText ("REFLECTION LATTICE  k", (int) area.getX(), (int) bounds.getY() + 3,
                180, 11, juce::Justification::centredLeft);

    if (order <= 0) return;

    const float slot = area.getWidth() / (float) order;
    const float barW = juce::jmin (slot * 0.5f, 14.0f);
    const float halfH = area.getHeight() * 0.42f;

    for (int i = 0; i < order; ++i)
    {
        const float cx = area.getX() + (i + 0.5f) * slot;
        const float live = juce::jlimit (-1.0f, 1.0f, liveCur[(size_t) i]);
        const float base = juce::jlimit (-1.0f, 1.0f, baseCur[(size_t) i]);

        // colour by sign: teal for positive reflection, violet for negative
        const juce::Colour c = live >= 0.0f ? Palette::accent : Palette::accent2;

        // faint design-value tick
        const float baseY = cy - base * halfH;
        g.setColour (Palette::textDim.withAlpha (0.4f));
        g.fillRect (cx - barW * 0.5f - 2.0f, baseY - 0.5f, barW + 4.0f, 1.0f);

        // live bar
        const float liveY = cy - live * halfH;
        juce::Rectangle<float> bar (cx - barW * 0.5f,
                                    juce::jmin (cy, liveY),
                                    barW,
                                    std::abs (cy - liveY));
        g.setColour (c.withAlpha (0.22f));
        g.fillRoundedRectangle (bar.expanded (1.5f, 0.0f), 2.0f);
        g.setColour (c.withAlpha (0.9f));
        g.fillRoundedRectangle (bar, 2.0f);

        // cap dot
        g.setColour (c);
        g.fillEllipse (cx - 2.5f, liveY - 2.5f, 5.0f, 5.0f);
    }
}

} // namespace schurUi
