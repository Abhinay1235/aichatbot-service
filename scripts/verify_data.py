"""Script to verify loaded data in the database."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.session import SessionLocal
from src.database.models import UberTrip
from sqlalchemy import func


def verify_data():
    """Verify and display statistics about loaded data."""
    db = SessionLocal()
    
    try:
        # Total count
        total_count = db.query(func.count(UberTrip.id)).scalar()
        print(f"📊 Total trips in database: {total_count:,}")
        
        if total_count == 0:
            print("\n⚠️  No data found. Please run: python scripts/load_data.py data/uber_data.csv")
            return
        
        # Booking status breakdown
        print("\n📈 Booking Status Breakdown:")
        status_counts = db.query(
            UberTrip.booking_status,
            func.count(UberTrip.id).label('count')
        ).group_by(UberTrip.booking_status).all()
        
        for status, count in status_counts:
            percentage = (count / total_count) * 100
            print(f"   {status}: {count:,} ({percentage:.1f}%)")
        
        # Vehicle type breakdown
        print("\n🚗 Vehicle Type Breakdown:")
        vehicle_counts = db.query(
            UberTrip.vehicle_type,
            func.count(UberTrip.id).label('count')
        ).group_by(UberTrip.vehicle_type).all()
        
        for vehicle, count in vehicle_counts:
            percentage = (count / total_count) * 100
            print(f"   {vehicle}: {count:,} ({percentage:.1f}%)")
        
        # Date range
        date_range = db.query(
            func.min(UberTrip.date).label('min_date'),
            func.max(UberTrip.date).label('max_date')
        ).first()
        
        if date_range and date_range.min_date:
            print(f"\n📅 Date Range:")
            print(f"   From: {date_range.min_date}")
            print(f"   To: {date_range.max_date}")
        
        # Financial stats
        financial_stats = db.query(
            func.sum(UberTrip.booking_value).label('total_revenue'),
            func.avg(UberTrip.booking_value).label('avg_booking'),
            func.count(UberTrip.id).label('paid_rides')
        ).filter(UberTrip.booking_value.isnot(None)).first()
        
        if financial_stats and financial_stats.total_revenue:
            print(f"\n💰 Financial Statistics:")
            print(f"   Total Revenue: ₹{financial_stats.total_revenue:,.2f}")
            print(f"   Average Booking Value: ₹{financial_stats.avg_booking:,.2f}")
            print(f"   Paid Rides: {financial_stats.paid_rides:,}")
        
        # Distance stats
        distance_stats = db.query(
            func.avg(UberTrip.ride_distance).label('avg_distance'),
            func.max(UberTrip.ride_distance).label('max_distance'),
            func.min(UberTrip.ride_distance).label('min_distance')
        ).filter(UberTrip.ride_distance.isnot(None), UberTrip.ride_distance > 0).first()
        
        if distance_stats and distance_stats.avg_distance:
            print(f"\n📏 Distance Statistics:")
            print(f"   Average Distance: {distance_stats.avg_distance:.1f} km")
            print(f"   Max Distance: {distance_stats.max_distance} km")
            print(f"   Min Distance: {distance_stats.min_distance} km")
        
        print("\n✅ Database verification complete!")
        
    except Exception as e:
        print(f"\n❌ Error verifying data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    verify_data()

