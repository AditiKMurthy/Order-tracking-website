# How the bot talks to Qdrant.
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import os
from dotenv import load_dotenv

# Load environment variables from project root
env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=env_path)

# Get Qdrant configuration from environment
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or None
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "company_policies")

# Initialize Qdrant client with optional API key
client = QdrantClient(
    host=QDRANT_HOST, 
    port=QDRANT_PORT,
    api_key=QDRANT_API_KEY
)

def simple_embedding(text: str):
    """Generates simple, deterministic mock vector embeddings based on text hashes."""
    vec = [0.0] * 32
    for i, char in enumerate(text[:32]):
        vec[i] = float(ord(char)) / 100.0
    # Fill remaining spots if text is shorter than 32 chars
    for i in range(len(text[:32]), 32):
        vec[i] = float(i) / 32.0
    return vec

def init_and_seed_vector_db():
    # Recreate the collection
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=32, distance=Distance.COSINE),
    )
    
    support_email = os.getenv("SUPPORT_EMAIL", "support@omnistream.com")
    
    policies = [
        {"id": 1, "text": "Our shipping policy: Normal orders take 3 days to deliver once status is PROCESSED."},
        {"id": 2, "text": "Our returns policy: Items can be returned within 30 days of receiving them."},
        {"id": 3, "text": f"Support contact policy: Reach us at {support_email} for logistics escalation."}
    ]
    
    points = []
    for policy in policies:
        points.append(PointStruct(
            id=policy["id"],
            vector=simple_embedding(policy["text"]),
            payload={"policy": policy["text"]}
        ))
        
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print("Vector Store successfully seeded with company policies.")

if __name__ == "__main__":
    init_and_seed_vector_db()