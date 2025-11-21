import pandas as pd
import matplotlib.pyplot as plt

def analyze_bidco_market_share(df):
    """
    Analyzes market share for BIDCO AFRICA LIMITED and visualizes top 20 suppliers.

    Parameters:
    df (pandas.DataFrame): DataFrame containing a 'Supplier' column.

    Returns:
    None
    """
    # Filter for BIDCO AFRICA LIMITED
    bidco_df = df[df['Supplier'] == 'BIDCO AFRICA LIMITED']

    # Calculate percentage of total rows
    total_rows = len(df)
    bidco_rows = len(bidco_df)
    bidco_percentage = (bidco_rows / total_rows) * 100

    print(f"Total rows: {total_rows}")
    print(f"BIDCO AFRICA LIMITED rows: {bidco_rows}")
    print(f"Percentage of overall data: {bidco_percentage:.2f}%")

    # Count number of unique suppliers
    num_suppliers = df['Supplier'].nunique()
    print(f"Number of suppliers: {num_suppliers}")

    # Market share (based on row count or total sales)
    supplier_distribution = df['Supplier'].value_counts(normalize=True) * 100  # percentage share

    # Visualize supplier market share
    top_suppliers = supplier_distribution.head(20)

    plt.figure(figsize=(10,6))
    bars = plt.bar(top_suppliers.index, top_suppliers.values, color='lightgrey')
    plt.title("Top 20 Suppliers by Market Share (based on data count)")
    plt.ylabel("Percentage of Total Data (%)")
    plt.xticks(rotation=45, ha='right')

    # Highlight BIDCO bar
    for i, supplier in enumerate(top_suppliers.index):
        if supplier == 'BIDCO AFRICA LIMITED':
            bars[i].set_color('orange')
            plt.text(i, top_suppliers.values[i] + 0.5, f"{top_suppliers.values[i]:.2f}%", 
                     ha='center', fontsize=9, color='black')

    plt.tight_layout()
    plt.show()

# Filters BIDCO automatically.
# Counts unique stores per category.
# Sorts from highest to lowest coverage.
# Visualizes it with a horizontal bar chart.
# Returns the Series so you can use it for further analysis

import seaborn as sns

def bidco_store_coverage(df):
    """
    Analyzes and visualizes how many stores BIDCO AFRICA LIMITED supplies in each category.

    Parameters:
    df (pandas.DataFrame): DataFrame containing 'Supplier', 'Category', and 'Store Name' columns.

    Returns:
    pandas.Series: Number of unique stores per category for BIDCO.
    """
    # Filter for BIDCO AFRICA LIMITED
    bidco_df = df[df['Supplier'] == 'BIDCO AFRICA LIMITED']

    # Count unique stores per category
    bidco_category_stores = (
        bidco_df.groupby('Category')['Store Name']
        .nunique()
        .sort_values(ascending=False)
    )

    # Plot the results
    plt.figure(figsize=(8,6))
    sns.barplot(
        x=bidco_category_stores.values,
        y=bidco_category_stores.index,
        palette="YlGnBu"
    )
    plt.title("BIDCO AFRICA LIMITED: Store Coverage by Category", fontsize=14)
    plt.xlabel("Number of Stores")
    plt.ylabel("Category")
    plt.tight_layout()
    plt.show()

    return bidco_category_stores
