#include "PluginProcessor.h"
#include "PluginEditor.h"

namespace IDs
{
static constexpr auto delay  = "delay";
static constexpr auto freq   = "freq";
static constexpr auto stages = "stages";
static constexpr auto spread = "spread";
static constexpr auto invert = "invert";
static constexpr auto mix    = "mix";
} // namespace IDs

namespace
{
struct PresetVal { const char* id; float value; };
struct Preset    { const char* name; std::vector<PresetVal> vals; };

const std::vector<Preset>& presets()
{
    static const std::vector<Preset> table {
        { "Init",             { {"delay",0.0f},{"freq",200.0f},{"stages",2},{"spread",0.0f},{"invert",0},{"mix",1.0f} } },
        { "Kick / Bass Align",{ {"delay",3.0f},{"freq",90.0f},{"stages",3},{"spread",0.2f},{"invert",0},{"mix",1.0f} } },
        { "Snare Top/Bottom", { {"delay",0.0f},{"freq",250.0f},{"stages",4},{"spread",0.3f},{"invert",1},{"mix",1.0f} } },
        { "DI vs Amp",        { {"delay",1.5f},{"freq",700.0f},{"stages",3},{"spread",0.4f},{"invert",0},{"mix",1.0f} } },
        { "Wide Decorrelate", { {"delay",0.0f},{"freq",400.0f},{"stages",6},{"spread",1.0f},{"invert",0},{"mix",1.0f} } },
        { "Bass Mono Fix",    { {"delay",0.0f},{"freq",120.0f},{"stages",2},{"spread",0.0f},{"invert",0},{"mix",1.0f} } },
    };
    return table;
}

constexpr float kMaxDelayMs = 20.0f;

// First-order all-pass reflection coefficient whose -90 degree point sits at fc.
inline float coeffForFreq (float fc, double sr) noexcept
{
    const float b = std::tan (juce::MathConstants<float>::pi * fc / (float) sr);
    return juce::jlimit (-0.999f, 0.999f, (b - 1.0f) / (b + 1.0f));
}
} // namespace

PhaseAlignAudioProcessor::PhaseAlignAudioProcessor()
    : AudioProcessor (BusesProperties()
                        .withInput  ("Input",  juce::AudioChannelSet::stereo(), true)
                        .withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      apvts (*this, nullptr, "PARAMS", createParameterLayout())
{
    rebuildDesign();

    std::vector<PresetManager::Factory> fac;
    for (const auto& p : presets())
    {
        PresetManager::Factory f;
        f.name = p.name;
        for (const auto& v : p.vals) f.values.push_back ({ juce::String (v.id), v.value });
        fac.push_back (std::move (f));
    }
    presetManager = std::make_unique<PresetManager> (apvts, std::move (fac), "PhaseAlign");
    abSystem      = std::make_unique<ABSystem> (apvts, 2);
}

void PhaseAlignAudioProcessor::maybeRebuild()
{
    const float stages = *apvts.getRawParameterValue (IDs::stages);
    const float freq   = *apvts.getRawParameterValue (IDs::freq);
    const float spread = *apvts.getRawParameterValue (IDs::spread);
    if (stages != lastStages || freq != lastFreq || spread != lastSpread)
    {
        rebuildDesign();   // in-place coefficient update on the audio thread
        lastStages = stages; lastFreq = freq; lastSpread = spread;
    }
}

juce::AudioProcessorValueTreeState::ParameterLayout
PhaseAlignAudioProcessor::createParameterLayout()
{
    std::vector<std::unique_ptr<juce::RangedAudioParameter>> params;

    params.push_back (std::make_unique<juce::AudioParameterFloat> (
        juce::ParameterID { IDs::delay, 1 }, "Delay",
        juce::NormalisableRange<float> { 0.0f, kMaxDelayMs, 0.001f }, 0.0f,
        juce::AudioParameterFloatAttributes().withLabel ("ms")));

    params.push_back (std::make_unique<juce::AudioParameterFloat> (
        juce::ParameterID { IDs::freq, 1 }, "Freq",
        juce::NormalisableRange<float> { 20.0f, 20000.0f, 0.1f, 0.28f }, 200.0f,
        juce::AudioParameterFloatAttributes().withLabel ("Hz")));

    params.push_back (std::make_unique<juce::AudioParameterInt> (
        IDs::stages, "Stages", 1, 8, 2));

    params.push_back (std::make_unique<juce::AudioParameterFloat> (
        juce::ParameterID { IDs::spread, 1 }, "Spread",
        juce::NormalisableRange<float> { 0.0f, 1.0f, 0.001f }, 0.0f));

    params.push_back (std::make_unique<juce::AudioParameterBool> (
        juce::ParameterID { IDs::invert, 1 }, "Invert", false));

    params.push_back (std::make_unique<juce::AudioParameterFloat> (
        juce::ParameterID { IDs::mix, 1 }, "Mix",
        juce::NormalisableRange<float> { 0.0f, 1.0f, 0.001f }, 1.0f));

    return { params.begin(), params.end() };
}

int PhaseAlignAudioProcessor::getNumPrograms() { return (int) presets().size(); }

const juce::String PhaseAlignAudioProcessor::getProgramName (int index)
{
    return juce::isPositiveAndBelow (index, (int) presets().size())
             ? juce::String (presets()[(size_t) index].name) : juce::String();
}

void PhaseAlignAudioProcessor::setCurrentProgram (int index)
{
    if (! juce::isPositiveAndBelow (index, (int) presets().size())) return;
    currentProgram = index;
    for (const auto& pv : presets()[(size_t) index].vals)
        if (auto* p = apvts.getParameter (pv.id))
            p->setValueNotifyingHost (p->convertTo0to1 (pv.value));
}

void PhaseAlignAudioProcessor::rebuildDesign()
{
    const int   stages = (int) *apvts.getRawParameterValue (IDs::stages);
    const float freq   = *apvts.getRawParameterValue (IDs::freq);
    const float spread = *apvts.getRawParameterValue (IDs::spread);
    const int   n      = juce::jlimit (1, schur::kMaxOrder, stages);
    const float nyq    = (float) (currentSampleRate * 0.49);

    float k[schur::kMaxOrder] {};
    for (int i = 0; i < n; ++i)
    {
        // spread the sections geometrically around `freq` (up to +/-1 octave)
        const float rel = (n <= 1) ? 0.0f : ((float) i / (float) (n - 1) - 0.5f);
        const float fc  = juce::jlimit (20.0f, nyq, freq * std::pow (2.0f, spread * 2.0f * rel));
        k[i] = coeffForFreq (fc, currentSampleRate);
    }

    for (auto& e : engines)
        e.updateReflections (k, n);   // no state reset — click-free live changes

    // publish snapshot
    snapOrder.store (n, std::memory_order_relaxed);
    snapFreq.store (freq, std::memory_order_relaxed);
    snapSampleRate.store (currentSampleRate, std::memory_order_relaxed);
    for (int i = 0; i < n; ++i)
        designK[(size_t) i].store (k[i], std::memory_order_relaxed);
}

bool PhaseAlignAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono()
        && layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
        return false;
    return layouts.getMainOutputChannelSet() == layouts.getMainInputChannelSet();
}

