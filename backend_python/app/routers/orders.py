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
    kafka_kwargs = {
        "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        "value_serializer": lambda v: json.dumps(v).encode('utf-8')
    }
    
    # Check for SASL configuration (optional, for Cloud Kafka)
    sasl_mechanism = os.getenv("KAFKA_SASL_MECHANISM")
    if sasl_mechanism:
        kafka_kwargs["security_protocol"] = os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_SSL")
        kafka_kwargs["sasl_mechanism"] = sasl_mechanism
        kafka_kwargs["sasl_plain_username"] = os.getenv("KAFKA_SASL_USERNAME")
        kafka_kwargs["sasl_plain_password"] = os.getenv("KAFKA_SASL_PASSWORD")
        
    producer = KafkaProducer(**kafka_kwargs)
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
    else:
        # Simulate local background processing without Kafka/Java Engine
        from datetime import datetime, timedelta
        new_order.status = "PROCESSED"
        new_order.delivery_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        db.commit()
        db.refresh(new_order)

    return new_order

@router.get("/{order_id}")
def get_order_status(order_id: int, db: Session = Depends(get_db)):
    # Feature 4: Speed Layer Lookup (Resilient)
    try:
        cached_status = redis_client.get(f"order:status:{order_id}")
        cached_date = redis_client.get(f"order:delivery:{order_id}")
    except Exception:
        cached_status = None
        cached_date = None
    
    if cached_status:
        return {
            "order_id": order_id,
            "status": cached_status,
            "delivery_date": cached_date,
            "source": "Speed Layer (Redis Cache)"
        }

    # Fallback to Core Database
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    return {
        "order_id": order.id,
        "status": order.status,
        "delivery_date": order.delivery_date,
        "source": "Core Database"
    }