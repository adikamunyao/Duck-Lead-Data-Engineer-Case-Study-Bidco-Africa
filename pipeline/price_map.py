import folium
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# ----------------------------------------------------------
# 1. GEOGRAPHIC MAP OF KENYA STORES COLORED BY PRICE INDEX
# ----------------------------------------------------------

def plot_geographic_price_map(store_summary, map_center=(-0.0236, 37.9062)):
    """
    Creates a geographic map of Kenyan stores color-coded by price index.
    Requires 'Latitude' and 'Longitude' columns in store_summary.
    """

    m = folium.Map(location=map_center, zoom_start=6)

    # Color logic: blue = underpriced, red = overpriced
    def get_color(idx):
        if idx < 0.90: return "blue"
        if idx < 1.00: return "lightblue"
        if idx < 1.10: return "orange"
        return "red"

    for _, row in store_summary.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=8,
            fill=True,
            fill_opacity=0.85,
            color=get_color(row['Avg_Price_Index']),
            popup=(
                f"<b>{row['Store Name']}</b><br>"
                f"Price Index: {row['Avg_Price_Index']:.3f}<br>"
                f"Discount: {row['Avg_Discount']:.1f}%<br>"
                f"Positioning: {row['Positioning']}"
            )
        ).add_to(m)

    return m



# -------------------------------------------------------------------
# 2. HEATMAP GROUPED BY STORE FORMAT (DISCOUNT / NEAR-MARKET / PREMIUM)
# -------------------------------------------------------------------

def plot_format_grouped_heatmap(store_summary):
    """
    Creates a heatmap where stores are grouped by Positioning:
    'Discount', 'Near-Market', 'Premium'.
    """

    # Sort by format then price index
    sorted_df = store_summary.sort_values(
        by=['Positioning', 'Avg_Price_Index'],
        ascending=[True, True]
    )

    pivot_df = sorted_df[['Store Name', 'Positioning', 'Avg_Price_Index']]
    pivot_df = pivot_df.set_index('Store Name')

    plt.figure(figsize=(9, 22))
    sns.heatmap(
        pivot_df[['Avg_Price_Index']],
        annot=True,
        cmap="coolwarm",
        center=1.0,
        linewidths=.5,
        cbar_kws={'label': 'Avg Price Index'}
    )

    plt.title("Store Price Index Heatmap — Grouped by Format", fontsize=16)
    plt.xlabel("Price Index")
    plt.ylabel("Store Name")
    plt.tight_layout()
    plt.show()



# ----------------------------------------------------------
# HOW TO RUN BOTH
# ----------------------------------------------------------

# 1. Map (must be in a cell alone to render correctly in Jupyter)
# map_view = plot_geographic_price_map(store_summary)
# map_view

# 2. Grouped Heatmap
# plot_format_grouped_heatmap(store_summary)
