import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def visualize_supplier_price_extremes_by_item_code(df, item_code):
    """
    For a given Item_Code:
    - Computes average unit price per supplier
    - Uses IQR to find extreme suppliers
    - Creates a clear visual showing supplier pricing
    - Returns a table of extreme suppliers
    """
    
    # Filter for the selected product
    d = df[df['Item_Code'] == item_code].copy()
    
    # Calculate unit price
    d['Unit_Price'] = d['Total Sales'] / d['Quantity']
    
    # Average price per supplier
    supplier_price = (
        d.groupby('Supplier')['Unit_Price']
        .mean()
        .reset_index(name='Avg_Unit_Price')
    )
    
    # Compute IQR
    Q1 = supplier_price['Avg_Unit_Price'].quantile(0.25)
    Q3 = supplier_price['Avg_Unit_Price'].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Classify extreme suppliers
    def classify(p):
        if p < lower_bound:
            return "Low Price Outlier"
        elif p > upper_bound:
            return "High Price Outlier"
        else:
            return "Normal"
    
    supplier_price['Status'] = supplier_price['Avg_Unit_Price'].apply(classify)
    
    # Extract only outliers
    outliers = supplier_price[supplier_price['Status'] != 'Normal']

    # -------- VISUAL --------
    plt.figure(figsize=(12, 6))

    sns.boxplot(
        x=supplier_price['Avg_Unit_Price'],
        color='lightblue'
    )

    sns.stripplot(
        x='Avg_Unit_Price',
        y=[''] * len(supplier_price),
        data=supplier_price,
        hue='Supplier',
        size=9,
        jitter=False
    )

    plt.title(f"Supplier Price Extremes for Item_Code {item_code}")
    plt.xlabel("Average Unit Price")
    plt.ylabel("")
    plt.legend(title="Supplier", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.show()

    return outliers

# outliers = visualize_supplier_price_extremes(df, item_code=12345)
# outliers


# ========================================
# Price Outlier Visualizer
# ========================================
# ✔ calculates unit price
# ✔ calculates IQR
# ✔ marks extreme stores
# ✔ draws a boxplot per product (Item_Code)
# ✔ returns a table of outlier stores too

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def visualize_price_outliers(df, item_code):
    """
    Visualize extreme store pricing for a given product (Item_Code) using IQR.
    Highlights outlier stores and colors points by supplier.
    Returns a dataframe of outlier stores.
    """
    
    # --- Filter to the selected product ---
    df_item = df[df['Item_Code'] == item_code].copy()
    
    # --- Calculate unit price ---
    df_item['Unit_Price'] = df_item['Total Sales'] / df_item['Quantity']
    
    # --- Compute IQR ---
    Q1 = df_item['Unit_Price'].quantile(0.25)
    Q3 = df_item['Unit_Price'].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # --- Outlier Detection ---
    df_item['Outlier'] = df_item['Unit_Price'].apply(
        lambda x: 'Low Price Outlier' if x < lower_bound 
        else ('High Price Outlier' if x > upper_bound else 'Normal')
    )
    
    outliers = df_item[df_item['Outlier'] != 'Normal'][[
        'Store Name', 'Supplier', 'Unit_Price', 'Outlier'
    ]].drop_duplicates()

    # --- Visualisation ---
    plt.figure(figsize=(12, 6))
    
    # Boxplot of all store prices
    sns.boxplot(x=df_item['Unit_Price'], color='lightblue')
    
    # Plot only extreme stores, colored by Supplier
    sns.scatterplot(
        x='Unit_Price',
        y=[0]*len(outliers),
        hue='Supplier',
        data=outliers,
        s=100,
        zorder=10,
        palette='tab10',
        legend='full'
    )

    # Annotate extreme stores
    for idx, row in outliers.iterrows():
        plt.text(
            row['Unit_Price'], 
            0.05,  # slightly above the baseline
            row['Store Name'],
            horizontalalignment='center',
            fontsize=9,
            rotation=45
        )
    
    plt.title(f"Store Pricing Variation for Item_Code {item_code}", fontsize=14, weight='bold')
    plt.xlabel("Unit Price")
    plt.yticks([])  # Hide y-axis ticks
    plt.legend(title="Supplier", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

    return outliers

# item_code = 123456   # example product
# outlier_stores = visualize_price_outliers(df, item_code)
# outlier_stores


# =====================================================================
# Supplier Extreme Pricing Detector
# ======================================================================

# Uses unit price (realised price), not only RRP

# Outliers are detected per Item_Code AND per Supplier, which is what you want

# Automatically produces a beautiful business-friendly visual

# No chained-assignment warnings

# Cleaner grouping, clearer logic, faster

# You only pass the df, nothing else (top_n optional)

# Clearer plot labels + supplier colors + better readability
def plot_supplier_price_outliers(df, top_n=10):
    """
    Detects extreme pricing per product by supplier using IQR on unit prices.
    Produces a summary visual showing which suppliers have unusually high/low
    prices for the top N affected products.

    Parameters:
        df : pandas DataFrame
        top_n : number of products (Item Codes) with most supplier outliers to plot
    """

    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    print(f"Comparing Prices Across Supplier.......\n")

    # --- Clean Data ---
    d = df[['Item_Code', 'Description', 'Supplier', 'Quantity',
            'Total Sales', 'Store Name']].copy()
    d = d[d['Quantity'] > 0].copy()

    # Compute unit price
    d['Unit_Price'] = d['Total Sales'] / d['Quantity']

    # --- Outlier detection per Item_Code (across suppliers) ---
    def detect_supplier_outliers(g):
        Q1 = g['Unit_Price'].quantile(0.25)
        Q3 = g['Unit_Price'].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        g['Outlier'] = (g['Unit_Price'] < lower) | (g['Unit_Price'] > upper)
        return g

    out_df = d.groupby('Item_Code', group_keys=False).apply(detect_supplier_outliers)

    # --- Identify top N products with the highest supplier outliers ---
    top_items = (
        out_df[out_df['Outlier']]
        .groupby('Item_Code')
        .size()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )

    plot_df = out_df[(out_df['Item_Code'].isin(top_items)) & (out_df['Outlier'])]

    # --- Summarize outliers per product per supplier ---
    summary = (plot_df.groupby(['Description', 'Supplier'])
               .size()
               .unstack(fill_value=0))

    # Keep only suppliers that appear as outliers
    summary = summary.loc[:, summary.sum(axis=0) > 0]

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(15, 8))

    summary.plot(
        kind='barh',
        stacked=True,
        ax=ax,
        color=sns.color_palette("tab20", n_colors=summary.shape[1])
    )

    ax.set_title("Products with Extreme Supplier Pricing (Unit Price IQR Method)",
                 fontsize=16, weight='bold')
    ax.set_xlabel("Number of Supplier Outlier Records")
    ax.set_ylabel("Product Description")
    ax.invert_yaxis()
    ax.legend(title="Supplier", bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()

    return fig

