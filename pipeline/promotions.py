def detect_promotions(df, discount_threshold=0.10, min_days=2):
    """
    Detect likely promotional periods for products based on price discounts.

    Parameters:
    df (pandas.DataFrame): DataFrame with columns 'Date Of Sale', 'Total Sales', 'Quantity', 'RRP', 'Item_Code', 'Description'.
    discount_threshold (float): Minimum discount percentage to consider a promotion (default 10% = 0.10).
    min_days (int): Minimum number of discounted days in a week to flag a promotion (default 2).

    Returns:
    pandas.DataFrame: Original DataFrame with additional columns:
        - 'Unit_Price': Realized unit price
        - 'Discount_Pct': Discount percentage relative to RRP
        - 'Year_Week': Year-week identifier
        - 'On_Promo': True if likely on promotion that week
        - 'Day_of_Week': Day name of sale
    """
    import pandas as pd
    import matplotlib.pyplot as plt

    df = df.copy()  # avoid modifying original DataFrame

    # Step 1: Convert Date Of Sale to datetime
    df['Date Of Sale'] = pd.to_datetime(df['Date Of Sale'])

    # Step 2: Compute realized unit price
    df['Unit_Price'] = df['Total Sales'] / df['Quantity']

    # Step 3: Compute discount percentage
    df['Discount_Pct'] = (df['RRP'] - df['Unit_Price']) / df['RRP']

    # Step 4: Extract week identifier (Year + Week number)
    df['Year_Week'] = df['Date Of Sale'].dt.strftime('%Y-%U')

    # Step 5: Flag daily promo events (discount ≥ threshold)
    df['Is_Promo_Day'] = df['Discount_Pct'] >= discount_threshold

    # Step 6: Count promo days per SKU per week
    promo_days = df.groupby(['Item_Code', 'Description', 'Year_Week'])['Is_Promo_Day'].transform('sum')

    # Step 7: Flag likely promo weeks (≥ min_days)
    df['On_Promo'] = promo_days >= min_days

    # Step 8: Day of the week for reference
    df['Day_of_Week'] = df['Date Of Sale'].dt.day_name()

    # Optional: clean up intermediate column
    df.drop(columns=['Is_Promo_Day'], inplace=True)

    return df

#============================================================
# Visualise
#============================================================
# Summarizes number of promo days per store per day of the week.
# Visualizes the most common promo days across all stores.
# Fully reusable and configurable for discount threshold and minimum days.

def visualize_bidco_promo_days(df, visualize=True):
    """
    Visualizes the most common promotion days for BIDCO stores.
    Requires df already processed by detect_promotions().

    Parameters:
        df (pd.DataFrame): Output from detect_promotions() with 'On_Promo' and 'Day_of_Week'.
        visualize (bool): Whether to show the plot.

    Returns:
        pd.DataFrame: Unique promo-day counts per store and weekday.
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Filter only BIDCO products
    bidco_df = df[df['Supplier'] == 'BIDCO AFRICA LIMITED'].copy()

    # Keep only rows flagged as promotional
    bidco_df = bidco_df[bidco_df['On_Promo']]

    # Count UNIQUE promo days → avoids SKU duplication
    promo_summary = (
        bidco_df
        .drop_duplicates(subset=['Store Name', 'Date Of Sale'])  # FIX inflated counts
        .groupby(['Store Name', 'Day_of_Week'])
        .size()
        .reset_index(name='Promo_Days_Count')
    )

    # Overall weekday totals (all stores combined)
    weekday_totals = (
        promo_summary.groupby('Day_of_Week')['Promo_Days_Count']
        .sum()
        .reset_index()
        .sort_values('Promo_Days_Count', ascending=False)
    )

    if visualize:
        plt.figure(figsize=(10, 5))
        sns.barplot(
            data=weekday_totals,
            x='Day_of_Week',
            y='Promo_Days_Count',
            palette='viridis'
        )
        plt.title("Most Common Promo Days for BIDCO Products")
        plt.xlabel("Day of Week")
        plt.ylabel("Number of Promo Days")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    return promo_summary

# Which stores promoted every day
# Which stores promoted occasionally
# Which stores never discounted Bidco products

def visualize_bidco_promo_intensity(df, visualize=True):
    """
    Creates a bar chart showing how many promo days each store had
    for BIDCO products within the single-week dataset.
    
    Parameters:
        df (pd.DataFrame): Output from detect_promotions(), must include On_Promo and Date Of Sale.
        visualize (bool): Whether to draw the bar chart.

    Returns:
        pd.DataFrame: Each store with its promo-day count.
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Focus ONLY on BIDCO items
    bidco_df = df[df['Supplier'] == 'BIDCO AFRICA LIMITED'].copy()

    # Keep only promotional rows
    bidco_df = bidco_df[bidco_df['On_Promo']]

    # Count UNIQUE promo days per store (since only one week)
    promo_days_per_store = (
        bidco_df
        .drop_duplicates(subset=['Store Name', 'Date Of Sale'])
        .groupby('Store Name')
        .size()
        .reset_index(name='Promo_Days_Count')
        .sort_values('Promo_Days_Count', ascending=False)
    )

    if visualize:
        plt.figure(figsize=(10, 6))
        sns.barplot(
            data=promo_days_per_store,
            x='Promo_Days_Count',
            y='Store Name',
            palette='viridis'
        )
        plt.title("Promotional Intensity per Store (BIDCO Only, 1 Week)")
        plt.xlabel("Number of Promo Days This Week")
        plt.ylabel("Store")
        plt.tight_layout()
        plt.show()

    return promo_days_per_store
