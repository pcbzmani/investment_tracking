# Expense & Income Tracker

A personal finance application built with Streamlit and Pandas.

## Features
- **Google Sheets Backend**: Data is saved immediately to the cloud. Access it from your mobile device via the Google Sheets app.
- **Track Finances**: Record Income and Expenses with categories.
- **Analytics Dashboard**: View spending trends, category breakdowns, and key metrics.
- **Dynamic Filters**: Drill down by Date Range and Category.
- **Power BI Ready**: Connect Power BI directly to the Google Sheet.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/pcbzmani/investment_tracking.git
    cd investment_tracking
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Run the application:
    ```bash
    streamlit run app.py
    ```

## Usage
- Open the app in your browser at `http://localhost:8501`.
- Go to **Data Entry** to add new transactions.
- Go to **Analytics** to view charts and insights.

## Technologies
- Python
- Streamlit
- Pandas
- OpenPyXL
