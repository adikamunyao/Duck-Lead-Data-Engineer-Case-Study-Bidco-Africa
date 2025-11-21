import pandas as pd
import numpy as np
from IPython.display import display, Markdown

def run_pricing_pipeline(bidco_data, full_data_path="../data/cleaned_sales_data.csv"):

    # ───────────────────────────────────────────────────────────────
    # STEP 0: Setup
    # ───────────────────────────────────────────────────────────────
    df = bidco_data.copy()

    df_original = pd.read_csv(full_data_path)

    df['Unit_Price'] = df['Total Sales'] / df['Quantity']

    try:
        full_df = df_original.copy()
        comp_df = full_df[~full_df['Supplier'].str.contains('BIDCO', case=False, na=False)].copy()
        comp_df['Unit_Price'] = comp_df['Total Sales'] / comp_df['Quantity']
        has_comp = True
    except:
        print("Warning: No full dataset found. Skipping competitor comparisons.")
        has_comp = False

    # ───────────────────────────────────────────────────────────────
    # STEP 1: Compute Section Metrics
    # ───────────────────────────────────────────────────────────────
    results = []

    for section in df['Section'].unique():

        bidco_sec = df[df['Section'] == section]

        units = bidco_sec['Quantity'].sum()
        revenue = bidco_sec['Total Sales'].sum()
        current_price = revenue / units
        rrp = (bidco_sec['RRP'] * bidco_sec['Quantity']).sum() / units
        current_discount = (1 - current_price / rrp) * 100

        comp_price = np.nan
        price_index = np.nan

        if has_comp:
            comp_sec = comp_df[comp_df['Section'] == section]
            if not comp_sec.empty:
                comp_price = (comp_sec['Unit_Price'] * comp_sec['Quantity']).sum() / comp_sec['Quantity'].sum()
                price_index = round(current_price / comp_price, 3) if comp_price > 0 else np.nan

        target_price = rrp * 0.91
        gain_per_unit = target_price - current_price
        weekly_gain = max(0, gain_per_unit * units)

        results.append({
            'Section': section,
            'Units_Sold': int(units),
            'RRP': round(rrp, 1),
            'Bidco_Price': round(current_price, 1),
            'Comp_Price': round(comp_price, 1) if not np.isnan(comp_price) else np.nan,
            'Price_Index': price_index,
            'Current_Discount_%': round(current_discount, 1),
            'Target_Price_(9%_off)': round(target_price, 1),
            'Weekly_Gain_KSh': int(weekly_gain)
        })

    action_df = pd.DataFrame(results)

    # ───────────────────────────────────────────────────────────────
    # STEP 2: Action Logic
    # ───────────────────────────────────────────────────────────────
    def get_action(row):
        idx = row['Price_Index']
        disc = row['Current_Discount_%']
        gain = row['Weekly_Gain_KSh']

        if pd.isna(idx):
            if disc > 12:
                return "Too discounted", f"Reduce to 9% off → +KSh {gain:,.0f}/week"
            elif disc < 5:
                return "Premium", "Keep — protect margin"
            else:
                return "Balanced", "Monitor"

        if idx < 0.98 and disc > 10:
            return "Too cheap + deep", f"Raise to 9% off → +KSh {gain:,.0f}/week"
        elif idx < 0.98:
            return "Too cheap", f"Raise price → +KSh {gain:,.0f}/week"
        elif idx > 1.05 and disc > 10:
            return "Too expensive + deep", f"Cut discount → +KSh {gain:,.0f}/week"
        elif disc > 12:
            return "Too discounted", f"Reduce to 9% → +KSh {gain:,.0f}/week"
        elif disc < 5 and idx > 1.02:
            return "Premium gold", "Keep — winning"
        else:
            return "Balanced", "Monitor"

    action_df[['Status', 'Action']] = action_df.apply(
        lambda x: pd.Series(get_action(x)), axis=1
    )

    final = (
        action_df[
            [
                'Section', 'Units_Sold', 'RRP', 'Bidco_Price', 'Comp_Price',
                'Price_Index', 'Current_Discount_%', 'Status', 'Action', 'Weekly_Gain_KSh'
            ]
        ]
        .sort_values('Weekly_Gain_KSh', ascending=False)
        .reset_index(drop=True)
    )

    # ───────────────────────────────────────────────────────────────
    # Output
    # ───────────────────────────────────────────────────────────────
    return final
