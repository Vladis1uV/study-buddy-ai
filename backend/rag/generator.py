"""
LLM response generation via RunPod Serverless (vLLM worker + Llama 3.1 8B Instruct).
"""

import os
import httpx

# Llama 3.1 chat template tokens
_SYS_HEADER = "<|start_header_id|>system<|end_header_id|>"
_USR_HEADER = "<|start_header_id|>user<|end_header_id|>"
_ASST_HEADER = "<|start_header_id|>assistant<|end_header_id|>"
_EOT = "<|eot_id|>"


class Generator:
    def __init__(self):
        self.api_key = os.getenv("RUNPOD_API_KEY", "")
        self.endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID", "")

    def _build_prompt(self, question: str, context: str) -> str:
        system = (
            "You are a helpful study assistant. "
            "Answer the question based ONLY on the provided context from lecture notes. "
            "If the context does not contain enough information, say so."
        )
        return (
            f"<|begin_of_text|>{_SYS_HEADER}\n\n"
            f"{system}{_EOT}"
            f"{_USR_HEADER}\n\n"
            f"Context:\n{context}\n\nQuestion: {question}{_EOT}"
            f"{_ASST_HEADER}\n\n"
        )

    def generate(self, question: str, context_chunks: list[str]) -> str:
        """Generate an answer using Llama 3.1 8B Instruct on RunPod Serverless."""
        context = "\n\n".join(context_chunks)
        prompt = self._build_prompt(question, context)

        url = f"https://api.runpod.ai/v2/{self.endpoint_id}/runsync"
        payload = {
            "input": {
                "prompt": prompt,
                "sampling_params": {
                    "max_tokens": 512,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "stop": [_EOT],
                },
            }
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = httpx.post(url, json=payload, headers=headers, timeout=120.0)
        if response.status_code != 200:
            raise RuntimeError(f"RunPod error {response.status_code}: {response.text}")

        data = response.json()
        try:
            full_text = data["output"][0]["choices"][0]["tokens"][0]
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(f"Unexpected RunPod response shape: {data}") from e

        # vLLM returns the full text (prompt + completion); extract only the assistant turn
        marker = f"{_ASST_HEADER}\n\n"
        if marker in full_text:
            return full_text.split(marker)[-1].strip()
        return full_text.strip()
