"""
LLM response generation.
TODO: Connect to your RunPod-hosted LLM.
"""

import os


class Generator:
    def __init__(self):
        self.runpod_url = os.getenv("RUNPOD_API_URL", "")
        self.runpod_key = os.getenv("RUNPOD_API_KEY", "")

    def generate(self, question: str, context_chunks: list[str]) -> str:
        """Generate an answer using the LLM with retrieved context."""
        context = "\n\n".join(context_chunks)

        prompt = f"""You are a helpful study assistant. Answer the question based ONLY on the provided context from lecture notes.

Context:
{context}

Question: {question}

Answer:"""

        # TODO: Call your RunPod-hosted LLM endpoint
        # Example with requests:
        # response = requests.post(
        #     self.runpod_url,
        #     headers={"Authorization": f"Bearer {self.runpod_key}"},
        #     json={"prompt": prompt, "max_tokens": 512}
        # )
        # return response.json()["output"]

        return f"[LLM not connected] Received question: '{question}' with {len(context_chunks)} context chunks."
