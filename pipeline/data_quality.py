# data_quality.py
import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid", font_scale=1.2)

# =========================================================
#  DATA HEALTH PIPELINE
# =========================================================
def data_health_pipeline(df, bidco_name='BIDCO AFRICA LIMITED', unhealthy_score_threshold=75):
    df = df.copy()
    print(f"Running FINAL health check on {len(df):,} rows...\n")

    # -----------------------------------------------------
    # 1. MISSING VALUES
    # -----------------------------------------------------
    missing_counts = df.isna().sum()
    missing_columns_with_counts = missing_counts[missing_counts > 0].to_dict()

    # -----------------------------------------------------
    # 2. DUPLICATES
    # -----------------------------------------------------
    dup_mask = df.duplicated(
        subset=['Item_Code', 'Store Name', 'Date Of Sale'], keep=False
    )
    duplicates = df[dup_mask]
    dup_rate = (len(duplicates) / len(df) * 100)

    # -----------------------------------------------------
    # 3. NEGATIVE VALUES
    # -----------------------------------------------------
    numeric_cols = ['Quantity', 'Total Sales', 'RRP']
    negative_rows = df[(df[numeric_cols] < 0).any(axis=1)].reset_index(drop=True)

    # -----------------------------------------------------
    # 4. OUTLIERS PER ITEM (IQR)
    # -----------------------------------------------------
    price_df = df[['Store Name', 'Item_Code', 'RRP']].dropna(subset=['RRP'])

    def detect_outliers(g):
        Q1, Q3 = g['RRP'].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        g['Outlier'] = (g['RRP'] < lower) | (g['RRP'] > upper)
        return g

    outliers_df = price_df.groupby('Item_Code', group_keys=False).apply(detect_outliers)

    store_outlier_stats = (
        outliers_df.groupby('Store Name', as_index=False)
        .agg(total_products=('Item_Code', 'count'),
             outlier_count=('Outlier', 'sum'))
    )
    store_outlier_stats['outlier_rate'] = (
        store_outlier_stats['outlier_count'] /
        store_outlier_stats['total_products'].replace(0, 1) * 100
    ).round(2)
    store_outlier_stats['Unreliable_Store'] = store_outlier_stats['outlier_rate'] > 10

    # -----------------------------------------------------
    # 5. STORE-LEVEL HEALTH SUMMARY
    # -----------------------------------------------------
    store_health = (
        df.groupby('Store Name', as_index=False)
        .agg(
            total_rows=('Item_Code', 'count'),
            negative_rows=('Quantity', lambda x: (x < 0).sum()),
            missing_rrp=('RRP', lambda x: x.isna().sum())
        )
    )

    outlier_stats = outliers_df.groupby('Store Name', as_index=False).agg(
        outlier_count=('Outlier', 'sum')
    )
    store_health = store_health.merge(outlier_stats, on='Store Name', how='left')
    store_health['outlier_count'] = store_health['outlier_count'].fillna(0)

    missing_cells = df.isna().groupby(df['Store Name']).sum().sum(axis=1)
    mc_df = missing_cells.reset_index(name='total_missing_cells')
    mc_df['total_possible_cells'] = df.groupby('Store Name').size().values * len(df.columns)
    mc_df['pct_missing_all_cols'] = (
        mc_df['total_missing_cells'] / mc_df['total_possible_cells'] * 100
    ).round(2)

    store_health = store_health.merge(
        mc_df[['Store Name', 'pct_missing_all_cols']], on='Store Name', how='left'
    ).merge(
        store_outlier_stats[['Store Name', 'Unreliable_Store']], 
        on='Store Name', how='left'
    ).fillna({'Unreliable_Store': False})

    # percentages
    store_health['pct_negative'] = store_health['negative_rows'] / store_health['total_rows'] * 100
    store_health['pct_missing_rrp'] = store_health['missing_rrp'] / store_health['total_rows'] * 100
    store_health['pct_outliers'] = store_health['outlier_count'] / store_health['total_rows'] * 100

    # -----------------------------------------------------
    # 6. HEALTH SCORE
    # -----------------------------------------------------
    def compute_health_score(row):
        s = 100
        s -= row['pct_negative'] * 0.20
        s -= row['pct_missing_rrp'] * 0.15
        s -= row['pct_outliers'] * 0.30
        s -= row['pct_missing_all_cols'] * 0.25
        if row['Unreliable_Store']:
            s -= 10
        return max(round(s, 1), 0)

    store_health['Data_Health_Score'] = store_health.apply(compute_health_score, axis=1)

    # -----------------------------------------------------
    # 7. OVERALL SCORE
    # -----------------------------------------------------
    overall_score = (
        (store_health['Data_Health_Score'] * store_health['total_rows']).sum()
        / store_health['total_rows'].sum()
    ).round(1)

    def classify(score):
        if score >= 90: return "Excellent – ready for analysis"
        if score >= 75: return "Good – minor cleaning recommended"
        if score >= 60: return "Moderate – review key issues"
        return "Poor – significant cleaning required"

    overall_rating = classify(overall_score)

    # -----------------------------------------------------
    # 8. UNHEALTHY SUMMARY
    # -----------------------------------------------------
    parts = []

    if missing_columns_with_counts:
        parts.append(pd.DataFrame([
            {'Issue': 'Missing Values', 'Store Name': '(all)', 'Details': f"{col} → {cnt} rows"}
            for col, cnt in missing_columns_with_counts.items()
        ]))

    if not negative_rows.empty:
        numeric_cols = ['Quantity', 'Total Sales', 'RRP']
        neg_summary = negative_rows[['Store Name', 'Item_Code', 'Description']].copy()
        neg_summary['Issue'] = 'Negative Value'
        neg_summary['Details'] = negative_rows[numeric_cols].apply(
            lambda r: ', '.join([f"{c}={v}" for c, v in r.items() if v < 0]), axis=1
        )
        parts.append(neg_summary)

    bad_stores = store_health.loc[
        store_health['Data_Health_Score'] < unhealthy_score_threshold,
        ['Store Name', 'Data_Health_Score']
    ].sort_values('Data_Health_Score')

    if not bad_stores.empty:
        bad = bad_stores.copy()
        bad['Issue'] = 'Low Health Score'
        bad['Details'] = bad['Data_Health_Score'].astype(str)
        parts.append(bad[['Issue', 'Store Name', 'Details']])

    unhealthy_df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

    # -----------------------------------------------------
    # 9. STRIKING HIGHLIGHT VISUAL
    # -----------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, max(4, len(unhealthy_df) * 0.5)))

    if not unhealthy_df.empty:
        unhealthy_df['Label'] = unhealthy_df['Store Name'] + " • " + unhealthy_df['Details']

        color_map = {
            'Missing Values': '#E63946',
            'Negative Value': '#FF9F1C',
            'Low Health Score': '#9B59B6'
        }
        unhealthy_df['Color'] = unhealthy_df['Issue'].map(color_map)
        unhealthy_df['Value'] = 1

        ax.barh(unhealthy_df['Label'], unhealthy_df['Value'], color=unhealthy_df['Color'])

        for i, row in unhealthy_df.iterrows():
            ax.text(0.02, i, f"{row['Issue']}", color='white',
                    va='center', fontsize=10, weight='bold')

        ax.set_title("🚨 UNHEALTHY DATA POINTS – QUICK VIEW",
                     fontsize=16, weight='bold', color='darkred')
        ax.set_xticks([])
        sns.despine(left=True, bottom=True)

        patches = [mpatches.Patch(color=v, label=k) for k, v in color_map.items()]
        ax.legend(handles=patches, title="Issue Type", loc="upper left", bbox_to_anchor=(1.02, 1))

    else:
        ax.text(0.5, 0.5, "All data is healthy! 🎉",
                ha='center', va='center', fontsize=20, color='green')
        ax.axis('off')

    plt.tight_layout()
    plt.show()

    print("\n" + "═" * 75)
    print(f"OVERALL DATA HEALTH SCORE : {overall_score}/100")
    print(f"ASSESSMENT                : {overall_rating}")
    print("═" * 75)

    return {
        'overall_score': overall_score,
        'overall_rating': overall_rating,
        'store_health': store_health,
        'missing_columns_with_counts': missing_columns_with_counts,
        'negative_rows': negative_rows,
        'unhealthy_visual': fig,
        'unhealthy_summary': unhealthy_df
    }


