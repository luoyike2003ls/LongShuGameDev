#!/bin/bash
# ============================================================
# LongShu (龙枢) Quick Launch Script
# ============================================================
# Auto-detects hardware and sets optimal parameters.
#
# Usage:
#   ./run_longshu.sh                    # Interactive mode
#   ./run_longshu.sh "你的问题"          # One-shot question
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL_DIR="${SCRIPT_DIR}/../models"
PROMPT_DIR="${SCRIPT_DIR}/../prompts"

# Default model path — look for the first GGUF file
MODEL_PATH=""
if [ -n "$1" ] && [ -f "$1" ]; then
    MODEL_PATH="$1"
    PROMPT="$2"
else
    # Auto-detect
    for f in "${MODEL_DIR}"/*.gguf; do
        if [ -f "$f" ]; then
            MODEL_PATH="$f"
            break
        fi
    done
    if [ -z "$MODEL_PATH" ]; then
        echo "❌ Model not found. Please place a .gguf file in ${MODEL_DIR}/"
        echo "   Or pass the path directly: ./run_longshu.sh /path/to/model.gguf"
        exit 1
    fi
fi

echo "🐉 LongShu (龙枢) — Game Development LLM"
echo "========================================="
echo "Model: ${MODEL_PATH}"
echo ""

# ============================================================
# Auto-detect hardware and set optimal parameters
# ============================================================
detect_hardware() {
    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS — Apple Silicon
        MEMORY=$(sysctl -n hw.memsize 2>/dev/null || echo "0")
        MEMORY_GB=$((MEMORY / 1073741824))

        if [ "$MEMORY_GB" -ge 64 ]; then
            echo "🔧 Detected: Apple Silicon (${MEMORY_GB}GB RAM)"
            GPU_LAYERS=-1     # All layers on Metal
            THREADS=10
            BATCH_SIZE=512
            CTX=8192
        elif [ "$MEMORY_GB" -ge 32 ]; then
            echo "🔧 Detected: Apple Silicon (${MEMORY_GB}GB RAM) — limited mode"
            GPU_LAYERS=-1
            THREADS=8
            BATCH_SIZE=256
            CTX=4096
        fi
    elif command -v nvidia-smi &>/dev/null; then
        # Linux with NVIDIA GPU
        GPU_COUNT=$(nvidia-smi -L 2>/dev/null | wc -l)
        GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)

        if [ "$GPU_COUNT" -ge 2 ] && [ "$GPU_MEM" -ge 24000 ]; then
            echo "🔧 Detected: Dual GPU (${GPU_COUNT}× ${GPU_MEM}MB VRAM)"
            GPU_LAYERS=60
            THREADS=16
            BATCH_SIZE=1024
            TENSOR_SPLIT="1,1"
        elif [ "$GPU_MEM" -ge 24000 ]; then
            echo "🔧 Detected: Single GPU (${GPU_MEM}MB VRAM)"
            GPU_LAYERS=30
            THREADS=16
            BATCH_SIZE=256
        else
            echo "⚠️  GPU memory low (${GPU_MEM}MB), falling back to CPU"
            GPU_LAYERS=0
            THREADS=$(nproc)
            BATCH_SIZE=256
        fi
    else
        # CPU only fallback
        echo "🔧 Detected: CPU only mode"
        GPU_LAYERS=0
        THREADS=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 8)
        BATCH_SIZE=256
    fi

    echo "   GPU Layers: ${GPU_LAYERS} | Threads: ${THREADS} | Batch: ${BATCH_SIZE} | Context: ${CTX}"
    echo ""
}

# ============================================================
# Run inference
# ============================================================
run_model() {
    local prompt_arg=""
    if [ -n "$PROMPT" ]; then
        prompt_arg="--prompt \"$PROMPT\""
    fi

    local tensor_arg=""
    if [ -n "$TENSOR_SPLIT" ]; then
        tensor_arg="--tensor-split ${TENSOR_SPLIT}"
    fi

    eval python3 "${SCRIPT_DIR}/run_longshu.py" \
        --model-path "${MODEL_PATH}" \
        --n-gpu-layers ${GPU_LAYERS} \
        --threads ${THREADS} \
        --batch-size ${BATCH_SIZE} \
        --n-ctx ${CTX} \
        ${tensor_arg} \
        ${prompt_arg}
}

# ============================================================
# Main
# ============================================================
detect_hardware
run_model
