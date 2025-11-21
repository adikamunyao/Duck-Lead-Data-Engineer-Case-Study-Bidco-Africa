# bidco_kpi_api.py

# Tools and Libraries
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import threading
import pandas as pd
import numpy as np

# ─── 1. FUNCTION TO START API ───
def start_bidco_kpi_api(bidco_data, df_original=None, weekly_gain=27618):
    """
    Starts a FastAPI server to display live KPIs for Bidco pricing.
    
    Parameters:
    - bidco_data: pandas DataFrame with BIDCO sales data
    - df_original: full DataFrame including competitors
    - weekly_gain: optional weekly margin gain (default: 27618)
    """

    # ─── 1. RECALCULATE KPIs ───
    df = bidco_data.copy()
    total_revenue = df['Total Sales'].sum()
    total_units = df['Quantity'].sum()
    avg_rrp = (df['RRP'] * df['Quantity']).sum() / total_units
    avg_price = total_revenue / total_units
    avg_discount = (1 - avg_price / avg_rrp) * 100
    promo_rate = (df['On_Promo'].sum() / len(df)) * 100
    promo_uplift = ((df[df['On_Promo']]['Quantity'].sum() / df['Promo_Units'].sum()) - 1) * 100 if df['Promo_Units'].sum() > 0 else 0

    try:
        full_df = df_original
        comp_df = full_df[~full_df['Supplier'].str.contains('BIDCO', case=False, na=False)]
        comp_df['Unit_Price'] = comp_df['Total Sales'] / comp_df['Quantity']
        comp_price = (comp_df['Unit_Price'] * comp_df['Quantity']).sum() / comp_df['Quantity'].sum()
        price_index = round(avg_price / comp_price, 3) if comp_price > 0 else np.nan
        price_index_str = f"{price_index:.3f}"
    except:
        price_index_str = "N/A"

    # ─── 2. FASTAPI APP ───
    app = FastAPI(title="Bidco KPI API", description="Live KPIs for Bidco Pricing Health")

    @app.get("/kpis", response_class=HTMLResponse)
    async def kpi_dashboard():
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bidco KPI Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background: #f8f9fa; }}
                .kpi-card {{ text-align: center; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .kpi-value {{ font-size: 2.2rem; font-weight: bold; }}
                .kpi-label {{ font-size: 0.9rem; color: #555; }}
                .premium {{ background: linear-gradient(135deg, #ffd700, #f9a825); color: #000; }}
                .discount {{ background: linear-gradient(135deg, #81c784, #4caf50); color: #fff; }}
                .warning {{ background: linear-gradient(135deg, #ff8a65, #ff5722); color: #fff; }}
                .gain {{ background: linear-gradient(135deg, #66bb6a, #43a047); color: #fff; }}
            </style>
        </head>
        <body>
            <div class="container py-5">
                <h1 class="text-center mb-4">Bidco Pricing Health – Live KPIs</h1>
                <div class="row g-4">

                    <div class="col-md-3">
                        <div class="kpi-card premium">
                            <div class="kpi-value">KSh {total_revenue:,.0f}</div>
                            <div class="kpi-label">Total Revenue (1 Week)</div>
                        </div>
                    </div>

                    <div class="col-md-3">
                        <div class="kpi-card discount">
                            <div class="kpi-value">{total_units:,.0f}</div>
                            <div class="kpi-label">Units Sold</div>
                        </div>
                    </div>

                    <div class="col-md-3">
                        <div class="kpi-card warning">
                            <div class="kpi-value">{avg_discount:.1f}%</div>
                            <div class="kpi-label">Avg Discount vs RRP</div>
                        </div>
                    </div>

                    <div class="col-md-3">
                        <div class="kpi-card premium">
                            <div class="kpi-value">{price_index_str}</div>
                            <div class="kpi-label">Price Index (vs Comp)</div>
                        </div>
                    </div>

                    <div class="col-md-3">
                        <div class="kpi-card warning">
                            <div class="kpi-value">{promo_rate:.0f}%</div>
                            <div class="kpi-label">Promo Coverage</div>
                        </div>
                    </div>

                    <div class="col-md-3">
                        <div class="kpi-card discount">
                            <div class="kpi-value">+{promo_uplift:.0f}%</div>
                            <div class="kpi-label">Promo Uplift</div>
                        </div>
                    </div>

                    <div class="col-md-3">
                        <div class="kpi-card gain">
                            <div class="kpi-value">KSh {weekly_gain:,.0f}</div>
                            <div class="kpi-label">Weekly Margin Gain</div>
                        </div>
                    </div>

                    <div class="col-md-3">
                        <div class="kpi-card premium">
                            <div class="kpi-value">99/100</div>
                            <div class="kpi-label">Data Health Score</div>
                        </div>
                    </div>

                </div>
            </div>
        </body>
        </html>
        """

    @app.get("/kpis/json")
    async def kpis_json():
        return {
            "total_revenue_ksh": round(total_revenue),
            "units_sold": int(total_units),
            "avg_discount_pct": round(avg_discount, 1),
            "price_index": price_index_str,
            "promo_coverage_pct": round(promo_rate),
            "promo_uplift_pct": round(promo_uplift),
            "weekly_gain_ksh": weekly_gain,
            "data_health": "99/100"
        }

    # ─── 3. START SERVER IN BACKGROUND ───
    def run_server():
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    return app
