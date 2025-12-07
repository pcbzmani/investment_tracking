import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Configuration ---
# --- Configuration ---
# FILE_PATH = 'finance_tracker.xlsx' # Removed single file path
COLUMNS = ['Date', 'Type', 'Category', 'Description', 'Mode', 'Amount']

# --- Helper Functions ---
def get_file_path(year, month):
    """Returns the filename for a specific year and month."""
    return f'finance_tracker_{year}_{month:02d}.xlsx'

def load_data(year, month):
    """Loads data for a specific year and month."""
    file_path = get_file_path(year, month)
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            return df
        except Exception as e:
            st.error(f"Error loading file {file_path}: {e}")
            return pd.DataFrame(columns=COLUMNS)
    else:
        return pd.DataFrame(columns=COLUMNS)

def save_data(df, year, month):
    """Saves the DataFrame to the specific monthly file."""
    file_path = get_file_path(year, month)
    try:
        df.to_excel(file_path, index=False)
    except Exception as e:
        st.error(f"Error saving file {file_path}: {e}")

# --- App UI ---
st.set_page_config(page_title="Expense & Income Tracker", layout="centered", page_icon="💰")
st.title("💰 Expense & Income Tracker")

# --- Sidebar: Period Selector ---
st.sidebar.header("Select Period")
current_year = datetime.today().year
years = list(range(current_year - 1, current_year + 5))
selected_year = st.sidebar.selectbox("Year", years, index=years.index(current_year))
selected_month = st.sidebar.selectbox("Month", list(range(1, 13)), index=datetime.today().month - 1)

# Current file being viewed
current_file_path = get_file_path(selected_year, selected_month)

# Create Tabs
tab1, tab2 = st.tabs(["📝 Data Entry", "📊 Analytics"])

with tab1:
    st.subheader(f"Add Transaction")
    # --- Input Form ---
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            date_input = st.date_input("Date", datetime.today())
            transaction_type = st.selectbox("Transaction Type", ["Income", "Expense"])
            
            # Category options logic
            if transaction_type == "Income":
                category_options = ["Salary", "Other"]
            else:
                category_options = [
                    "Rent", "Groceries", "Laundry", "Mobile Recharge", 
                    "Entertainment", "Outside Food", "Taxi", "Miscellaneous"
                ]
            category = st.selectbox("Category", category_options)

        with col2:
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            mode = st.selectbox("Mode", ["Cash", "Card", "UPI"])
            description = st.text_input("Description")

        submitted = st.form_submit_button("Save Record")

        if submitted:
            if amount > 0:
                # 1. Determine target file based on INPUT DATE, not selected view
                target_year = date_input.year
                target_month = date_input.month
                
                # 2. Load existing data for that specific month
                df = load_data(target_year, target_month)
                
                # 3. Append new entry
                new_entry = {
                    "Date": pd.to_datetime(date_input),
                    "Type": transaction_type,
                    "Category": category,
                    "Description": description,
                    "Mode": mode,
                    "Amount": amount
                }
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                
                # 4. Save to the specific monthly file
                save_data(df, target_year, target_month)
                
                st.success(f"Entry saved to {get_file_path(target_year, target_month)}!")
                
                # Refresh if we are viewing the same month we just added to
                if target_year == selected_year and target_month == selected_month:
                    st.rerun()
            else:
                st.warning("Please enter a valid amount.")

    # --- Data Preview & Download ---
    st.divider()
    st.subheader(f"Manage Transactions ({datetime(selected_year, selected_month, 1).strftime('%B %Y')})")

    # Load data for the SELECTED period to view
    current_df = load_data(selected_year, selected_month)

    if not current_df.empty:
        # Format Date for display
        display_df = current_df.copy()
        display_df['Date'] = display_df['Date'].dt.date
        
        # Display transactions
        st.dataframe(display_df, use_container_width=True)
        
        # Delete Section
        st.caption("Delete a Record (from this month)")
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            options = display_df.apply(lambda x: f"{x.name}: {x['Date']} - {x['Category']} - {x['Amount']}", axis=1)
            selected_indices = st.multiselect("Select records to delete:", options.index, format_func=lambda x: options[x])
        
        with col_del2:
            st.write("") 
            st.write("") 
            if st.button("Delete Selected"):
                if selected_indices:
                    current_df = current_df.drop(selected_indices).reset_index(drop=True)
                    # Save back to specific file
                    save_data(current_df, selected_year, selected_month)
                    st.success("Records deleted successfully!")
                    st.rerun()
                else:
                    st.warning("Select records first.")

        # 3. Download Feature
        # Use current_file_path which was determined at the top
        if os.path.exists(current_file_path):
            with open(current_file_path, "rb") as f:
                st.download_button(
                    label=f"Download {os.path.basename(current_file_path)}",
                    data=f,
                    file_name=os.path.basename(current_file_path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.info(f"No records found for {datetime(selected_year, selected_month, 1).strftime('%B %Y')}.")

with tab2:
    st.subheader("Financial Analytics")
    
    # Use the same data loaded for the selected period
    data = current_df
    
    if not data.empty:
        # Ensure Date is datetime
        data['Date'] = pd.to_datetime(data['Date'])
        
        # --- Sidebar Filters for Analytics (Within the selected month) ---
        st.sidebar.divider()
        st.sidebar.header("Analytics Filters")
        
        # Category Filter
        all_categories = ["All"] + list(data['Category'].unique())
        selected_category = st.sidebar.selectbox("Select Category", all_categories)
        
        # Filter Data
        filtered_data = data.copy()
        
        if selected_category != "All":
            filtered_data = filtered_data[filtered_data['Category'] == selected_category]
        
        if not filtered_data.empty:
            # --- Key Metrics ---
            total_income = filtered_data[filtered_data['Type'] == 'Income']['Amount'].sum()
            total_expense = filtered_data[filtered_data['Type'] == 'Expense']['Amount'].sum()
            net_balance = total_income - total_expense
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Income", f"₹{total_income:,.2f}")
            m2.metric("Total Expense", f"₹{total_expense:,.2f}")
            m3.metric("Net Balance", f"₹{net_balance:,.2f}")
            
            st.divider()

            # --- Expense Analysis ---
            st.subheader("Expense Breakdown")
            
            # Filter only expenses
            expense_data = filtered_data[filtered_data['Type'] == 'Expense']
            
            if not expense_data.empty:
                c1, c2 = st.columns(2)
                
                with c1:
                    st.caption("Expenses by Category")
                    category_breakdown = expense_data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
                    st.bar_chart(category_breakdown)
                    
                with c2:
                    st.caption("Expenses by Mode")
                    mode_breakdown = expense_data.groupby('Mode')['Amount'].sum()
                    st.bar_chart(mode_breakdown, horizontal=True) 
                
                st.subheader("Spending Trend")
                # Daily Spending Trend
                daily_spending = expense_data.groupby('Date')['Amount'].sum()
                st.line_chart(daily_spending)
            
            else:
                st.info("No expenses found for the selected filters.")
        else:
            st.info("No data matches the selected filters.")

    else:
        st.info("Add some transactions in the 'Data Entry' tab to see analytics.")
