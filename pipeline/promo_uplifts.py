def calculate_bidco_promo_uplift(df):
    """
    Calculates promo uplift % for BIDCO products by section.
    Logic is identical to the user's original code, only structured as a pipeline.
    """

    import numpy as np
    import pandas as pd

    # Filter BIDCO only
    bidco_data = df[df['Supplier'] == 'BIDCO AFRICA LIMITED'].copy()

    # Promo vs baseline units split
    bidco_data['Promo_Units'] = bidco_data['Quantity'].where(bidco_data['On_Promo'] == True, 0)
    bidco_data['Baseline_Units'] = bidco_data['Quantity'].where(bidco_data['On_Promo'] == False, 0)

    # Aggregate by Section
    section_units = (
        bidco_data.groupby('Section')
        .agg({
            'Promo_Units': 'sum',
            'Baseline_Units': 'sum'
        })
        .reset_index()
    )

    # Promo uplift %
    section_units['Promo_Uplift_Pct'] = (
        (section_units['Promo_Units'] - section_units['Baseline_Units']) /
        (section_units['Baseline_Units'].replace({0: np.nan}))
    ) * 100

    # Sort from highest uplift down
    section_units_sorted = section_units.sort_values('Promo_Uplift_Pct', ascending=False)

    return section_units_sorted

def visualize_bidco_promo_uplift(section_units_sorted):
    """
    Visualizes promo uplift using the user's original logic and style.
    """

    import seaborn as sns
    import matplotlib.pyplot as plt
    import numpy as np

    # Fill missing uplift with 0
    section_units_sorted['Promo_Uplift_Pct_Filled'] = (
        section_units_sorted['Promo_Uplift_Pct'].fillna(0)
    )

    # Define uplift categories (unchanged from your logic)
    def uplift_category(uplift):
        if uplift > 500:
            return 'Very High Uplift'
        elif uplift > 100:
            return 'High Uplift'
        elif uplift > 0:
            return 'Moderate Uplift'
        else:
            return 'Low/Negative Uplift'

    section_units_sorted['Uplift_Category'] = (
        section_units_sorted['Promo_Uplift_Pct_Filled'].apply(uplift_category)
    )

    # Color palette
    palette = {
        'Very High Uplift': '#2ca02c',    # dark green
        'High Uplift': '#98df8a',         # light green
        'Moderate Uplift': '#ffdd57',     # yellow
        'Low/Negative Uplift': '#d62728'  # red
    }

    # Plot
    plt.figure(figsize=(10, 8))
    sns.barplot(
        data=section_units_sorted,
        y='Section',
        x='Promo_Uplift_Pct_Filled',
        hue='Uplift_Category',
        dodge=False,
        palette=palette,
        edgecolor='black'
    )

    plt.axvline(0, color='black', linestyle='--')
    plt.xlabel("Promo Uplift % (units vs baseline)")
    plt.ylabel("Section")
    plt.title("BIDCO: Promo Uplift % by Section with Performance Categories")
    plt.legend(title='Uplift Category', loc='lower right')

    plt.tight_layout()
    plt.show()

    return section_units_sorted
