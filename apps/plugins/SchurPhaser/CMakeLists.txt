cmake_minimum_required(VERSION 3.22)
project(SchurPhaser VERSION 1.0.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Quilio SDK path (its shared quilio_ui TopBar is compiled in below).
set(QUILIO_SDK "/Users/abhishekshivakumar/vstplugins/QuilioSDK" CACHE PATH "Path to the Quilio SDK")

# NOTE: the SDK ships JUCE 7.0.12, but its own quilio_ui/TopBar.cpp (and our code)
# use juce::FontOptions, a JUCE 8 API. So we build against JUCE 8 and link only the
# SDK's shared UI source.
include(FetchContent)
FetchContent_Declare(JUCE
    GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
    GIT_TAG 8.0.6 GIT_SHALLOW TRUE)
FetchContent_MakeAvailable(JUCE)

juce_add_plugin(SchurPhaser
    COMPANY_NAME "Flow"
    BUNDLE_ID com.flow.schurphaser
    PLUGIN_MANUFACTURER_CODE Flwr
    PLUGIN_CODE SchP
    FORMATS VST3 AU Standalone
    PRODUCT_NAME "Schur Phase"
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    COPY_PLUGIN_AFTER_BUILD TRUE
    VST3_CATEGORIES Fx Modulation
)

juce_generate_juce_header(SchurPhaser)

target_sources(SchurPhaser
    PRIVATE
        Source/PluginProcessor.cpp
        Source/PluginEditor.cpp
        Source/PhaseScope.cpp
        Source/SchurLatticeDSP.cpp
        "${QUILIO_SDK}/quilio_ui/components/TopBar.cpp"
)

target_include_directories(SchurPhaser PRIVATE
    "${QUILIO_SDK}/quilio_ui/components"
)

target_compile_definitions(SchurPhaser
    PUBLIC
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0
        JUCE_DISPLAY_SPLASH_SCREEN=0
)

target_link_libraries(SchurPhaser
    PRIVATE
        juce::juce_audio_utils
        juce::juce_dsp
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags
)