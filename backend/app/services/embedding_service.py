import chromadb
from chromadb.utils import embedding_functions
from app.config import settings
import os

# Ensure the vector store directory exists
CHROMA_DATA_PATH = "chroma_db"
os.makedirs(CHROMA_DATA_PATH, exist_ok=True)

# Initialize Persistent Client (Production-grade storage)
chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

# Use a local, free embedding model (No API key required)
default_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Get or create the 'complaints' collection
collection = chroma_client.get_or_create_collection(
    name="corruption_complaints",
    embedding_function=default_ef,
    metadata={"hnsw:space": "cosine"}  # Using Cosine similarity for better semantic matching
)


class EmbeddingService:
    @staticmethod
    async def index_complaint(complaint_id: int, text: str, metadata: dict):
        """Stores a complaint in the vector database."""
        collection.add(
            ids=[str(complaint_id)],
            documents=[text],
            metadatas=[metadata]
        )

    @staticmethod
    async def find_similar_cases(text: str, limit: int = 5, distance_threshold: float = 0.5):
        """Searches for semantically similar complaints."""
        results = collection.query(
            query_texts=[text],
            n_results=limit
        )

        # Filter results based on distance (closer to 0 is more similar)
        # We only return cases that are 'close enough'
        similar_cases = []
        if results['ids'][0]:
            for i in range(len(results['ids'][0])):
                if results['distances'][0][i] < distance_threshold:
                    similar_cases.append({
                        "id": results['ids'][0][i],
                        "distance": results['distances'][0][i],
                        "metadata": results['metadatas'][0][i]
                    })
        return similar_cases


embedding_service = EmbeddingService()