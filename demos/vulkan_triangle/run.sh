#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ICD_JSON="/opt/homebrew/opt/molten-vk/etc/vulkan/icd.d/MoltenVK_icd.json"
LAYER_PATH="/opt/homebrew/opt/vulkan-validationlayers/share/vulkan/explicit_layer.d"

if [[ -f "$ICD_JSON" ]]; then
  export VK_ICD_FILENAMES="$ICD_JSON"
fi

if [[ -d "$LAYER_PATH" ]]; then
  export VK_LAYER_PATH="$LAYER_PATH"
fi

: "${FLOW_VK_PRETTY:=1}"
export FLOW_VK_PRETTY

: "${FLOW_VK_TRACE:=1}"
export FLOW_VK_TRACE

VK_LAYER_LIB="/opt/homebrew/opt/vulkan-validationlayers/lib"
VK_LOADER_LIB="/opt/homebrew/opt/vulkan-loader/lib"
VK_MOLTENVK_LIB="/opt/homebrew/opt/molten-vk/lib"

DYLD_PATHS=()
[[ -d "$VK_LAYER_LIB" ]] && DYLD_PATHS+=("$VK_LAYER_LIB")
[[ -d "$VK_LOADER_LIB" ]] && DYLD_PATHS+=("$VK_LOADER_LIB")
[[ -d "$VK_MOLTENVK_LIB" ]] && DYLD_PATHS+=("$VK_MOLTENVK_LIB")

if [[ ${#DYLD_PATHS[@]} -gt 0 ]]; then
  IFS=: read -r -a EXISTING <<< "${DYLD_LIBRARY_PATH:-}"
  export DYLD_LIBRARY_PATH="$(IFS=:; echo "${DYLD_PATHS[*]}${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}")"
fi

exec "$ROOT/vulkan_triangle"
