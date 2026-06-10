import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sales_data(output_path, num_rows=105000):
    print(f"Starting generation of {num_rows} unique sales records...")
    np.random.seed(42)  # For reproducibility

    # Define metadata arrays
    regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]
    
    region_countries = {
        "North America": ["United States", "Canada"],
        "Europe": ["United Kingdom", "Germany", "France", "Italy"],
        "Asia-Pacific": ["Japan", "Australia", "India", "Singapore"],
        "Latin America": ["Brazil", "Mexico", "Colombia", "Argentina"]
    }
    
    region_reps = {
        "North America": ["Sarah Jenkins", "Michael Chang", "David Miller"],
        "Europe": ["Emma Dubois", "Lukas Weber", "Chloe Laurent"],
        "Asia-Pacific": ["Rajesh Kumar", "Yuki Tanaka", "Aisha Rahman"],
        "Latin America": ["Carlos Mendez", "Sofia Rodriguez", "Diego Silva"]
    }

    segments = ["Consumer", "Corporate", "Home Office"]
    
    categories = ["Technology", "Office Supplies", "Furniture", "Hardware"]
    
    category_products = {
        "Technology": ["Cloud SaaS License", "Smart Phone v12", "Enterprise Router", "Security Software Suite"],
        "Office Supplies": ["Premium Paper Carton", "Heavy Duty Binder", "Gel Pens Pack", "Ergonomic Stapler"],
        "Furniture": ["Ergonomic Task Chair", "Adjustable Standing Desk", "Modular Bookshelf", "Mobile File Cabinet"],
        "Hardware": ["External SSD 2TB", "UltraWide Monitor 34\"", "Mechanical Keyboard", "USB-C Triple Dock"]
    }
    
    product_base_prices = {
        "Cloud SaaS License": 120.0, "Smart Phone v12": 850.0, "Enterprise Router": 450.0, "Security Software Suite": 250.0,
        "Premium Paper Carton": 15.0, "Heavy Duty Binder": 8.0, "Gel Pens Pack": 5.0, "Ergonomic Stapler": 12.0,
        "Ergonomic Task Chair": 350.0, "Adjustable Standing Desk": 550.0, "Modular Bookshelf": 220.0, "Mobile File Cabinet": 180.0,
        "External SSD 2TB": 130.0, "UltraWide Monitor 34\"": 400.0, "Mechanical Keyboard": 90.0, "USB-C Triple Dock": 110.0
    }
    
    product_cost_multipliers = {
        "Cloud SaaS License": 0.15, "Smart Phone v12": 0.65, "Enterprise Router": 0.55, "Security Software Suite": 0.20,
        "Premium Paper Carton": 0.40, "Heavy Duty Binder": 0.35, "Gel Pens Pack": 0.30, "Ergonomic Stapler": 0.45,
        "Ergonomic Task Chair": 0.60, "Adjustable Standing Desk": 0.65, "Modular Bookshelf": 0.50, "Mobile File Cabinet": 0.55,
        "External SSD 2TB": 0.50, "UltraWide Monitor 34\"": 0.60, "Mechanical Keyboard": 0.45, "USB-C Triple Dock": 0.50
    }

    # Generate basic random mappings
    # Assign regions
    assigned_regions = np.random.choice(regions, size=num_rows, p=[0.40, 0.28, 0.20, 0.12])
    
    # Mappings for countries and sales reps
    countries = []
    sales_reps = []
    for r in assigned_regions:
        countries.append(np.random.choice(region_countries[r]))
        sales_reps.append(np.random.choice(region_reps[r]))
        
    assigned_segments = np.random.choice(segments, size=num_rows, p=[0.35, 0.45, 0.20])
    assigned_categories = np.random.choice(categories, size=num_rows, p=[0.30, 0.35, 0.20, 0.15])
    
    # Products selection based on category
    products = []
    for cat in assigned_categories:
        products.append(np.random.choice(category_products[cat]))
        
    # Generate dates from 2021-01-01 to 2026-06-30
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2026, 6, 30)
    delta_days = (end_date - start_date).days
    
    random_days = np.random.randint(0, delta_days + 1, size=num_rows)
    order_dates = [start_date + timedelta(days=int(d)) for d in random_days]
    
    # Units sold (dependent on category to look realistic)
    units_sold_ranges = {
        "Technology": (1, 15),
        "Office Supplies": (10, 100),
        "Furniture": (1, 8),
        "Hardware": (2, 25)
    }
    
    units_sold = []
    for cat in assigned_categories:
        low, high = units_sold_ranges[cat]
        units_sold.append(np.random.randint(low, high + 1))
    units_sold = np.array(units_sold)
    
    # Base prices and costs
    unit_prices = np.array([product_base_prices[p] for p in products])
    cost_mults = np.array([product_cost_multipliers[p] for p in products])
    
    # Introduce small random pricing variance (+-5%) for B2B negotiations
    price_variance = np.random.uniform(0.95, 1.05, size=num_rows)
    unit_prices = np.round(unit_prices * price_variance, 2)
    
    # Math Calculations
    revenue = np.round(units_sold * unit_prices, 2)
    costs = np.round(revenue * cost_mults, 2)
    profit = np.round(revenue - costs, 2)

    # Seasonality multipliers
    # Months: Jan=1, Feb=2, ..., Dec=12
    # Season: Q4 (Oct-Dec) high (+25%), Q1 (Jan-Mar) low (-15%), Q3 (Jul-Sep) flat, Q2 (Apr-Jun) (+10%)
    month_numbers = np.array([d.month for d in order_dates])
    year_numbers = np.array([d.year for d in order_dates])
    
    season_multipliers = np.ones(num_rows)
    seasons = []
    
    for idx, month in enumerate(month_numbers):
        if month in [12, 1, 2]:
            seasons.append("Winter")
            season_multipliers[idx] = 0.85 if month != 12 else 1.25  # December spike, Jan/Feb drop
        elif month in [3, 4, 5]:
            seasons.append("Spring")
            season_multipliers[idx] = 1.05
        elif month in [6, 7, 8]:
            seasons.append("Summer")
            season_multipliers[idx] = 0.90
        else:
            seasons.append("Autumn")
            season_multipliers[idx] = 1.15

    # Yearly growth trends
    # 2021 = 1.0, 2022 = 1.08, 2023 = 1.20, 2024 = 1.38, 2025 = 1.45, 2026 = 1.55
    yearly_multipliers = {2021: 1.0, 2022: 1.08, 2023: 1.20, 2024: 1.38, 2025: 1.45, 2026: 1.58}
    year_mults = np.array([yearly_multipliers[y] for y in year_numbers])

    # Apply trends to revenue, cost, profit to make trends look real
    revenue = np.round(revenue * season_multipliers * year_mults, 2)
    costs = np.round(costs * season_multipliers * year_mults, 2)
    profit = np.round(revenue - costs, 2)

    # Marketing Spend (typically 5% to 15% of revenue, with some random variation)
    marketing_pct = np.random.uniform(0.05, 0.12, size=num_rows)
    marketing_spend = np.round(revenue * marketing_pct, 2)

    # Forecasted Revenue & Actual Revenue (Actual Revenue equals Revenue)
    # Forecast is generated with a normal distribution error centered around actual revenue (mean error of 2% under-forecast with 10% std dev)
    forecast_error = np.random.normal(1.02, 0.08, size=num_rows)
    # Forecasted Revenue
    forecasted_revenue = np.round(revenue * forecast_error, 2)
    actual_revenue = revenue.copy()
    
    # Revenue Variance %: (Actual - Forecasted) / Forecasted * 100
    revenue_variance_pct = np.round(((actual_revenue - forecasted_revenue) / forecasted_revenue) * 100, 2)

    # Sales Targets
    # Targets are set monthly per representative. To model realistic targets:
    # Target = Forecasted Revenue * target multiplier (e.g. 1.05, indicating a stretch target)
    target_multiplier = np.random.uniform(0.98, 1.08, size=num_rows)
    sales_target = np.round(forecasted_revenue * target_multiplier, 2)
    
    # Target Achievement %: (Actual / Target) * 100
    target_achievement_pct = np.round((actual_revenue / sales_target) * 100, 2)

    # Formatting Dates
    months = np.array([d.strftime("%B") for d in order_dates])
    quarters = np.array([f"Q{(d.month-1)//3 + 1}" for d in order_dates])
    order_date_strs = np.array([d.strftime("%Y-%m-%d") for d in order_dates])
    
    # Create sequential unique Order IDs
    order_ids = [f"ORD-{y}-{i+100000:06d}" for i, y in enumerate(year_numbers)]

    # Assemble DataFrame
    df = pd.DataFrame({
        "Order ID": order_ids,
        "Order Date": order_date_strs,
        "Month": months,
        "Quarter": quarters,
        "Year": year_numbers,
        "Region": assigned_regions,
        "Country": countries,
        "Customer Segment": assigned_segments,
        "Product Category": assigned_categories,
        "Product Name": products,
        "Sales Representative": sales_reps,
        "Units Sold": units_sold,
        "Unit Price": unit_prices,
        "Revenue": revenue,
        "Cost": costs,
        "Profit": profit,
        "Marketing Spend": marketing_spend,
        "Forecasted Revenue": forecasted_revenue,
        "Actual Revenue": actual_revenue,
        "Revenue Variance %": revenue_variance_pct,
        "Sales Target": sales_target,
        "Target Achievement %": target_achievement_pct,
        "Season": seasons
    })

    # Ensure unique rows based on Order ID
    df.drop_duplicates(subset=["Order ID"], inplace=True)
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"Dataset successfully created and saved to {output_path}!")
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns.")

if __name__ == "__main__":
    output_file = os.path.join("data", "raw_sales_data.csv")
    generate_sales_data(output_file)
