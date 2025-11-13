# Bidco Pricing & Promo Health Check 
**One-Week Retail Data Analysis**  
*Prepared by Munyao Emmanuel Adika | Duck – Retail Data Layer for Africa*  
*Date: November 12, 2025*

---

## Executive Summary
<img width="1056" height="472" alt="image" src="https://github.com/user-attachments/assets/6b407a3f-31d0-4839-8e8f-01c3a0ebbee1" />

**Action**: **Reduce discounts in Sunflower Oil, Other Flavor, Baking Powder** → **+KSh 27,618/week margin gain**

---

## Objective

Bidco wants to understand:
1. **Promo effectiveness** — are promotions driving volume?
2. **Price positioning** — are we premium, discount, or balanced vs competitors?
3. **Data reliability** — can we trust the numbers?

---
## Data
We analyzed **1 week of sales data**  from a major retailer to deliver **actionable KPIs** and **pricing fixes**.

| **Column**         | **Description**                                                                       |
| ------------------ | ------------------------------------------------------------------------------------- |
| **Store Name**     | Name of the retail outlet or branch.                          |
| **Item_Code**      | Unique internal identifier for the product within the retailer’s system.              |
| **Item Barcode**   | Standard barcode identifier (EAN/UPC).                                                |
| **Description**    | Human-readable SKU description.                                                       |
| **Category**       | Broad product grouping.                               |
| **Department**     | Mid-level grouping within a category (e.g., “Cooking Essentials”).                    |
| **Sub-Department** | More refined classification for analytical grouping.                                  |
| **Section**        | Micro-segmentation within the Sub-Department, often representing brand or format.     |
| **Quantity**       | Number of units sold during the transaction period.                                   |
| **Total Sales**    | Total value of items sold — calculated as *Quantity × Realized Price*.                |
| **RRP**            | Recommended Retail Price — benchmark price before discounts or promotions.            |
| **Supplier**       | Supplier or distributor for the product. |
| **Date Of Sale**   | Date of the transaction.                         |
---

### 1. Data Health – Trust the Numbers
<img width="762" height="207" alt="image" src="https://github.com/user-attachments/assets/fb333e53-640d-4648-861a-73e1dfd8230a" />

> **Verdict**: Data is **clean and trustworthy**. One minor outlier — excluded from KPIs.

---

## 2. Promotions & Performance

| KPI | Value | Insight |
|-----|-------|--------|
| **Promo Coverage** | **95%** | Nearly all SKUs promoted |
| **Promo Uplift** | **+7%** | Modest volume lift |
| **Avg Promo Discount** | **14.2%** | Deep cuts, low return |
| **Top Uplift SKU** | Sunflower Oil 1L | +18% units |
| **Worst ROI** | Baking Powder | 22% off → -3% uplift |

> **Insight #1**: **Promotions are overused** — 95% coverage but only **+7% uplift**.  
> **Insight #2**: **Sunflower Oil responds well** — keep promo, but **reduce depth**.  
> **Insight #3**: **Baking Powder promo fails** — stop or test shallower discount.

---

## 3. Pricing Index – Are We Too Expensive?

| KPI | Value | Positioning |
|-----|-------|-------------|
| **Overall Price Index** | **2.126** | **Premium (2.1x competitors)** |
| **Store-Level Range** | 1.89 – 2.41 | Consistent premium |
| **Avg Discount vs RRP** | **12.9%** | Heavy discounting despite high price |

### Store-Level View (Top 3)

| Store | Price Index | Positioning | Action |
|------|-------------|-------------|--------|
| Store 02 | 2.41 | Ultra-Premium | **Cut discount** |
| Store 09 | 2.18 | Premium | **Reduce promo depth** |
| Store 05 | 1.89 | High-Premium | **Keep** |

> **Insight #4**: Bidco is **priced 2.1x above competitors** — **premium positioning is real**, but **deep discounts erode margin**.

---

## 4. Margin Opportunity – Exact KSh Gain

We modeled **raising prices to 9% off RRP** (from current 12.9%) in **3 high-volume sections**:

| Section | Current Discount | Units | Gain/Week |
|--------|------------------|-------|----------|
| **Sunflower Oil** | 18.2% | 1,200 | **+KSh 14,400** |
| **Other Flavor** | 16.8% | 480 | **+KSh 8,640** |
| **Baking Powder** | 22.1% | 210 | **+KSh 4,578** |

> **Total Weekly Gain**: **+KSh 27,618**  
> **Annualized**: **+KSh 1.44M**

---

## Recommendations

| # | Action | Owner | Impact |
|---|--------|-------|--------|
| 1 | **Reduce Sunflower Oil discount** from 18.2% → **9%** | Trade Team | **+KSh 14.4K/week** |
| 2 | **Cut Other Flavor promo** from 16.8% → **9%** | Marketing | **+KSh 8.6K/week** |
| 3 | **Stop Baking Powder promo** (or test 10%) | Category Lead | **+KSh 4.6K/week** |
| 4 | **Protect premium SKUs** (CSD, Tabs) at <5% discount | All | Maintain brand equity |

---

## Assumptions & Logic

- **Bidco SKUs**: Filtered by `Supplier.contains('BIDCO')`
- **Competitors**: All non-Bidco SKUs in same `Section`
- **Price Index**: `Bidco Unit Price / Competitor Avg Unit Price` (volume-weighted)
- **Promo Detection**: `On_Promo == True` + `Discount_Pct > 5%`
- **Baseline**: `Baseline_Units` field used for uplift
- **Gain Calculation**: `(RRP × 0.91) - Current Price` × Units

---
## Conclusion

This one-week analysis of Bidco’s retail performance reveals a clear, high-confidence opportunity: while Bidco commands a strong premium positioning (Price Index = 2.126), it is undermining its own margin through overuse of deep discounts — averaging 12.9% off RRP and reaching 22% in key sections.Despite 95% of SKUs on promotion, volume uplift is only +7%, indicating diminishing returns and margin erosion. The data is highly reliable (98/100 health score), giving us full confidence in the findings.By recalibrating just three high-volume sections — Sunflower Oil, Other Flavor, and Baking Powder — to a disciplined 9% discount vs RRP, Bidco can unlock KSh 27,618 in weekly margin — equivalent to KSh 1.44 million annually — without sacrificing volume.This is not a pricing problem. It’s a discipline opportunity.Bidco is already winning on brand equity and shelf presence. Now, it must win on margin discipline.

---
**Let’s turn data into profit.**  
Munyao Emmanuel Adika  
[adikamunyao@gmail.com](mailto:adikamunyao@gmail.com)
