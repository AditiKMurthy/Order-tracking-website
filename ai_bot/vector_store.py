# How the bot talks to Qdrant.
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import os
from dotenv import load_dotenv

# Load environment variables from project root
env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=env_path)

# Get Qdrant configuration from environment
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or None
QDRANT_PATH = os.getenv("QDRANT_PATH")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "company_policies")

# Determine a local fallback path
DEFAULT_LOCAL_PATH = os.path.join(os.path.dirname(__file__), "data/qdrant_db")

# Initialize Qdrant client
if QDRANT_URL:
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
elif QDRANT_PATH:
    client = QdrantClient(
        path=QDRANT_PATH
    )
else:
    try:
        # Try connecting to the remote Qdrant service first
        client = QdrantClient(
            host=QDRANT_HOST, 
            port=QDRANT_PORT,
            api_key=QDRANT_API_KEY,
            timeout=2.0
        )
        # Verify connection by calling a fast API
        client.get_collections()
    except Exception:
        # Fall back to local SQLite-backed Qdrant database
        print(f"Warning: Could not connect to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}. "
              f"Falling back to local on-disk storage at {DEFAULT_LOCAL_PATH}")
        client = QdrantClient(
            path=DEFAULT_LOCAL_PATH
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