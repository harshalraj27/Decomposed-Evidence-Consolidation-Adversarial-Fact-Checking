# Models Directory

This directory contains the local LLM used for claim decomposition.

## Required Model

### Meta-Llama-3-8B-Instruct (Q5_K_M)

The system requires a quantized Llama-3 model for decomposing complex claims into atomic subclaims.

**Model:** `Meta-Llama-3-8B-Instruct-Q5_K_M.gguf`  
**Source:** [QuantFactory/Meta-Llama-3-8B-Instruct-GGUF](https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF)  
**Size:** ~5.7GB  
**Quantization:** Q5_K_M (balanced quality/size trade-off)

---

## Download Instructions

### Option 1: Direct Download (Recommended)

1. Visit: https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF
2. Download: `Meta-Llama-3-8B-Instruct-Q5_K_M.gguf`
3. Place in this directory (`models/`)

**Direct link:** [Meta-Llama-3-8B-Instruct-Q5_K_M.gguf](https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/blob/main/Meta-Llama-3-8B-Instruct-Q5_K_M.gguf)

---

### Option 2: Command Line (huggingface-cli)
```bash
# Install huggingface-hub if not already installed
pip install huggingface-hub

# Download model to this directory
huggingface-cli download QuantFactory/Meta-Llama-3-8B-Instruct-GGUF \
  Meta-Llama-3-8B-Instruct-Q5_K_M.gguf \
  --local-dir . \
  --local-dir-use-symlinks False
```

---

### Option 3: Python Script
```python
from huggingface_hub import hf_hub_download

hf_hub_download(
    repo_id="QuantFactory/Meta-Llama-3-8B-Instruct-GGUF",
    filename="Meta-Llama-3-8B-Instruct-Q5_K_M.gguf",
    local_dir="models/",
    local_dir_use_symlinks=False
)
```

---

## Verify Installation

After downloading, verify the model is in place:
```bash
ls -lh Meta-Llama-3-8B-Instruct-Q5_K_M.gguf
```

**Expected output:**
```
-rw-r--r-- 1 user user 5.7G Jan 04 10:00 Meta-Llama-3-8B-Instruct-Q5_K_M.gguf
```

---

## Model Specifications

| Property | Value |
|----------|-------|
| **Base Model** | Meta-Llama-3-8B-Instruct |
| **Quantization** | Q5_K_M |
| **File Size** | ~5.7GB |
| **Context Length** | 8192 tokens |
| **Parameters** | 8 billion |
| **Format** | GGUF |
| **Inference Engine** | llama.cpp |

---

## Why Q5_K_M Quantization?

**Q5_K_M** (5-bit quantization, medium) provides:
- **Quality:** Minimal performance degradation vs FP16
- **Size:** ~5.7GB (vs ~16GB for FP16)
- **Speed:** Faster inference on consumer GPUs
- **Memory:** Fits in 8GB VRAM with headroom for other models

**Alternative quantizations available but not recommended:**
- Q2_K: Too aggressive, noticeable quality loss
- Q4_K_M: Slightly smaller (~4.9GB) but lower quality
- Q6_K: Larger (~7GB) with minimal quality gain
- Q8_0: Much larger (~8.5GB) for marginal improvement

---

## Usage in Pipeline

This model is loaded by `app/llm_decomposer.py` and used for:
- Deciding if a claim needs decomposition
- Breaking complex claims into atomic subclaims
- Preserving original claim semantics without adding facts

**Typical inference:**
- Input: Complex claim (e.g., "X improves Y but causes Z")
- Output: JSON with subclaims ["X improves Y", "X causes Z"]
- Time: ~2-5 seconds per claim on RTX 4070

---

## Troubleshooting

### Model Not Found Error
```
FileNotFoundError: models/Meta-Llama-3-8B-Instruct-Q5_K_M.gguf not found
```

**Solution:** Verify the model file is in this directory with exact filename.

---

### Out of Memory Error
```
RuntimeError: CUDA out of memory
```

**Solution:** Q5_K_M requires ~6GB VRAM. If you have <8GB VRAM, consider:
- Closing other GPU applications
- Using Q4_K_M quantization (smaller, slight quality loss)
- Running on CPU (much slower but works)

---

### Slow Inference

**Symptom:** Decomposition takes >10 seconds per claim

**Solutions:**
- Verify GPU is being used (check `llm_decomposer.py` for `n_gpu_layers`)
- Ensure CUDA is properly installed
- Check GPU utilization with `nvidia-smi`

---

## License

This model is derived from Meta's Llama-3 and inherits its license:
- **License:** [Llama 3 Community License](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct/blob/main/LICENSE)
- **Usage:** Allowed for research and commercial use with restrictions
- **Attribution:** Required when using this model

---

## Directory Structure

After setup, this directory should contain:
```
models/
├── README.md                                    # This file
└── Meta-Llama-3-8B-Instruct-Q5_K_M.gguf        # LLM model file (~5.7GB)
```

---

## Additional Notes

### Why Local Model?

This project uses a local LLM instead of API-based models (GPT-4, Claude) for:
- **Reproducibility:** Same model version always available
- **Privacy:** No claims sent to external services
- **Cost:** No API fees
- **Control:** Custom prompts, no rate limits

### Model Updates

This README assumes using the specific Q5_K_M quantization. If you update to:
- Different quantization → Update filename in `llm_decomposer.py`
- Different base model → May require prompt adjustments
- Newer Llama version → Test decomposition quality before switching

---

## Support

If you encounter issues:
1. Check model file exists and is ~5.7GB
2. Verify CUDA/GPU setup with `nvidia-smi`
3. Review `app/llm_decomposer.py` configuration
4. Check system RAM (model requires ~8GB during loading)

For model-specific issues, see: https://github.com/ggerganov/llama.cpp