"""Script to load CSV data into the database."""

import pandas as pd
import sys
import os
from datetime import datetime
from typing import Optional

# Add parent directory to path (use absolute path to avoid issues)
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.database.session import SessionLocal, engine
from src.database.models import Base, UberTrip


def parse_date_time(date_str: str, time_str: str) -> Optional[datetime]:
    """Parse date and time strings into datetime object."""
    try:
        # Date is already in format "2024-07-26 14:00:00"
        if pd.isna(date_str):
            return None
        # Parse the date string directly
        return pd.to_datetime(date_str)
    except Exception as e:
        print(f"Error parsing date/time: {date_str}, {time_str} - {e}")
        return None


def clean_value(value, default=None):
    """Clean and convert values, handling nulls and empty strings."""
    if pd.isna(value) or value == '' or value == 'null' or str(value).strip() == '':
        return default
    return value


def load_csv_to_database(csv_path: str, batch_size: int = 1000):
    """
    Load CSV data into the database.
    
    Args:
        csv_path: Path to the CSV file
        batch_size: Number of records to insert per batch
    """
    # Create tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Read CSV
    print(f"Reading CSV file: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f"CSV shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Columns: {df.columns.tolist()}")
    
    # Remove empty last column if it exists
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Get database session
    db = SessionLocal()
    
    try:
        total_rows = len(df)
        inserted = 0
        skipped = 0
        
        print(f"\nStarting data load...")
        
        for idx, row in df.iterrows():
            try:
                # Parse date
                date_obj = parse_date_time(row.get('Date'), row.get('Time'))
                
                # Create UberTrip object
                trip = UberTrip(
                    date=date_obj,
                    time=str(row.get('Time', '')),
                    booking_id=str(row.get('Booking_ID', '')),
                    customer_id=str(row.get('Customer_ID', '')),
                    booking_status=clean_value(row.get('Booking_Status')),
                    vehicle_type=clean_value(row.get('Vehicle_Type')),
                    pickup_location=clean_value(row.get('Pickup_Location')),
                    drop_location=clean_value(row.get('Drop_Location')),
                    v_tat=int(row['V_TAT']) if pd.notna(row.get('V_TAT')) and str(row.get('V_TAT')).lower() != 'null' else None,
                    c_tat=int(row['C_TAT']) if pd.notna(row.get('C_TAT')) and str(row.get('C_TAT')).lower() != 'null' else None,
                    canceled_rides_by_customer=clean_value(row.get('Canceled_Rides_by_Customer')),
                    canceled_rides_by_driver=clean_value(row.get('Canceled_Rides_by_Driver')),
                    incomplete_rides=clean_value(row.get('Incomplete_Rides')),
                    incomplete_rides_reason=clean_value(row.get('Incomplete_Rides_Reason')),
                    booking_value=float(row['Booking_Value']) if pd.notna(row.get('Booking_Value')) and str(row.get('Booking_Value')).lower() != 'null' else None,
                    payment_method=clean_value(row.get('Payment_Method')),
                    ride_distance=int(row['Ride_Distance']) if pd.notna(row.get('Ride_Distance')) and str(row.get('Ride_Distance')).lower() != 'null' else None,
                    driver_ratings=float(row['Driver_Ratings']) if pd.notna(row.get('Driver_Ratings')) and str(row.get('Driver_Ratings')).lower() != 'null' else None,
                    customer_rating=float(row['Customer_Rating']) if pd.notna(row.get('Customer_Rating')) and str(row.get('Customer_Rating')).lower() != 'null' else None,
                )
                
                db.add(trip)
                inserted += 1
                
                # Commit in batches
                if inserted % batch_size == 0:
                    db.commit()
                    print(f"Processed {inserted}/{total_rows} rows...")
                    
            except Exception as e:
                skipped += 1
                if skipped <= 10:  # Print first 10 errors
                    print(f"Error processing row {idx}: {e}")
                    print(f"Row data: {row.get('Booking_ID', 'N/A')}")
                db.rollback()
                continue
        
        # Final commit
        db.commit()
        print(f"\n✅ Data load complete!")
        print(f"   Inserted: {inserted} rows")
        print(f"   Skipped: {skipped} rows")
        print(f"   Total: {total_rows} rows")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during data load: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load CSV data into database")
    parser.add_argument("csv_path", help="Path to the CSV file")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size for inserts (default: 1000)")
    args = parser.parse_args()
    
    load_csv_to_database(args.csv_path, batch_size=args.batch_size)

