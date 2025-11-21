# bidco_promo_pipeline.py
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns


class BIDCOPromoAnalyzer:
    """
    One-stop pipeline for BIDCO promotional discount analysis.
    Just do:
        analyzer = BIDCOPromoAnalyzer(df)
        analyzer.show_all_charts()
    """
    
    def __init__(self, df: pd.DataFrame, supplier_name: str = "BIDCO AFRICA LIMITED"):
        self.df = df.copy()
        self.supplier = supplier_name
        self.bidco = self._prepare_data()
    
    def _prepare_data(self):
        data = self.df[self.df['Supplier'] == self.supplier].copy()
        data = data[data['Quantity'] > 0].copy()
        
        # Clean Unit Price & true Discount %
        data['Unit_Price'] = data['Total Sales'] / data['Quantity']
        data['Discount_Pct'] = ((data['RRP'] - data['Unit_Price']) / data['RRP']) * 100
        
        # Filter nonsense
        data = data[(data['Discount_Pct'] >= 0) & (data['Discount_Pct'] < 100)]
        data['Status'] = data['On_Promo'].map({True: 'On Promotion', False: 'Regular Price'})
        
        # Discount buckets
        bins = [0, 10, 20, 30]
        labels = ['0-10%', '10-20%', '20-30%']
        data['Discount_Bucket'] = pd.cut(data['Discount_Pct'], bins=bins, labels=labels)
        
        return data
    
    def section_summary(self):
        """Returns the improved section-level summary table"""
        summary = (
            self.bidco.groupby('Section')
            .agg(
                Total_Qty=('Quantity', 'sum'),
                Total_Sales=('Total Sales', 'sum'),
                Avg_RRP=('RRP', 'mean'),
                Avg_Unit_Price=('Unit_Price', 'mean'),
                Avg_Discount_Pct=('Discount_Pct', 'mean'),
                Median_Discount_Pct=('Discount_Pct', 'median'),
                Transactions=('Item_Code', 'count')
            )
            .round(2)
            .reset_index()
            .sort_values('Avg_Discount_Pct', ascending=False)
        )
        return summary
    
    def chart_discount_distribution(self):
        fig = px.histogram(
            self.bidco, x='Discount_Pct', color='Status', nbins=40, marginal="box",
            title="BIDCO Discount Depth Distribution",
            labels={'Discount_Pct': 'Discount % off RRP'},
            color_discrete_map={'On Promotion': '#E63946', 'Regular Price': '#2A9D8F'}
        )
        fig.update_layout(barmode='overlay', bargap=0.1, height=550)
        fig.update_traces(opacity=0.75)
        fig.show()
    
    def chart_deep_discounts_by_section(self):
        summary = self.section_summary()
        fig = px.bar(
            summary.head(20),
            x='Section', y='Avg_Discount_Pct',
            text='Avg_Discount_Pct',
            color='Total_Qty',
            title="Top 20 BIDCO Sections by Average Discount Depth<br><sub>Bigger bar = more units sold</sub>",
            labels={'Avg_Discount_Pct': 'Avg Discount %'}
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(xaxis_tickangle=45, height=600)
        fig.show()
    
    def chart_promo_effectiveness_bubbles(self):
        bucket = self.bidco[self.bidco['On_Promo']].groupby('Discount_Bucket').agg({
            'Quantity': ['sum', 'mean'],
            'Total Sales': 'sum',
            'Item_Code': 'count'
        }).round(1)
        bucket.columns = ['Total_Qty', 'Avg_Qty_per_Trans', 'Total_Revenue', 'Transactions']
        bucket = bucket.reset_index()
        
        fig = px.scatter(
            bucket,
            x='Discount_Bucket',
            y='Avg_Qty_per_Trans',
            size='Total_Qty',
            color='Total_Revenue',
            title="Promo Effectiveness by Discount Depth<br><sub>Bubble size = Total Volume | Color = Total Revenue</sub>",
            labels={'Avg_Qty_per_Trans': 'Avg Units per Transaction', 'Discount_Bucket': 'Discount Band'}
        )
        fig.update_layout(height=600)
        fig.show()
    
    def chart_efficiency_quadrant(self):
        promo = self.bidco[self.bidco['On_Promo']].copy()
        promo['Revenue_per_Discount_Point'] = promo['Total Sales'] / (promo['Discount_Pct'] + 0.01)
        
        fig = px.scatter(
            promo,
            x='Discount_Pct',
            y='Quantity',
            size='Total Sales',
            color='Revenue_per_Discount_Point',
            hover_data=['Description', 'Section', 'Item_Code'],
            title="BIDCO Promo Efficiency Quadrant<br>Top-Right (shallow discount + high volume) = WINNERS",
            color_continuous_scale='RdYlGn',
            labels={'Revenue_per_Discount_Point': 'Revenue per % Discounted (Higher = Better)'}
        )
        fig.add_vline(x=25, line_dash="dash", line_color="orange", annotation_text="25% Threshold")
        fig.add_hline(y=promo['Quantity'].quantile(0.75), line_dash="dash", line_color="orange")
        fig.update_layout(height=650)
        fig.show()
    
    def chart_discount_vs_volume_density(self):
        """
        New Chart: KDE Density Heatmap – shows where the 'sweet spot' really is
        """
        summary = self.section_summary()
        
        plt.figure(figsize=(11, 7))
        sns.kdeplot(
            data=summary,
            x='Avg_Discount_Pct',
            y='Total_Qty',
            fill=True,
            cmap='viridis',
            thresh=0.05,
            levels=100,
            alpha=0.9
        )
        
        # Overlay the actual points (makes it crystal clear)
        sns.scatterplot(
            data=summary,
            x='Avg_Discount_Pct',
            y='Total_Qty',
            size=summary['Total_Sales'],
            sizes=(50, 800),
            color='white',
            edgecolor='black',
            linewidth=1,
            alpha=0.8,
            legend=False
        )
        
        plt.title("BIDCO Promo Sweet Spot\n(Denser yellow = more categories clustered there)", 
                  fontsize=16, fontweight='bold', pad=20)
        plt.xlabel("Average Discount Depth (%)", fontsize=12)
        plt.ylabel("Total Units Sold per Section", fontsize=12)
        
        # Highlight the 15–20% zone
        plt.axvline(15, color='orange', linestyle='--', alpha=0.8)
        plt.axvline(20, color='orange', linestyle='--', alpha=0.8)
        plt.text(17.5, plt.ylim()[1]*0.92, "SWEET SPOT\n15–20%", ha='center', color='orange', 
                 fontsize=12, fontweight='bold', bbox=dict(facecolor='white', alpha=0.7))
        
        plt.tight_layout()
        plt.show()

    def show_all_charts(self):
        """Now includes the new density chart"""
        print(f"Analyzing {len(self.bidco):,} BIDCO transactions...\n")
        self.chart_discount_distribution()
        self.chart_deep_discounts_by_section()
        self.chart_promo_effectiveness_bubbles()
        self.chart_efficiency_quadrant()
        self.chart_discount_vs_volume_density()   # ← NEW: the killer density map
        print("All 5 BIDCO insights complete!")