#include "PluginProcessor.h"
#include "PluginEditor.h"

namespace IDs
{
static constexpr auto sections = "sections";
static constexpr auto color    = "color";
static constexpr auto spread   = "spread";
static constexpr auto rate     = "rate";
static constexpr auto depth    = "depth";
static constexpr auto width    = "width";
static constexpr auto mix      = "mix";
static constexpr auto emphasis = "emphasis";
static constexpr auto sync     = "sync";
static constexpr auto syncdiv  = "syncdiv";
} // namespace IDs

namespace
{
// Tempo divisions, slow -> fast. Value = LFO cycles per beat.
const juce::StringArray kDivLabels {
    "1/1", "1/2.", "1/2", "1/2T", "1/4.", "1/4", "1/4T", "1/8.", "1/8", "1/8T", "1/16", "1/16T" };
constexpr double kCyclesPerBeat[] {
    0.25, 1.0/3.0, 0.5, 0.75, 2.0/3.0, 1.0, 1.5, 4.0/3.0, 2.0, 3.0, 4.0, 6.0 };

struct PresetVal { const char* id; float value; };
struct Preset    { const char* name; std::vector<PresetVal> vals; };

// Factory presets. sync=1/0, syncdiv is a 0-based division index.
const std::vector<Preset>& presets()
{
    static const std::vector<Preset> table {
        { "Init",              { {"rate",0.8f},{"depth",0.12f},{"width",0.9f},{"mix",0.75f},{"sections",6},{"color",0.55f},{"spread",0.65f},{"emphasis",0.0f},{"sync",0},{"syncdiv",5} } },
        { "Slow Sweep",        { {"rate",0.25f},{"depth",0.18f},{"width",1.2f},{"mix",0.8f},{"sections",6},{"color",0.5f},{"spread",0.6f},{"emphasis",0.0f},{"sync",0} } },
        { "Jet Flanger",       { {"rate",3.5f},{"depth",0.28f},{"width",1.6f},{"mix",0.9f},{"sections",8},{"color",0.72f},{"spread",0.9f},{"emphasis",0.3f},{"sync",0} } },
        { "Deep Notch",        { {"rate",0.5f},{"depth",0.12f},{"width",0.8f},{"mix",1.0f},{"sections",10},{"color",0.6f},{"spread",0.8f},{"emphasis",-0.2f},{"sync",0} } },
        { "Sync · 1/4",        { {"sync",1},{"syncdiv",5},{"depth",0.2f},{"width",1.4f},{"mix",0.85f},{"sections",6},{"color",0.55f},{"spread",0.65f},{"emphasis",0.0f} } },
        { "Sync · 1/8T",       { {"sync",1},{"syncdiv",9},{"depth",0.22f},{"width",1.5f},{"mix",0.8f},{"sections",8},{"color",0.6f},{"spread",0.7f},{"emphasis",0.1f} } },
        { "Wide Shimmer",      { {"rate",1.5f},{"depth",0.15f},{"width",3.0f},{"mix",0.7f},{"sections",12},{"color",0.8f},{"spread",1.0f},{"emphasis",0.0f},{"sync",0} } },
        { "Subtle Warmth",     { {"rate",0.4f},{"depth",0.06f},{"width",0.6f},{"mix",0.35f},{"sections",4},{"color",0.45f},{"spread",0.5f},{"emphasis",0.0f},{"sync",0} } },
    };
    return table;
}
} // namespace

int SchurPhaserAudioProcessor::getNumPrograms() { return (int) presets().size(); }

const juce::String SchurPhaserAudioProcessor::getProgramName (int index)
{
    return juce::isPositiveAndBelow (index, (int) presets().size())
             ? juce::String (presets()[(size_t) index].name) : juce::String();
}

void SchurPhaserAudioProcessor::setCurrentProgram (int index)
{
    if (! juce::isPositiveAndBelow (index, (int) presets().size())) return;
    currentProgram = index;
    for (const auto& pv : presets()[(size_t) index].vals)
        if (auto* p = apvts.getParameter (pv.id))
            p->setValueNotifyingHost (p->convertTo0to1 (pv.value));
}

