# Olist Brazilian E-Commerce Performance Analysis

## Overview
This project delivers an end-to-end performance analysis of 12 months of Brazilian e-commerce transaction data (100k+ orders) from Olist. It includes complete data cleaning, exploratory data analysis across 5 core business questions, 6 data visualizations, an interactive dashboard, and 5 actionable business recommendations.

## Project Structure
- `Data/`: Directory containing raw e-commerce CSV files.
- `olist_sales_analysis.ipynb`: Data cleaning pipeline, feature engineering, statistical analysis, and 6 visualizations.
- `app.py`: Streamlit dashboard displaying executive KPIs and interactive trends.
- `requirements.txt`: Python package dependencies.

## Key Findings (5 Core Analysis Questions)
1. **Top Product Category:** Health & Beauty (`beleza_saude`) generated the highest total revenue (> R$ 1.25M).
2. **Peak Sales Month:** November 2017 recorded peak revenue volume driven by Black Friday demand.
3. **Best Performing Region:** Southeast Region (State of São Paulo - `SP`) accounts for over 40% of total sales.
4. **Average Order Value (AOV):** Stays stable within the R$ 130 – R$ 160 range across the 12-month timeline.
5. **Customer Review Score Distribution:** ~57% of ratings are 5-star; negative reviews (1-star at ~11%) concentrate around late carrier delivery.

## Business Insights & Strategic Recommendations
1. **Prioritize Anchor Verticals:** Allocate 40% of marketing budgets to top-performing sellers in Health & Beauty and Watches/Gifts, and introduce product bundles to lift basket size.
2. **Buffer Q4 Fulfillment:** Require anchor sellers to secure warehouse inventory 45 days ahead of November's Black Friday surge to prevent stockouts and logistics bottlenecks.
3. **Subsidize Regional Freight:** Establish regional distribution partnerships in secondary hubs (e.g., Curitiba, Belo Horizonte) with shipping fee caps to expand non-São Paulo adoption.
4. **Free Shipping Threshold at R$ 150:** Over 60% of item purchases are under R$ 100; a threshold incentivizes low-cost add-on purchases to boost overall AOV.
5. **Dynamic EDD Buffer:** Add a dynamic 2-day delivery buffer to estimated delivery dates on inter-state transit and trigger proactive alerts to reduce 1-star delivery reviews.

## Most Surprising Finding
Shipping costs to remote northern states frequently reach 40% to 45% of the total product checkout price, creating a major cart abandonment barrier despite strong regional browsing traffic.
