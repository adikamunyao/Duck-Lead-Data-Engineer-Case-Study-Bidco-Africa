import sys
import os
import pandas as pd
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
from IPython.display import display, Markdown

# Function to build the price index
def build_price_index(df: pd.DataFrame, target_supplier: str = "Bidco") -> pd.DataFrame:
    print("Building Price Index...")

    # Identify target supplier and competitors
    mask_target = df['Supplier'].str.contains(target_supplier, case=False, na=False)
    df_target = df[mask_target].copy()
    df_comp = df[~mask_target].copy()

    # Competitor Avg Price per Store + Sub-Department + Section
    comp_avg = (
        df_comp.groupby(['Store Name', 'Sub-Department', 'Section'])['Unit_Price']
        .mean()
        .reset_index()
        .rename(columns={'Unit_Price': 'Comp_Avg_Price'})
    )

    # Target Supplier Avg Price per same group
    target_avg = (
        df_target.groupby(['Store Name', 'Sub-Department', 'Section'])['Unit_Price']
        .mean()
        .reset_index()
        .rename(columns={'Unit_Price': f'{target_supplier}_Avg_Price'})
    )

    # Merge and calculate Price Index
    price_index = target_avg.merge(comp_avg, on=['Store Name', 'Sub-Department', 'Section'], how='left')
    price_index['Price_Index'] = (price_index[f'{target_supplier}_Avg_Price'] / price_index['Comp_Avg_Price']).round(3)
    price_index = price_index.dropna(subset=['Comp_Avg_Price'])  # Only keep where competitors exist

    # Add Avg RRP and Avg Discount %
    target_summary = (
        df_target.groupby(['Store Name', 'Sub-Department', 'Section'])
        .agg(
            Avg_RRP=('RRP', 'mean'),
            Avg_Discount_Pct=('Discount_Pct', 'mean')
        )
        .reset_index()
    )
    price_index = price_index.merge(target_summary, on=['Store Name', 'Sub-Department', 'Section'], how='left')
    price_index['Avg_Discount_Pct'] = (price_index['Avg_Discount_Pct'] * 100).round(1)

    print(f"Price Index built for {len(price_index)} store-section combos")
    return price_index
