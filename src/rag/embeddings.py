from google import genai
from google.genai import types
from typing import List, Optional
import numpy as np
from src.config import settings
import os

class GeminiEmbeddings:
    
    SUPPORTED_DIMENSIONS = [128, 256, 512, 768, 1024, 1536, 2048, 3072]
    DEFAULT_DIMENSION = 768
    NORMALIZE_DIMENSIONS = [128, 256, 512, 768, 1024, 1536, 2048]
    
    def __init__(self, output_dimensionality: int = DEFAULT_DIMENSION):
        if output_dimensionality not in self.SUPPORTED_DIMENSIONS:
            raise ValueError(
                f"output_dimensionality must be one of {self.SUPPORTED_DIMENSIONS}, "
                f"got {output_dimensionality}"
            )
        key = settings.GOOGLE_API_KEY
        self.client = genai.Client(api_key=key)
        self.model_name = "gemini-embedding-001"
        self.output_dimensionality = output_dimensionality
    
    def _normalize_embedding(self, embedding: List[float]) -> List[float]:
        
        embedding_array = np.array(embedding)
        norm = np.linalg.norm(embedding_array)
        if norm == 0:
            return embedding
        return (embedding_array / norm).tolist()
    
    def embed_documents(
        self,
        texts: List[str],
        task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> List[List[float]]:
        
        if not texts:
            raise ValueError("texts list cannot be empty")
        
        embeddings = []
        
        try:
            result = self.client.models.embed_content(
                model=self.model_name,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=self.output_dimensionality
                )
            )
            
            # Extract embeddings and normalize if necessary
            for embedding_obj in result.embeddings:
                embedding_values = embedding_obj.values
                
                # Normalize for non-3072 dimensions
                if self.output_dimensionality in self.NORMALIZE_DIMENSIONS:
                    embedding_values = self._normalize_embedding(embedding_values)
                
                embeddings.append(embedding_values)
            
            return embeddings
            
        except Exception as e:
            raise RuntimeError(f"Error embedding documents: {e}")
    
    def embed_query(
        self,
        text: str,
        task_type: str = "RETRIEVAL_QUERY"
    ) -> List[float]:
        
        if not text or not text.strip():
            raise ValueError("text cannot be empty")
        
        try:
            result = self.client.models.embed_content(
                model=self.model_name,
                contents=[text],
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=self.output_dimensionality
                )
            )
            
            embedding_values = result.embeddings[0].values
            
            # Normalize for non-3072 dimensions
            if self.output_dimensionality in self.NORMALIZE_DIMENSIONS:
                embedding_values = self._normalize_embedding(embedding_values)
            
            return embedding_values
            
        except Exception as e:
            raise RuntimeError(f"Error embedding query: {e}")
    
    def embed_for_semantic_similarity(self, texts: List[str]) -> List[List[float]]:
        
        return self.embed_documents(texts, task_type="SEMANTIC_SIMILARITY")
    
    def embed_for_classification(self, texts: List[str]) -> List[List[float]]:
        
        return self.embed_documents(texts, task_type="CLASSIFICATION")
    
    def embed_for_clustering(self, texts: List[str]) -> List[List[float]]:
        
        return self.embed_documents(texts, task_type="CLUSTERING")


def get_embeddings(
    output_dimensionality: int = GeminiEmbeddings.DEFAULT_DIMENSION
) -> GeminiEmbeddings:
    
    return GeminiEmbeddings(output_dimensionality=output_dimensionality)