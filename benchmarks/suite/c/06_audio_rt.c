/* Real-Time Audio Callback Benchmark
 * Tests hard real-time performance with multiple synth voices,
 * filter parameter smoothing, and jitter measurement.
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <stdint.h>

#define PI 3.14159265358979323846
#define TWO_PI 6.28318530717958647692
#define SAMPLE_RATE 48000.0
#define BUFFER_SIZE 256
#define NUM_VOICES 8
#define WAVETABLE_SIZE 2048

typedef struct {
    double phase;
    double phase_inc;
    double amplitude;
} Oscillator;

typedef struct {
    double cutoff;
    double resonance;
    double z1, z2;
    double cutoff_smooth;
    double resonance_smooth;
} Filter;

typedef struct {
    double attack, decay, sustain, release;
    double phase;
    double level;
    int stage;
} Envelope;

typedef struct {
    Oscillator osc;
    Filter filter;
    Envelope env;
    int active;
} Voice;

static double wavetable[WAVETABLE_SIZE];

static inline double osc_sample(Oscillator* osc) {
    int idx = (int)(osc->phase * WAVETABLE_SIZE) % WAVETABLE_SIZE;
    double sample = wavetable[idx] * osc->amplitude;
    
    osc->phase += osc->phase_inc;
    if (osc->phase >= 1.0) osc->phase -= 1.0;
    
    return sample;
}

static inline double filter_process(Filter* flt, double input, double smooth_coeff) {
    flt->cutoff_smooth += smooth_coeff * (flt->cutoff - flt->cutoff_smooth);
    flt->resonance_smooth += smooth_coeff * (flt->resonance - flt->resonance_smooth);
    
    double alpha = flt->cutoff_smooth;
    double output = (1.0 - alpha) * input + alpha * flt->z1;
    
    flt->z1 = output;
    return output;
}

static inline double env_process(Envelope* env) {
    double level = env->level;
    
    if (env->stage == 1) {
        env->level += env->attack;
        if (env->level >= 1.0) {
            env->level = 1.0;
            env->stage = 2;
        }
    }
    if (env->stage == 2) {
        env->level -= env->decay * (env->level - env->sustain);
        if (env->level <= env->sustain + 0.001) {
            env->level = env->sustain;
            env->stage = 3;
        }
    }
    if (env->stage == 4) {
        env->level *= (1.0 - env->release);
        if (env->level < 0.001) {
            env->level = 0.0;
            env->stage = 0;
        }
    }
    
    return level;
}

void init_wavetable(void) {
    for (int i = 0; i < WAVETABLE_SIZE; i++) {
        wavetable[i] = sin((double)i / WAVETABLE_SIZE * TWO_PI);
    }
}

void init_voice(Voice* v, double freq) {
    v->osc.phase = 0.0;
    v->osc.phase_inc = freq / SAMPLE_RATE;
    v->osc.amplitude = 0.5;
    
    v->filter.cutoff = 0.3;
    v->filter.resonance = 0.5;
    v->filter.z1 = v->filter.z2 = 0.0;
    v->filter.cutoff_smooth = 0.3;
    v->filter.resonance_smooth = 0.5;
    
    v->env.attack = 0.001;
    v->env.decay = 0.0005;
    v->env.sustain = 0.7;
    v->env.release = 0.0001;
    v->env.phase = 0.0;
    v->env.level = 0.0;
    v->env.stage = 1;
    
    v->active = 1;
}

double process_callback(Voice* voices, double* buffer, double param_automation) {
    clock_t start = clock();
    
    /* Clear buffer */
    for (int i = 0; i < BUFFER_SIZE; i++) {
        buffer[i] = 0.0;
    }
    
    /* Process each voice */
    for (int v = 0; v < NUM_VOICES; v++) {
        if (voices[v].active) {
            voices[v].filter.cutoff = 0.2 + 0.3 * param_automation;
            
            for (int i = 0; i < BUFFER_SIZE; i++) {
                double osc_out = osc_sample(&voices[v].osc);
                double filt_out = filter_process(&voices[v].filter, osc_out, 0.001);
                double env_level = env_process(&voices[v].env);
                buffer[i] += filt_out * env_level;
            }
        }
    }
    
    /* Master gain / limiting */
    for (int i = 0; i < BUFFER_SIZE; i++) {
        double sample = buffer[i] * 0.125;
        if (sample > 1.0) sample = 1.0;
        else if (sample < -1.0) sample = -1.0;
        buffer[i] = sample;
    }
    
    clock_t end = clock();
    return (double)(end - start) / CLOCKS_PER_SEC * 1000000.0;
}

int main() {
    printf("==============================================\n");
    printf("  REAL-TIME AUDIO CALLBACK BENCHMARK - C\n");
    printf("==============================================\n\n");
    printf("Sample rate: %.0f Hz\n", SAMPLE_RATE);
    printf("Buffer size: %d samples (%.2f ms)\n", 
           BUFFER_SIZE, BUFFER_SIZE / SAMPLE_RATE * 1000.0);
    printf("Voices: %d\n\n", NUM_VOICES);
    
    double deadline_us = BUFFER_SIZE / SAMPLE_RATE * 1000000.0;
    printf("Hard deadline: %.1f µs\n\n", deadline_us);
    
    init_wavetable();
    
    Voice voices[NUM_VOICES];
    double freqs[] = {261.63, 329.63, 392.00, 523.25, 659.26, 783.99, 130.81, 196.00};
    for (int v = 0; v < NUM_VOICES; v++) {
        init_voice(&voices[v], freqs[v]);
    }
    
    double buffer[BUFFER_SIZE];
    
    double total_time = 0.0;
    double max_time = 0.0;
    double min_time = 1000000.0;
    double sum_sq = 0.0;
    int deadline_misses = 0;
    
    int num_callbacks = 10 * 48000 / BUFFER_SIZE;
    printf("Running %d callbacks (10 sec audio)...\n\n", num_callbacks);
    
    for (int cb = 0; cb < num_callbacks; cb++) {
        double param = 0.5 + 0.5 * sin(cb * 0.01);
        double callback_time = process_callback(voices, buffer, param);
        
        total_time += callback_time;
        sum_sq += callback_time * callback_time;
        
        if (callback_time > max_time) max_time = callback_time;
        if (callback_time < min_time) min_time = callback_time;
        if (callback_time > deadline_us) deadline_misses++;
    }
    
    double avg_time = total_time / num_callbacks;
    double variance = sum_sq / num_callbacks - avg_time * avg_time;
    double jitter = sqrt(variance);
    
    printf("Results:\n");
    printf("─────────────────────────────────────────────\n");
    printf("  Average callback time: %.1f µs\n", avg_time);
    printf("  Min callback time:     %.1f µs\n", min_time);
    printf("  Max callback time:     %.1f µs\n", max_time);
    printf("  Jitter (stddev):       %.1f µs\n", jitter);
    printf("  CPU usage:             %.1f%%\n", avg_time / deadline_us * 100.0);
    printf("  Deadline misses:       %d / %d %s\n", 
           deadline_misses, num_callbacks, deadline_misses == 0 ? "✓" : "✗");
    printf("  Headroom:              %.1f µs\n", deadline_us - max_time);
    
    printf("\nBenchmark complete.\n");
    return 0;
}
