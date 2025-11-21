# Calculate Promo Uplift per Store & Section
def calculate_bidco_store_section_uplift(df):
    """
    Calculates promo uplift per store and section for BIDCO products.
    Logic is identical to the user's code, only structured into a function.
    """

    import pandas as pd
    import numpy as np

    bidco_df = df[df['Supplier'] == 'BIDCO AFRICA LIMITED'].copy()

    # Baseline (off-promo) mean daily units per Store & Section
    baseline = (
        bidco_df[bidco_df['On_Promo'] == False]
        .groupby(['Store Name', 'Section'])['Quantity']
        .mean()
        .reset_index()
        .rename(columns={'Quantity': 'Baseline_Units'})
    )

    # Promo (on-promo) mean daily units per Store & Section
    promo = (
        bidco_df[bidco_df['On_Promo'] == True]
        .groupby(['Store Name', 'Section'])['Quantity']
        .mean()
        .reset_index()
        .rename(columns={'Quantity': 'Promo_Units'})
    )

    # Merge promo and baseline
    promo_analysis = pd.merge(promo, baseline, on=['Store Name', 'Section'], how='left')

    # Promo uplift %
    promo_analysis['Promo_Uplift_Pct'] = (
        (promo_analysis['Promo_Units'] - promo_analysis['Baseline_Units']) /
        promo_analysis['Baseline_Units']
    ) * 100

    # Classification of reliability
    promo_analysis['Type'] = np.where(
        promo_analysis['Baseline_Units'].isna(),
        'Emerging Promo',
        'Reliable Uplift'
    )

    # Fill uplift for emerging segments
    promo_analysis['Promo_Uplift_Pct_Fill'] = promo_analysis['Promo_Uplift_Pct'].fillna(0)

    return promo_analysis

# ==================================================
# Visualize Top-Performing Stores per Section
# ==================================================
def visualize_bidco_top_store_uplift(promo_analysis):
    """
    Plots the top-performing stores per section based on promo uplift.
    Uses the logic exactly as provided by the user.
    """

    import seaborn as sns
    import matplotlib.pyplot as plt
    
    # Keep only reliable uplift calculations
    store_uplift = promo_analysis[promo_analysis['Type'] == 'Reliable Uplift'].copy()

    # Rank stores within each section
    store_uplift['Rank_in_Section'] = store_uplift.groupby('Section')['Promo_Uplift_Pct']\
                                                   .rank(ascending=False, method='dense')

    # Take the top 5 per section
    top_stores = (
        store_uplift.groupby('Section')
        .apply(lambda x: x.nlargest(5, 'Promo_Uplift_Pct'))
        .reset_index(drop=True)
    )

    # Plot
    plt.figure(figsize=(14, 8))
    sns.barplot(
        data=top_stores,
        x='Promo_Uplift_Pct',
        y='Store Name',
        hue='Section',
        dodge=False,
        palette="RdYlGn"
    )

    plt.xlabel("Promo Uplift %")
    plt.ylabel("Top Stores per Section")
    plt.title("BIDCO Top Performing Stores per Section")
    plt.legend(title='Section', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

    return top_stores

# ===============================================================================
# Heatmap for Emerging Promo Opportunities
# ===============================================================================
def visualize_bidco_emerging_promos(promo_analysis):
    """
    Visualizes emerging promo opportunities where stores participated in promotions
    but have no baseline data, using a heatmap (your logic).
    """

    import seaborn as sns
    import matplotlib.pyplot as plt
    import pandas as pd

    # Filter Emerging Promo group
    emerging_data = promo_analysis[promo_analysis['Type'] == 'Emerging Promo']

    # Pivot table: Section × Store
    emerging_heatmap = emerging_data.pivot_table(
        index='Section',
        columns='Store Name',
        values='Promo_Units',
        aggfunc='sum',
        fill_value=0
    )

    # Plot
    plt.figure(figsize=(16, 8))
    sns.heatmap(
        emerging_heatmap,
        cmap="Blues",
        linewidths=0.5,
        linecolor='gray',
        annot=True,
        fmt=".0f"
    )

    plt.title("BIDCO Emerging Promo Opportunities (No Baseline)")
    plt.ylabel("Section")
    plt.xlabel("Store")
    plt.tight_layout()
    plt.show()

    return emerging_heatmap

