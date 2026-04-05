"""
One-time script to export the sentence-transformers model to ONNX format.

Run locally:
    pip install optimum[exporters] transformers
    python backend/scripts/export_model.py
"""

from optimum.exporters.onnx import main_export

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
OUTPUT_DIR = "backend/model/all-MiniLM-L6-v2-onnx"

if __name__ == "__main__":
    main_export(model_name_or_path=MODEL_ID, output=OUTPUT_DIR, task="feature-extraction")
    print(f"Model exported to {OUTPUT_DIR}")
