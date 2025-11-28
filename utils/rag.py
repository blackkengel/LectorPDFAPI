from openai import OpenAI
import numpy as np
from configuration.environments import OPENAI_API_KEY

class EmbeddingsClient:
    def __init__(self, model="text-embedding-3-small"):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no está configurada en environment.py")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model

    def embed(self, texts):
        embeddings = []
        for text in texts:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            embeddings.append(response.data[0].embedding)
        return np.array(embeddings, dtype="float32")


