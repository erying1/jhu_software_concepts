#!/usr/bin/env python3
"""Test if llama-cpp-python is using CUDA"""

import os
import sys

print("=" * 60)
print("CUDA Setup Verification for llama-cpp-python")
print("=" * 60)

# Check if llama_cpp is installed
try:
    from llama_cpp import Llama
    print("✓ llama-cpp-python is installed")
except ImportError:
    print("✗ llama-cpp-python is NOT installed")
    print("\nPlease install with CUDA support:")
    print("  Windows: Set CMAKE_ARGS=-DGGML_CUDA=on")
    print("  Then: pip install llama-cpp-python --force-reinstall --no-cache-dir")
    sys.exit(1)

# Check for CUDA libraries
try:
    import llama_cpp
    # Try to find CUDA-related attributes
    has_cuda = False
    
    # Check module attributes for CUDA support indicators
    module_attrs = dir(llama_cpp)
    cuda_indicators = [attr for attr in module_attrs if 'cuda' in attr.lower() or 'gpu' in attr.lower()]
    
    if cuda_indicators:
        print(f"✓ Found CUDA-related attributes: {cuda_indicators}")
        has_cuda = True
    
    print(f"\nCUDA Support: {'✓ YES' if has_cuda else '? UNKNOWN - will test during model load'}")
    
except Exception as e:
    print(f"! Warning checking CUDA: {e}")

# Check if model file exists
MODEL_PATH = "module_3/module_2.1/llm_hosting/models/tinyllama-1.1b-chat-v1.0.Q3_K_M.gguf"
if os.path.exists(MODEL_PATH):
    print(f"✓ Model file found: {MODEL_PATH}")
    
    print("\n" + "=" * 60)
    print("Testing model load with GPU layers...")
    print("=" * 60)
    
    try:
        # Try loading with GPU layers
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=512,
            n_threads=4,
            n_gpu_layers=35,  # All layers for TinyLlama
            verbose=True
        )
        
        print("\n✓ Model loaded successfully!")
        print("\nLook for 'CUDA' or 'GPU' in the output above.")
        print("If you see 'CUDA buffer size' messages, GPU is working! 🎉")
        
        # Try a simple inference
        print("\n" + "=" * 60)
        print("Testing inference...")
        print("=" * 60)
        
        response = llm("Hello, ", max_tokens=10)
        print(f"✓ Inference successful: {response['choices'][0]['text']}")
        
    except Exception as e:
        print(f"\n✗ Error loading model: {e}")
        print("\nThis might mean CUDA support wasn't compiled in.")
        print("Try reinstalling with: CMAKE_ARGS=-DGGML_CUDA=on pip install llama-cpp-python --force-reinstall")
        
else:
    print(f"✗ Model file NOT found: {MODEL_PATH}")
    print("  Please download the model first")

print("\n" + "=" * 60)
print("Verification complete")
print("=" * 60)
