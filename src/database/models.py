"""Database models for the application."""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.session import Base


class UberTrip(Base):
    """Model for storing Uber trip data from CSV."""
    
    __tablename__ = "uber_trips"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Date and Time
    date = Column(DateTime, index=True)  # Combined Date+Time from CSV
    time = Column(String)  # Time as string from CSV
    
    # Identifiers
    booking_id = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(String, index=True)
    
    # Booking Details
    booking_status = Column(String, index=True)  # Success, Canceled by Driver, Canceled by Customer, Driver Not Found
    vehicle_type = Column(String, index=True)  # Prime Sedan, Bike, Prime SUV, eBike, Mini, Auto, Prime Plus
    
    # Locations
    pickup_location = Column(String, index=True)
    drop_location = Column(String, index=True)
    
    # Turnaround Times (can be null)
    v_tat = Column(Integer, nullable=True)  # Vehicle Turnaround Time
    c_tat = Column(Integer, nullable=True)  # Customer Turnaround Time
    
    # Cancellation Details (can be null)
    canceled_rides_by_customer = Column(Text, nullable=True)  # Cancellation reason
    canceled_rides_by_driver = Column(Text, nullable=True)  # Cancellation reason
    
    # Incomplete Rides (can be null)
    incomplete_rides = Column(String, nullable=True)  # Yes/No
    incomplete_rides_reason = Column(Text, nullable=True)
    
    # Financial
    booking_value = Column(Float, nullable=True, index=True)  # Fare amount
    payment_method = Column(String, index=True, nullable=True)  # Cash, UPI, Credit Card
    
    # Ride Details
    ride_distance = Column(Integer, nullable=True, index=True)  # Distance in km (0 for canceled rides)
    
    # Ratings (can be null)
    driver_ratings = Column(Float, nullable=True)
    customer_rating = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_date_status', 'date', 'booking_status'),
        Index('idx_vehicle_status', 'vehicle_type', 'booking_status'),
        Index('idx_customer_date', 'customer_id', 'date'),
        Index('idx_pickup_drop', 'pickup_location', 'drop_location'),
    )


class Session(Base):
    """Model for storing chat sessions."""
    
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to messages
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """Model for storing individual chat messages."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.session_id"), index=True)
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to session
    session = relationship("Session", back_populates="messages")

