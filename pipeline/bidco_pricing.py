from IPython.display import display, Markdown

def generate_bidco_pricing_strategy(store_summary, overall_index):
    """
    Generates the Bidco Pricing Strategy action plan,
    displays styled tables, and prints summary insights.

    Parameters
    ----------
    store_summary : pd.DataFrame
        Must contain columns:
        ['Store Name', 'Avg_Price_Index', 'Avg_Discount', 'Positioning']
    overall_index : float
        Overall price index for final summary text.
    """

    display(Markdown("## **Bidco Pricing Strategy – Store Action Plan**"))

    # ─────────────────────────────────────────────────────────────
    # No competitor data case
    # ─────────────────────────────────────────────────────────────
    if len(store_summary) == 0 or store_summary['Avg_Price_Index'].isna().all():
        display(Markdown("""
        **No competitor data found** – cannot compare Bidco vs rivals.  
        Bidco may be the **only supplier** in these categories.  
        **Next step**: Use **discount vs RRP** to manage margins.
        """))
        return None

    # ─────────────────────────────────────────────────────────────
    # Compute action column
    # ─────────────────────────────────────────────────────────────
    def get_action(row):
        idx = row['Avg_Price_Index']
        disc = row['Avg_Discount']
        store = row['Store Name']

        if idx < 1.0 and disc > 8:
            return f"**{store}**: Too cheap + deep discount → **Reduce promo**"
        elif idx > 1.0 and disc > 8:
            return f"**{store}**: Expensive + deep discount → **Cut discount**"
        elif idx < 1.0 and disc <= 8:
            return f"**{store}**: Too cheap → **Raise price +5%**"
        elif idx > 1.0 and disc <= 8:
            return f"**{store}**: Premium + low discount → **Keep – winning!**"
        else:
            return f"**{store}**: Balanced – monitor"

    store_summary['Action'] = store_summary.apply(get_action, axis=1)

    # ─────────────────────────────────────────────────────────────
    # Styling helper
    # ─────────────────────────────────────────────────────────────
    def color_action(val):
        if "Reduce promo" in val:     return 'background-color: #FFCDD2; color: #B71C1C; font-weight: bold'
        if "Cut discount" in val:     return 'background-color: #FFEBEE; color: #B71C1C; font-weight: bold'
        if "Raise price" in val:      return 'background-color: #E8F5E9; color: #1B5E20; font-weight: bold'
        if "Keep" in val:             return 'background-color: #FFF8E1; color: #FF8F00; font-weight: bold'
        return ''

    # ─────────────────────────────────────────────────────────────
    # Prepare table
    # ─────────────────────────────────────────────────────────────
    table = store_summary[['Store Name', 'Avg_Price_Index', 'Avg_Discount', 'Positioning', 'Action']].copy()
    table['Avg_Price_Index'] = table['Avg_Price_Index'].round(3)
    table['Avg_Discount'] = table['Avg_Discount'].round(1).astype(str) + '%'

    # Sort by urgency
    urgency_order = {
        "Reduce promo": 1,
        "Cut discount": 2,
        "Raise price": 3,
        "Keep": 4,
        "Balanced": 5
    }

    table['urgency'] = table['Action'].apply(
        lambda x: urgency_order.get(x.split('→')[1].strip().split()[0], 6)
    )
    table = table.sort_values('urgency').drop('urgency', axis=1)

    # Display styled table
    styled = (
        table.style
        .format({'Avg_Price_Index': '{:.3f}'})
        .applymap(color_action, subset=['Action'])
        .set_table_attributes('style="font-size: 14px"')
        .set_caption("Bidco Pricing Strategy – What to Do in Each Store")
    )

    display(styled)

    # ─────────────────────────────────────────────────────────────
    # Summary insight
    # ─────────────────────────────────────────────────────────────
    red = len(table[table['Action'].str.contains("Reduce|Cut")])
    green = len(table[table['Action'].str.contains("Raise")])
    gold = len(table[table['Action'].str.contains("Keep")])
    return table
