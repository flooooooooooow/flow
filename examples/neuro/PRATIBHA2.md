# Pratibha-2 EEG embeddings

`pratibha2.flow` runs the Pratibha-2 encoder in Flow. The Flow program reads the checkpoint's Safetensors file, applies the model's patch embedding and positional encoding, runs all 22 transformer blocks, then writes one embedding with 512 values as a CSV row.

## Model files

The code and weights use revision `863edc940d82a02744776a7820641bf1bc32310b` from [MannasAI/pratibha-2](https://huggingface.co/MannasAI/pratibha-2). Download its configuration and weights:

```bash
mkdir -p "$HOME/.cache/flow/pratibha-2"
curl -L --fail https://huggingface.co/MannasAI/pratibha-2/resolve/863edc940d82a02744776a7820641bf1bc32310b/config.json -o "$HOME/.cache/flow/pratibha-2/config.json"
curl -L --fail https://huggingface.co/MannasAI/pratibha-2/resolve/863edc940d82a02744776a7820641bf1bc32310b/model.safetensors -o "$HOME/.cache/flow/pratibha-2/model.safetensors"
```

The weights file is about 371 MB. The inference program uses only Flow and the C math and file functions already used by Flow's standard library. It does not import Transformers or PyTorch, and it does not execute the model's remote Python code.

## Input and run

Create a CSV with one electrode per column and one sample per row. Use exact electrode names from the model configuration. Samples must be at 200 Hz. The program z-scores each channel across the whole input, because the encoder expects preprocessed EEG. It does not filter or resample the signal. Patches contain 200 samples and advance by 180 samples. It ignores incomplete trailing samples.

The output is one CSV row of 512 values: the encoder's per-token features averaged over every channel-patch token. On a four-channel, 260-sample recording the row matches the upstream PyTorch encoder, given the same preprocessing, at cosine 0.9999999 with a maximum absolute difference of 1e-6. A single window with a handful of channels takes about a second.

```bash
PRATIBHA_MODEL_DIR="$HOME/.cache/flow/pratibha-2" \
PRATIBHA_INPUT=recording.csv \
PRATIBHA_OUTPUT=embedding.csv \
  ./flow run examples/neuro/pratibha2.flow
```

The model's weights and code are released under Apache-2.0. See the upstream [model card](https://huggingface.co/MannasAI/pratibha-2) for the model description and citation.