void PhaseAlignAudioProcessor::prepareToPlay (double sampleRate, int)
{
    currentSampleRate = sampleRate;
    for (auto& e : engines) { e.setSampleRate (sampleRate); e.reset(); }
    for (auto& d : delays)  { d.prepare (sampleRate, kMaxDelayMs); d.reset(); }
    tap.prepare (1 << 15);

    mixSm.reset (sampleRate, 0.02);
    delaySm.reset (sampleRate, 0.05);   // slower ramp — retuning the delay glides cleanly
    mixSm.setCurrentAndTargetValue (*apvts.getRawParameterValue (IDs::mix));
    delaySm.setCurrentAndTargetValue (*apvts.getRawParameterValue (IDs::delay) * 0.001f * (float) sampleRate);

    lastStages = lastFreq = lastSpread = -1.0f;   // force first-block rebuild
    rebuildDesign();
}

void PhaseAlignAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&)
{
    juce::ScopedNoDenormals noDenormals;

    if (bypassed.load (std::memory_order_relaxed))
        return;   // soft bypass — dry passthrough

    const int numSamples = buffer.getNumSamples();
    const int numCh = juce::jmin (2, buffer.getNumChannels());

    maybeRebuild();   // audio-thread coefficient update; no cross-thread race, no state reset

    const float delayMs = *apvts.getRawParameterValue (IDs::delay);
    const bool  invert  = *apvts.getRawParameterValue (IDs::invert) > 0.5f;
    const int   order   = engines[0].order;
    const float sign    = invert ? -1.0f : 1.0f;

    mixSm.setTargetValue   (*apvts.getRawParameterValue (IDs::mix));
    delaySm.setTargetValue (delayMs * 0.001f * (float) currentSampleRate);

    snapDelayMs.store (delayMs, std::memory_order_relaxed);
    snapInvert.store (invert, std::memory_order_relaxed);

    float* chData[2] = { buffer.getWritePointer (0),
                         numCh > 1 ? buffer.getWritePointer (1) : nullptr };

    for (int n = 0; n < numSamples; ++n)
    {
        const float dsamp = delaySm.getNextValue();   // smoothed delay, shared L/R
        const float msm   = mixSm.getNextValue();
        for (int ch = 0; ch < numCh; ++ch)
        {
            float* data = chData[ch];
            const float dry = data[n];
            const float delayed = delays[(size_t) ch].process (dry, dsamp);
            const float wet = sign * engines[(size_t) ch].processSample (delayed, engines[(size_t) ch].kBase.data(), order);
            data[n] = dry * (1.0f - msm) + wet * msm;
        }
    }

    // ---- L/R phase correlation on the processed output ----
    {
        const float* l = buffer.getReadPointer (0);
        const float* r = numCh > 1 ? buffer.getReadPointer (1) : l;
        double sLL = 0.0, sRR = 0.0, sLR = 0.0;
        for (int n = 0; n < numSamples; ++n)
        {
            sLL += (double) l[n] * l[n];
            sRR += (double) r[n] * r[n];
            sLR += (double) l[n] * r[n];
        }
        const double denom = std::sqrt (sLL * sRR);
        const float corr = (denom > 1.0e-9) ? (float) juce::jlimit (-1.0, 1.0, sLR / denom) : 1.0f;
        const float prev = snapCorrelation.load (std::memory_order_relaxed);
        snapCorrelation.store (prev + 0.2f * (corr - prev), std::memory_order_relaxed);

        tap.push (buffer.getWritePointer (0),
                  numCh > 1 ? buffer.getWritePointer (1) : nullptr, numSamples);
    }
}

void PhaseAlignAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    if (auto xml = apvts.copyState().createXml())
        copyXmlToBinary (*xml, destData);
}

void PhaseAlignAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    if (auto xml = getXmlFromBinary (data, sizeInBytes))
        if (xml->hasTagName (apvts.state.getType()))
            apvts.replaceState (juce::ValueTree::fromXml (*xml));
    rebuildDesign();
}

juce::AudioProcessorEditor* PhaseAlignAudioProcessor::createEditor()
{
    return new PhaseAlignAudioProcessorEditor (*this);
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new PhaseAlignAudioProcessor();
}
