"""
One-time script to export the sentence-transformers model to ONNX format.

Run locally:
    pip install optimum[onnxruntime] transformers torch
    optimum-cli export onnx --model sentence-transformers/all-MiniLM-L6-v2 --task feature-extraction backend/model/all-MiniLM-L6-v2-onnx

Or just run this command directly in your terminal — no Python script needed.
"""

print("Run this command in your terminal instead:")
print()
print("  optimum-cli export onnx --model sentence-transformers/all-MiniLM-L6-v2 --task feature-extraction backend/model/all-MiniLM-L6-v2-onnx")
