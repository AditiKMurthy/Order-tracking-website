# The "Shapes" in the database (PostgreSQL tables).
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    purpose = Column(String, nullable=False)  # "register" or "reset"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, PROCESSED
    delivery_date = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))