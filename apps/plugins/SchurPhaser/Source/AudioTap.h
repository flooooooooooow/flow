#pragma once

#include <JuceHeader.h>
#include <vector>

namespace schurUi
{

//==============================================================================
/** Lock-free single-producer / single-consumer tap. The audio thread pushes
    post-processing L/R frames; the editor drains them on its timer for the
    spectrum analyser and correlation meter. Never allocates on the audio thread. */
class AudioTap
{
public:
    void prepare (int capacity = 1 << 15)
    {
        capacity = juce::nextPowerOfTwo (capacity);
        fifo.setTotalSize (capacity);
        bufL.assign ((size_t) capacity, 0.0f);
        bufR.assign ((size_t) capacity, 0.0f);
    }

    void push (const float* l, const float* r, int n) noexcept
    {
        if (bufL.empty()) return;
        const auto scope = fifo.write (n);
        const float* src = l;
        int idx = 0;
        for (int blk = 0; blk < 2; ++blk)
        {
            const int start = (blk == 0) ? scope.startIndex1 : scope.startIndex2;
            const int size  = (blk == 0) ? scope.blockSize1  : scope.blockSize2;
            for (int i = 0; i < size; ++i)
            {
                bufL[(size_t) (start + i)] = l[idx + i];
                bufR[(size_t) (start + i)] = r ? r[idx + i] : l[idx + i];
            }
            idx += size;
        }
        juce::ignoreUnused (src);
    }

    /** Drain up to n frames; returns the number actually read. */
    int pop (float* outL, float* outR, int n) noexcept
    {
        if (bufL.empty()) return 0;
        n = juce::jmin (n, fifo.getNumReady());
        const auto scope = fifo.read (n);
        int idx = 0;
        for (int blk = 0; blk < 2; ++blk)
        {
            const int start = (blk == 0) ? scope.startIndex1 : scope.startIndex2;
            const int size  = (blk == 0) ? scope.blockSize1  : scope.blockSize2;
            for (int i = 0; i < size; ++i)
            {
                outL[idx + i] = bufL[(size_t) (start + i)];
                outR[idx + i] = bufR[(size_t) (start + i)];
            }
            idx += size;
        }
        return n;
    }

    int numReady() const noexcept { return fifo.getNumReady(); }

private:
    juce::AbstractFifo fifo { 2 };
    std::vector<float> bufL, bufR;
};

} // namespace schurUi
