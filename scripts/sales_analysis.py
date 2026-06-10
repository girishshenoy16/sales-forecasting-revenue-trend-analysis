import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

def run_sales_analysis(raw_path, cleaned_path, js_output_path):
    print("Loading raw sales data...")
    df = pd.read_csv(raw_path)
    
    # 1. Data Cleaning & Validation
    print("Performing data validation and cleaning...")
    
    # Check shape and columns
    print(f"Loaded {len(df)} rows.")
    
    # Check for null values
    nulls = df.isnull().sum().sum()
    if nulls > 0:
        print(f"Warning: Found {nulls} missing values. Filling missing numeric values with 0...")
        df.fillna(0, inplace=True)
    else:
        print("No missing values found. Dataset is complete.")
        
    # Ensure correct data types
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Year"] = df["Year"].astype(int)
    df["Units Sold"] = df["Units Sold"].astype(int)
    df["Unit Price"] = df["Unit Price"].astype(float)
    df["Revenue"] = df["Revenue"].astype(float)
    df["Cost"] = df["Cost"].astype(float)
    df["Profit"] = df["Profit"].astype(float)
    df["Marketing Spend"] = df["Marketing Spend"].astype(float)
    df["Forecasted Revenue"] = df["Forecasted Revenue"].astype(float)
    df["Actual Revenue"] = df["Actual Revenue"].astype(float)
    df["Sales Target"] = df["Sales Target"].astype(float)
    
    # Recalculate and validate metrics to ensure mathematical precision
    # Preserve the trend-adjusted revenue and profit computed by data_generator.py
    df["Revenue Variance %"] = np.round(((df["Actual Revenue"] - df["Forecasted Revenue"]) / df["Forecasted Revenue"]) * 100, 2)
    df["Target Achievement %"] = np.round((df["Actual Revenue"] / df["Sales Target"]) * 100, 2)
    
    # Sort data chronologically
    df.sort_values(by="Order Date", inplace=True)
    
    # Save the cleaned transactional data
    print(f"Saving cleaned transactional data to {cleaned_path}...")
    os.makedirs(os.path.dirname(cleaned_path), exist_ok=True)
    df.to_csv(cleaned_path, index=False)
    
    # 2. Data Warehouse Aggregation (Pre-Aggregating for Web Dashboard)
    print("Creating pre-aggregated multidimensional dataset for HTML/CSS/JS dashboard...")
    
    # Extract month abbreviation and year-month sort key
    df["MonthShort"] = df["Order Date"].dt.strftime("%b")
    df["MonthVal"] = df["Order Date"].dt.month
    
    # Group by key dimensions to create a summary table (OLAP cube-like structure)
    group_cols = ["Year", "MonthVal", "MonthShort", "Month", "Quarter", "Region", "Product Category", "Customer Segment"]
    
    agg_df = df.groupby(group_cols).agg({
        "Units Sold": "sum",
        "Revenue": "sum",
        "Cost": "sum",
        "Profit": "sum",
        "Marketing Spend": "sum",
        "Forecasted Revenue": "sum",
        "Sales Target": "sum"
    }).reset_index()
    
    # Recalculate metrics on aggregated level
    agg_df["Revenue"] = np.round(agg_df["Revenue"], 2)
    agg_df["Cost"] = np.round(agg_df["Cost"], 2)
    agg_df["Profit"] = np.round(agg_df["Profit"], 2)
    agg_df["Forecasted Revenue"] = np.round(agg_df["Forecasted Revenue"], 2)
    agg_df["Sales Target"] = np.round(agg_df["Sales Target"], 2)
    agg_df["Marketing Spend"] = np.round(agg_df["Marketing Spend"], 2)
    agg_df["Units Sold"] = agg_df["Units Sold"].astype(int)
    
    # Sort aggregated data for clean rendering
    agg_df.sort_values(by=["Year", "MonthVal"], inplace=True)
    
    # Format as list of records (dictionaries)
    records = agg_df.to_dict(orient="records")
    
    # Get top products to pre-load and display static rankings easily in dashboard
    top_products_df = df.groupby(["Product Category", "Product Name"]).agg({
        "Revenue": "sum",
        "Units Sold": "sum",
        "Profit": "sum"
    }).reset_index()
    top_products_df["Revenue"] = np.round(top_products_df["Revenue"], 2)
    top_products_df["Profit"] = np.round(top_products_df["Profit"], 2)
    top_products = top_products_df.to_dict(orient="records")
    
    # Write aggregated data as a JS file
    print(f"Exporting dashboard data structure to {js_output_path}...")
    os.makedirs(os.path.dirname(js_output_path), exist_ok=True)
    
    js_content = f"// Pre-aggregated Sales Data for HTML/CSS/JS Dashboard\n"
    js_content += f"// Total Transactional Records: {len(df)}\n"
    js_content += f"// Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    js_content += f"const dashboardData = {json.dumps(records, indent=2)};\n\n"
    js_content += f"const topProductsData = {json.dumps(top_products, indent=2)};\n"
    
    with open(js_output_path, "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print("Data pipeline finished successfully!")

if __name__ == "__main__":
    raw_data = os.path.join("data", "raw_sales_data.csv")
    cleaned_data = os.path.join("data", "cleaned_sales_data.csv")
    js_data = os.path.join("docs", "data.js")
    run_sales_analysis(raw_data, cleaned_data, js_data)
