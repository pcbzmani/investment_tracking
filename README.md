# Expense & Income Tracker

A personal finance application built with Streamlit and Pandas.

## Features
- **Privacy First**: Stateless architecture ensures NO data is stored on the server. Your data stays on your device.
- **Track Finances**: Record Income and Expenses with categories.
- **Monthly Data Management**: Upload your monthly Excel file, make edits, and download the updated version.
- **Analytics Dashboard**: View spending trends, category breakdowns, and key metrics.
- **Power BI Ready**: Data remains in standard Excel format for external dashboards.

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
