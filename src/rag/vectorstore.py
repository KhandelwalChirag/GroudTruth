import os
import pickle
import faiss
import numpy as np
from typing import List, Dict, Tuple
from src.config import settings
from src.rag.embeddings import get_embeddings


class VectorStore:
    """FAISS-based vector store for document retrieval"""
    
    def __init__(self):
        self.embeddings = get_embeddings()
        self.index = None
        self.documents = []
        self.metadata = []
        self.dimension = 768  # Gemini embedding dimension
        
        # Try to load existing index
        self.load_index()
    
    def create_index(self, documents: List[str], metadata: List[Dict] = None):
        """
        Create a new FAISS index from documents
        
        Args:
            documents: List of text documents
            metadata: Optional metadata for each document
        """
        print(f"Creating vector index for {len(documents)} documents...")
        
        # Store documents and metadata
        self.documents = documents
        self.metadata = metadata if metadata else [{} for _ in documents]
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = self.embeddings.embed_documents(documents)
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings_array)
        
        print(f"Index created with {self.index.ntotal} vectors")
        
        # Save index
        self.save_index()
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query: Query string
            top_k: Number of results to return
        
        Returns:
            List of dictionaries with document, metadata, and score
        """
        if self.index is None or self.index.ntotal == 0:
            print("Warning: Index is empty")
            return []
        
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        # Embed query
        query_embedding = self.embeddings.embed_query(query)
        query_vector = np.array([query_embedding]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_vector, top_k)
        
        # Format results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):  # Valid index
                results.append({
                    'document': self.documents[idx],
                    'metadata': self.metadata[idx],
                    'score': float(distance),
                    'rank': i + 1
                })
        
        return results
    
    def add_documents(self, documents: List[str], metadata: List[Dict] = None):
        """
        Add new documents to existing index
        
        Args:
            documents: List of text documents
            metadata: Optional metadata for each document
        """
        if not documents:
            return
        
        print(f"Adding {len(documents)} new documents...")
        
        # Generate embeddings
        embeddings = self.embeddings.embed_documents(documents)
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Add to index
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)
        
        self.index.add(embeddings_array)
        
        # Update documents and metadata
        self.documents.extend(documents)
        new_metadata = metadata if metadata else [{} for _ in documents]
        self.metadata.extend(new_metadata)
        
        print(f"Index now contains {self.index.ntotal} vectors")
        
        # Save updated index
        self.save_index()
    
    def save_index(self):
        """Save index to disk"""
        try:
            settings.VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            index_path = settings.VECTORSTORE_PATH / f"{settings.FAISS_INDEX_NAME}.index"
            faiss.write_index(self.index, str(index_path))
            
            # Save documents and metadata
            data_path = settings.VECTORSTORE_PATH / f"{settings.FAISS_INDEX_NAME}.pkl"
            with open(data_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'metadata': self.metadata
                }, f)
            
            print(f"Index saved to {settings.VECTORSTORE_PATH}")
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def load_index(self):
        """Load index from disk"""
        try:
            index_path = settings.VECTORSTORE_PATH / f"{settings.FAISS_INDEX_NAME}.index"
            data_path = settings.VECTORSTORE_PATH / f"{settings.FAISS_INDEX_NAME}.pkl"
            
            if index_path.exists() and data_path.exists():
                # Load FAISS index
                self.index = faiss.read_index(str(index_path))
                
                # Load documents and metadata
                with open(data_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.metadata = data['metadata']
                
                print(f"Loaded index with {self.index.ntotal} vectors")
                return True
        except Exception as e:
            print(f"Could not load existing index: {e}")
        
        return False
    
    def clear_index(self):
        """Clear the index"""
        self.index = None
        self.documents = []
        self.metadata = []
        print("Index cleared")


# Global vector store instance
_vectorstore = None

def get_vectorstore() -> VectorStore:
    """Get global vector store instance"""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = VectorStore()
    return _vectorstore