# =========================================================
#  MISSING RRP SUMMARY PLOT
# =========================================================

def missing_rrp_summary_plot(
        df,
        supplier_name="BIDCO AFRICA LIMITED",
        supplier_col="Supplier",
        rrp_col="RRP",
        store_col="Store Name"
    ):
    """
    Produces a single clean stacked horizontal bar chart showing
    missing RRP counts by store, separated by:
        - Bidco
        - Other suppliers
    """
     # Filter missing RRP
    missing_df = df[df[rrp_col].isna()].copy()

    if missing_df.empty:
        print("No missing RRP values found.")
        return None

    # Supplier classification column
    missing_df["Supplier Type"] = missing_df[supplier_col].apply(
        lambda x: "Bidco" if x == supplier_name else "Other"
    )

    # Count missing per store & supplier type
    summary = (
        missing_df.groupby([store_col, "Supplier Type"])
        .size()
        .unstack(fill_value=0)
    )

    # Plot
    fig, ax = plt.subplots(figsize=(14, 8))
    summary.plot(
        kind="barh",
        stacked=True,
        color={"Bidco": "orange", "Other": "skyblue"},
        ax=ax
    )

    ax.set_title(
        "Summary of Missing RRP by Store\n(Bidco vs Other Suppliers)",
        fontsize=16,
        weight="bold"
    )
    ax.set_xlabel("Number of Missing RRP Records")
    ax.set_ylabel("Store Name")

    plt.tight_layout()
    plt.show()

    return fig


