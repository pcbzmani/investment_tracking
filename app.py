import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- Configuration ---
# Columns must match your Google Sheet exactly or will be created
COLUMNS = ['Date', 'Type', 'Category', 'Description', 'Mode', 'Amount']

# --- App UI ---
st.set_page_config(page_title="Expense & Income Tracker", layout="centered", page_icon="💰")
st.title("💰 Expense & Income Tracker")

# --- Google Sheets Connection ---
# Helper function to get data
def get_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        # Read data, evaluate strings to real types if needed (though read() usually handles basic types)
        df = conn.read()
        return df
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return pd.DataFrame(columns=COLUMNS)

def update_data(df):
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        conn.update(data=df)
        st.success("Data updated successfully in Google Drive!")
        st.cache_data.clear() # Clear cache to refresh data on next load
    except Exception as e:
        st.error(f"Error updating Google Sheets: {e}")

# --- Helper to ensure columns exist ---
try:
    current_df = get_data()
    # If using a blank sheet, columns might not exist. Ensure at least header exists.
    # Note: st-gsheets-connection read() might return empty or just headers.
    # We will enforce schema locally before saving back if it's empty.
    if current_df.empty and set(current_df.columns) != set(COLUMNS):
         current_df = pd.DataFrame(columns=COLUMNS)
except:
    current_df = pd.DataFrame(columns=COLUMNS)

# Ensure Date is datetime
if not current_df.empty and 'Date' in current_df.columns:
    current_df['Date'] = pd.to_datetime(current_df['Date'])

# Create Tabs
tab1, tab2 = st.tabs(["📝 Data Entry", "📊 Analytics"])

with tab1:
    st.subheader("Add Transaction")
    
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            date_input = st.date_input("Date", datetime.today())
            transaction_type = st.selectbox("Transaction Type", ["Income", "Expense"])
            
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
                new_entry = {
                    "Date": pd.to_datetime(date_input),
                    "Type": transaction_type,
                    "Category": category,
                    "Description": description,
                    "Mode": mode,
                    "Amount": amount
                }
                # Append to current dataframe
                updated_df = pd.concat([current_df, pd.DataFrame([new_entry])], ignore_index=True)
                
                # Update Google Sheet
                update_data(updated_df)
                st.rerun()
            else:
                st.warning("Please enter a valid amount.")

    st.divider()
    st.subheader("Manage Transactions")

    if not current_df.empty:
        # Display transactions
        display_df = current_df.copy()
        display_df['Date'] = display_df['Date'].dt.date
        st.dataframe(display_df, use_container_width=True)
        
        # Delete Section
        st.caption("Delete a Record")
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            options = display_df.apply(lambda x: f"{x.name}: {x['Date']} - {x['Category']} - {x['Amount']}", axis=1)
            selected_indices = st.multiselect("Select records to delete:", options.index, format_func=lambda x: options[x])
        
        with col_del2:
            st.write("") 
            st.write("") 
            if st.button("Delete Selected"):
                if selected_indices:
                    updated_df = current_df.drop(selected_indices).reset_index(drop=True)
                    update_data(updated_df)
                    st.rerun()
                else:
                    st.warning("Select records first.")
    else:
        st.info("No records found. Add a new transaction above!")

with tab2:
    st.subheader("Financial Analytics")
    
    data = current_df.copy()
    
    if not data.empty:
        # Ensure Date is datetime
        data['Date'] = pd.to_datetime(data['Date'])
        
        # --- Sidebar Filters ---
        st.sidebar.divider()
        st.sidebar.header("Analytics Filters")
        
        min_date = data['Date'].min()
        max_date = data['Date'].max()
        
        if pd.isnull(min_date) or pd.isnull(max_date):
            filtered_data = data
        else:
            start_date, end_date = st.sidebar.date_input(
                "Select Date Range",
                [min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )
            filtered_data = data[
                (data['Date'] >= pd.to_datetime(start_date)) & 
                (data['Date'] <= pd.to_datetime(end_date))
            ]
        
        # Category Filter
        all_categories = ["All"] + list(data['Category'].unique())
        selected_category = st.sidebar.selectbox("Select Category", all_categories)
        
        if selected_category != "All":
            filtered_data = filtered_data[filtered_data['Category'] == selected_category]
        
        if not filtered_data.empty:
            # Metrics
            total_income = filtered_data[filtered_data['Type'] == 'Income']['Amount'].sum()
            total_expense = filtered_data[filtered_data['Type'] == 'Expense']['Amount'].sum()
            net_balance = total_income - total_expense
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Income", f"₹{total_income:,.2f}")
            m2.metric("Total Expense", f"₹{total_expense:,.2f}")
            m3.metric("Net Balance", f"₹{net_balance:,.2f}")
            
            st.divider()

            # Charts
            expense_data = filtered_data[filtered_data['Type'] == 'Expense']
            if not expense_data.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.caption("Expenses by Category")
                    st.bar_chart(expense_data.groupby('Category')['Amount'].sum().sort_values(ascending=False))
                with c2:
                    st.caption("Expenses by Mode")
                    st.bar_chart(expense_data.groupby('Mode')['Amount'].sum(), horizontal=True)
                
                st.subheader("Spending Trend")
                st.line_chart(expense_data.groupby('Date')['Amount'].sum())
            else:
                st.info("No expenses found for selection.")
        else:
             st.info("No data matches the filters.")
    else:
        st.info("Add transactions to see analytics.")

# Note: No 'Download' button needed as data maps directly to Google Sheets, providing a better UI there.
