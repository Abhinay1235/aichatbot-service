# Uber Data Schema Documentation

## CSV Structure Analysis

The Uber CSV file contains **103,026 rows** of trip data with the following structure:

### Columns

1. **Date** - DateTime (format: "2024-07-26 14:00:00")
2. **Time** - Time string (format: "14:00:00")
3. **Booking_ID** - String (unique identifier, e.g., "CNR7153255142")
4. **Booking_Status** - String (Success, Canceled by Driver, Canceled by Customer, Driver Not Found)
5. **Customer_ID** - String (e.g., "CID713523")
6. **Vehicle_Type** - String (Prime Sedan, Bike, Prime SUV, eBike, Mini, Auto, Prime Plus)
7. **Pickup_Location** - String (location name)
8. **Drop_Location** - String (location name)
9. **V_TAT** - Integer (Vehicle Turnaround Time in minutes, nullable)
10. **C_TAT** - Integer (Customer Turnaround Time in minutes, nullable)
11. **Canceled_Rides_by_Customer** - Text (cancellation reason, nullable)
12. **Canceled_Rides_by_Driver** - Text (cancellation reason, nullable)
13. **Incomplete_Rides** - String (Yes/No, nullable)
14. **Incomplete_Rides_Reason** - Text (reason for incomplete ride, nullable)
15. **Booking_Value** - Float (fare amount in currency, nullable)
16. **Payment_Method** - String (Cash, UPI, Credit Card, nullable)
17. **Ride_Distance** - Integer (distance in km, 0 for canceled rides, nullable)
18. **Driver_Ratings** - Float (rating out of 5, nullable)
19. **Customer_Rating** - Float (rating out of 5, nullable)
20. **Vehicle Images** - String (appears to be empty/error in CSV)

## Database Schema

### Table: `uber_trips`

All columns from CSV are mapped to database columns with appropriate data types and indexes.

#### Key Indexes Created:
- `booking_id` - Unique index for fast lookups
- `date` - Index for time-based queries
- `booking_status` - Index for filtering by status
- `vehicle_type` - Index for vehicle type queries
- `customer_id` - Index for customer-specific queries
- `pickup_location`, `drop_location` - Indexes for location queries
- `booking_value` - Index for financial analysis
- `ride_distance` - Index for distance-based queries
- Composite indexes:
  - `idx_date_status` - For queries filtering by date and status
  - `idx_vehicle_status` - For vehicle type and status analysis
  - `idx_customer_date` - For customer history queries
  - `idx_pickup_drop` - For route analysis

## Query Patterns Supported

The chatbot can answer questions about:

### 1. **Booking Statistics**
- Total bookings
- Successful vs canceled bookings
- Booking status distribution
- Booking trends over time

### 2. **Vehicle Analysis**
- Bookings by vehicle type
- Revenue by vehicle type
- Popular vehicle types
- Vehicle type performance

### 3. **Location Analysis**
- Most popular pickup/drop locations
- Busiest routes
- Location-based revenue
- Distance analysis

### 4. **Financial Analysis**
- Total revenue
- Average booking value
- Revenue by payment method
- Revenue trends

### 5. **Customer Analysis**
- Customer booking history
- Customer ratings
- Customer cancellation patterns

### 6. **Performance Metrics**
- Average ride distance
- Average turnaround times (V_TAT, C_TAT)
- Driver and customer ratings
- Incomplete ride analysis

### 7. **Cancellation Analysis**
- Cancellation rates
- Cancellation reasons
- Cancellations by customer vs driver
- Cancellation patterns by vehicle type/location

### 8. **Time-based Analysis**
- Bookings by date/time
- Peak hours
- Daily/weekly/monthly trends
- Seasonal patterns

## Example Queries

The chatbot will be able to handle questions like:
- "How many successful rides were there in July?"
- "What is the average booking value for Prime SUV?"
- "Which location has the most pickups?"
- "What percentage of rides were canceled?"
- "Show me the top 5 routes by distance"
- "What is the total revenue from UPI payments?"
- "Which vehicle type has the highest customer rating?"

## Data Quality Notes

- Some fields contain `null` values (especially for canceled/incomplete rides)
- `Ride_Distance` is 0 for canceled rides
- `Booking_Value` is null for canceled rides
- Ratings are null for canceled/incomplete rides
- The last column "Vehicle Images" appears to be empty/error in the CSV

