cmake_minimum_required(VERSION 3.22)
project(PhaseAlign VERSION 1.0.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(
    JUCE
    GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
    GIT_TAG        8.0.6
    GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(JUCE)

juce_add_plugin(PhaseAlign
    COMPANY_NAME "Flow"
    BUNDLE_ID com.flow.phasealign
    PLUGIN_MANUFACTURER_CODE Flwr
    PLUGIN_CODE PhAl
    FORMATS VST3 AU Standalone
    PRODUCT_NAME "Phase Align"
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    COPY_PLUGIN_AFTER_BUILD TRUE
    VST3_CATEGORIES Fx Tools
)

juce_generate_juce_header(PhaseAlign)

# Reuse the Schur all-pass engine + shared look-and-feel from the sibling plugin.
set(SCHUR_SHARED "${CMAKE_CURRENT_SOURCE_DIR}/../SchurPhaser/Source")

target_sources(PhaseAlign
    PRIVATE
        Source/PluginProcessor.cpp
        Source/PluginEditor.cpp
        Source/ScopeView.cpp
        ${SCHUR_SHARED}/SchurLatticeDSP.cpp
        ${SCHUR_SHARED}/quilio/UndoTree.cpp
        ${SCHUR_SHARED}/quilio/ABSystem.cpp
        ${SCHUR_SHARED}/quilio/PresetManager.cpp
        ${SCHUR_SHARED}/quilio/TopBar.cpp
)

target_include_directories(PhaseAlign PRIVATE ${SCHUR_SHARED} ${SCHUR_SHARED}/quilio)

target_compile_definitions(PhaseAlign
    PUBLIC
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0
        JUCE_DISPLAY_SPLASH_SCREEN=0
)

target_link_libraries(PhaseAlign
    PRIVATE
        juce::juce_audio_utils
        juce::juce_dsp
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags
)
