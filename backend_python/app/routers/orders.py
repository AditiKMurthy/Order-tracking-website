from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
import os
from dotenv import load_dotenv
import redis
from kafka import KafkaProducer
from ..database import get_db
from ..models import Order
from ..schemas import OrderCreate, OrderResponse
from .auth import get_current_user
from ..models import User

# Load environment variables
load_dotenv()

router = APIRouter(tags=["Orders"])

# Speed Layer (Redis Connection)
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"), 
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    password=os.getenv("REDIS_PASSWORD") or None,
    decode_responses=True
)

# Pipeline Layer (Kafka Producer Connection)
try:
    producer = KafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
except Exception as e:
    print(f"Warning: Kafka initialization failed: {e}")
    producer = None # Graceful degraded mode if kafka initialization fails on boot

@router.post("/", response_model=OrderResponse)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Save to Database (Pending State)
    new_order = Order(
        item_name=order_data.item_name,
        destination=order_data.destination,
        status="PENDING",
        user_id=current_user.id
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # 2. Push Event onto Kafka Pipeline
    if producer:
        event_payload = {
            "order_id": new_order.id,
            "item_name": new_order.item_name,
            "destination": new_order.destination
        }
        producer.send('order-events', value=event_payload)
        producer.flush()

    return new_order

@router.get("/{order_id}")
def get_order_status(order_id: int, db: Session = Depends(get_db)):
    # Feature 4: Speed Layer Lookup
    cached_status = redis_client.get(f"order:status:{order_id}")
    cached_date = redis_client.get(f"order:delivery:{order_id}")
    
    if cached_status:
        return {
            "order_id": order_id,
            "status": cached_status,
            "delivery_date": cached_date,
            "source": "Speed Layer (Redis Cache)"
        }

    # Fallback to PostgreSQL
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    return {
        "order_id": order.id,
        "status": order.status,
        "delivery_date": order.delivery_date,
        "source": "Core Database (Postgres)"
    }