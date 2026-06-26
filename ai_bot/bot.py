# The LLM interaction logic.
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

# Load environment variables from project root
env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=env_path)

# Core Application Imports
from backend_python.app.database import get_db
from backend_python.app.models import Order

# Absolute import from the workspace root level
from ai_bot.vector_store import simple_embedding, COLLECTION_NAME, client as qdrant_client

router = APIRouter(prefix="/bot", tags=["Smart Support Bot"])

@router.get("/ask")
def ask_bot(query: str, order_id: int, db: Session = Depends(get_db)):
    # 1. Look up data inside transactional DB
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order tracking record not found")

    # 2. Extract relative semantic documents from Vector Store
    query_vector = simple_embedding(query)
    search_results = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=1
    )
    
    policy_context = search_results[0].payload["policy"] if search_results else "No relevant context found."

    # 3. Augment data and return simulated structured prompt context answer
    response_msg = (
        f"Hello! Regarding your order {order.id} status tracking for item '{order.item_name}': "
        f"Your current status is {order.status} with expected delivery date: {order.delivery_date}. "
        f"According to company standard documentation context rules: '{policy_context}'"
    )
    
    return {
        "user_query": query,
        "resolved_answer": response_msg
    }