# =========================================================
#  EXTREME PRICING PLOT
# =========================================================
def plot_rrp_outliers_by_supplier(df, top_n=10):
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Filter relevant columns
    price_df = df[['Store Name', 'Item_Code', 'Description', 'Category', 'RRP', 'Supplier']].copy()
    price_df = price_df.dropna(subset=['RRP'])

    # Detect outliers
    def detect_outliers(group):
        Q1 = group['RRP'].quantile(0.25)
        Q3 = group['RRP'].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        group['Outlier'] = (group['RRP'] < lower) | (group['RRP'] > upper)
        return group

    outliers_df = price_df.groupby('Item_Code', group_keys=False).apply(detect_outliers)

    # Top N products by number of outliers
    top_products = outliers_df[outliers_df['Outlier']]['Description'].value_counts().head(top_n).index
    plot_df = outliers_df[(outliers_df['Description'].isin(top_products)) & (outliers_df['Outlier'])]

    # Summarize number of outliers per product per supplier
    summary_df = plot_df.groupby(['Description', 'Supplier']).size().unstack(fill_value=0)
    affected_suppliers = summary_df.columns[(summary_df.sum(axis=0) > 0)].tolist()
    summary_df = summary_df[affected_suppliers]

    # Plot
    fig, ax = plt.subplots(figsize=(14, 8))
    summary_df.plot(
        kind='barh',
        stacked=True,
        color=sns.color_palette("tab10", n_colors=len(affected_suppliers)),
        ax=ax
    )

    ax.set_title("Top Products with Extreme Pricing (RRP) by Supplier", fontsize=16, weight='bold')
    ax.set_xlabel("Number of Outlier Records")
    ax.set_ylabel("Product Description")
    ax.invert_yaxis()
    ax.legend(title="Supplier", bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.show()
    
    return fig