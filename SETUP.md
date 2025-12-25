# Setup Instructions

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation Steps

1. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Copy `.env.example` to `.env` (if available) or create a `.env` file
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

4. **Create database directory**:
   ```bash
   mkdir -p database
   ```

5. **Run the application**:
   ```bash
   python -m src.main
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn src.main:app --reload
   ```

6. **Access the API**:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Next Steps

1. Place your Uber CSV file in the `data/` directory
2. Run the CSV analysis script to examine the data structure:
   ```bash
   python scripts/load_data.py data/uber_data.csv
   ```
3. After analyzing the CSV, we'll update the database schema accordingly