SchurPhaserAudioProcessor::SchurPhaserAudioProcessor()
    : AudioProcessor (BusesProperties()
                        .withInput  ("Input",  juce::AudioChannelSet::stereo(), true)
                        .withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      apvts (*this, nullptr, "PARAMS", createParameterLayout())
{
    rebuildDesign();
}

void SchurPhaserAudioProcessor::maybeRebuild()
{
    const float sections = *apvts.getRawParameterValue (IDs::sections);
    const float color    = *apvts.getRawParameterValue (IDs::color);
    const float spread   = *apvts.getRawParameterValue (IDs::spread);
    const float emphasis = *apvts.getRawParameterValue (IDs::emphasis);

    if (sections != lastSections || color != lastColor
        || spread != lastSpread || emphasis != lastEmphasis)
    {
        rebuildDesign();   // updates coefficients in place; does not reset filter state
        lastSections = sections; lastColor = color;
        lastSpread = spread; lastEmphasis = emphasis;
    }
}

juce::AudioProcessorValueTreeState::ParameterLayout
SchurPhaserAudioProcessor::createParameterLayout()
{
    std::vector<std::unique_ptr<juce::RangedAudioParameter>> params;

    params.push_back (std::make_unique<juce::AudioParameterInt> (
        IDs::sections, "Stages", 2, 16, 6));

    params.push_back (std::make_unique<juce::AudioParameterFloat> (
        juce::ParameterID { IDs::color, 1 }, "Tone",
        juce::NormalisableRange<float> { 0.2f, 0.9f, 0.001f }, 0.55f));

    params.push_back (std::make_unique<juce::AudioParameterFloat> (
        juce::ParameterID { IDs::spread, 1 }, "Spread",
        juce::NormalisableRange<float> { 0.0f, 1.0f, 0.001f }, 0.65f));

    params.push_back (std::make_unique<juce::AudioParameterFloat> (
        juce::ParameterID { IDs::rate, 1 }, "Rate",
        juce::NormalisableRange<float> { 0.05f, 12.0f, 0.01f, 0.45f }, 0.8f,
        juce::AudioParameterFloatAttributes().withLabel ("Hz")));

    params.push_back (std::make_unique<juce::AudioParameterFloat> (
        juce::ParameterID { IDs::depth, 1 }, "Depth",
        juce::NormalisableRange<float> { 0.0f, 0.35f, 0.001f }, 0.12f));

    params.push_back (std::make_unique<juce::AudioParameterFloat> (
        juce::ParameterID { IDs::width, 1 }, "Width",
        juce::NormalisableRange<float> { 0.0f, 3.14f, 0.001f }, 0.9f));

    params.push_back (std::make_unique<juce::AudioParameterFloat> (
        juce::ParameterID { IDs::mix, 1 }, "Mix",
        juce::NormalisableRange<float> { 0.0f, 1.0f, 0.001f }, 0.75f));

    params.push_back (std::make_unique<juce::AudioParameterFloat> (
        juce::ParameterID { IDs::emphasis, 1 }, "Emphasis",
        juce::NormalisableRange<float> { -1.0f, 1.0f, 0.001f }, 0.0f));

    params.push_back (std::make_unique<juce::AudioParameterBool> (
        juce::ParameterID { IDs::sync, 1 }, "Sync", false));

    params.push_back (std::make_unique<juce::AudioParameterChoice> (
        juce::ParameterID { IDs::syncdiv, 1 }, "Division", kDivLabels, 5));

    return { params.begin(), params.end() };
}

void SchurPhaserAudioProcessor::rebuildDesign()
{
    const int sections = (int) *apvts.getRawParameterValue (IDs::sections);
    const float color  = *apvts.getRawParameterValue (IDs::color);
    const float spread = *apvts.getRawParameterValue (IDs::spread);
    const float emphasis = *apvts.getRawParameterValue (IDs::emphasis);

    float poles[schur::kMaxOrder] {};
    schur::LatticeEngine::designPolesFromParams (sections, color, spread, poles);

    for (int i = 0; i < sections; ++i)
    {
        const float t = (sections <= 1) ? 0.0f : (float) i / (float) (sections - 1);
        const float tilt = emphasis * 0.25f * (t - 0.5f);
        poles[i] = std::clamp (poles[i] + tilt, 0.05f, 0.95f);
    }

    for (auto& e : engines)
        e.designFromPoles (poles, sections);

    // Publish the (unmodulated) design to the UI snapshot.
    const int ord = engines[0].order;
    snapOrder.store (ord, std::memory_order_relaxed);
    for (int i = 0; i < ord; ++i)
        baseK[(size_t) i].store (engines[0].kBase[(size_t) i], std::memory_order_relaxed);
}

bool SchurPhaserAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono()
        && layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
        return false;

    if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet())
        return false;

    return true;
}

void SchurPhaserAudioProcessor::prepareToPlay (double sampleRate, int)
{
    currentSampleRate = sampleRate;
    for (auto& e : engines)
    {
        e.setSampleRate (sampleRate);
        e.reset();
    }
    phaseTime = 0.0;
    tap.prepare (1 << 15);

    mixSm.reset (sampleRate, 0.02);
    depthSm.reset (sampleRate, 0.02);
    widthSm.reset (sampleRate, 0.02);
    mixSm.setCurrentAndTargetValue (*apvts.getRawParameterValue (IDs::mix));
    depthSm.setCurrentAndTargetValue (*apvts.getRawParameterValue (IDs::depth));
    widthSm.setCurrentAndTargetValue (*apvts.getRawParameterValue (IDs::width));

    lastSections = lastColor = lastSpread = -1.0f;   // force a rebuild on first block
    lastEmphasis = -999.0f;
    rebuildDesign();
}

void SchurPhaserAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer,
                                              juce::MidiBuffer&)
{
    juce::ScopedNoDenormals noDenormals;

    if (bypassed.load (std::memory_order_relaxed))
        return;   // soft bypass — pass the dry signal through untouched

    const int numSamples = buffer.getNumSamples();
    const int numCh = juce::jmin (2, buffer.getNumChannels());

    maybeRebuild();   // audio-thread coefficient update; no cross-thread race, no state reset

    depthSm.setTargetValue (*apvts.getRawParameterValue (IDs::depth));
    widthSm.setTargetValue (*apvts.getRawParameterValue (IDs::width));
    mixSm.setTargetValue   (*apvts.getRawParameterValue (IDs::mix));

    const bool  sync  = *apvts.getRawParameterValue (IDs::sync) > 0.5f;
    const int   div   = (int) *apvts.getRawParameterValue (IDs::syncdiv);
    const int order   = engines[0].order;

    // Resolve LFO rate: free-running knob, or tempo-locked to the host.
    float rate = *apvts.getRawParameterValue (IDs::rate);
    if (sync)
    {
        double bpm = 120.0, ppq = 0.0;
        bool playing = false;
        if (auto* ph = getPlayHead())
            if (auto pos = ph->getPosition())
            {
                if (auto b = pos->getBpm())          bpm = *b;
                if (auto q = pos->getPpqPosition())  ppq = *q;
                playing = pos->getIsPlaying();
            }
        if (! (bpm > 0.0) || ! std::isfinite (bpm)) bpm = 120.0;   // guard bad/zero tempo
        if (! std::isfinite (ppq)) ppq = 0.0;
        const double cpb = kCyclesPerBeat[juce::jlimit (0, 11, div)];
        rate = (float) (bpm / 60.0 * cpb);
        if (playing)   // lock the sweep phase to the transport
            phaseTime = (ppq * 60.0 / bpm) * currentSampleRate;
    }
    snapRateHz.store (rate, std::memory_order_relaxed);

    auto* inL = buffer.getWritePointer (0);
    float* inR = numCh > 1 ? buffer.getWritePointer (1) : nullptr;

    for (int n = 0; n < numSamples; ++n)
    {
        const float t = (float) (phaseTime / currentSampleRate);
        const float dsm = depthSm.getNextValue();
        const float wsm = widthSm.getNextValue();
        const float msm = mixSm.getNextValue();

        for (int ch = 0; ch < numCh; ++ch)
        {
            const float stereoPhase = (ch == 0) ? 0.0f : wsm;
            auto& eng = engines[(size_t) ch];
            eng.fillModulatedK (t, dsm, rate, stereoPhase, kScratch.data(), order);

            const float dry = (ch == 0) ? inL[n] : inR[n];
            const float wet = eng.processSample (dry, kScratch.data(), order);
            const float y = dry * (1.0f - msm) + wet * msm;

            if (ch == 0)
                inL[n] = y;
            else
                inR[n] = y;
        }

        phaseTime += 1.0;
    }

    // --- Publish an animation snapshot for the editor (channel 0, end of block). ---
    const float depthNow = depthSm.getTargetValue();
    const float tNow = (float) (phaseTime / currentSampleRate);
    float kNow[schur::kMaxOrder] {};
    engines[0].fillModulatedK (tNow, depthNow, rate, 0.0f, kNow, order);
    for (int i = 0; i < order; ++i)
        liveK[(size_t) i].store (kNow[i], std::memory_order_relaxed);
    snapOrder.store (order, std::memory_order_relaxed);
    snapMix.store (mixSm.getTargetValue(), std::memory_order_relaxed);
    snapDepth.store (depthNow, std::memory_order_relaxed);
    snapSampleRate.store (currentSampleRate, std::memory_order_relaxed);
    snapActive.store (true, std::memory_order_relaxed);

    tap.push (inL, inR, numSamples);
}

void SchurPhaserAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    if (auto xml = apvts.copyState().createXml())
        copyXmlToBinary (*xml, destData);
}

void SchurPhaserAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    if (auto xml = getXmlFromBinary (data, sizeInBytes))
        if (xml->hasTagName (apvts.state.getType()))
            apvts.replaceState (juce::ValueTree::fromXml (*xml));
    rebuildDesign();
}

juce::AudioProcessorEditor* SchurPhaserAudioProcessor::createEditor()
{
    return new SchurPhaserAudioProcessorEditor (*this);
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new SchurPhaserAudioProcessor();
}