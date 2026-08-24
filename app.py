import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Olist Executive Dashboard", layout="wide")

# Load unified dataset
@st.cache_data
def load_data():
    orders = pd.read_csv("Data/olist_orders_dataset.csv")
    order_items = pd.read_csv("Data/olist_order_items_dataset.csv")
    products = pd.read_csv("Data/olist_products_dataset.csv")
    translation = pd.read_csv("Data/product_category_name_translation.csv")
    customers = pd.read_csv("Data/olist_customers_dataset.csv")

    products = products.merge(translation, on="product_category_name", how="left")
    products["category"] = products["product_category_name_english"].fillna("other")
    
    orders = orders[orders["order_status"] == "delivered"].copy()
    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
    orders["order_month"] = orders["order_purchase_timestamp"].dt.to_period("M").astype(str)

    df = order_items.merge(orders, on="order_id", how="inner") \
                    .merge(products, on="product_id", how="left") \
                    .merge(customers, on="customer_id", how="left")
    return df

df = load_data()

st.title("Olist E-Commerce Performance Dashboard")

# Top KPI Row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_revenue = df["price"].sum()
total_orders = df["order_id"].nunique()
top_category = df.groupby("category")["price"].sum().idxmax()
best_month = df.groupby("order_month")["price"].sum().idxmax()

kpi1.metric("Total Revenue", f"R$ {total_revenue:,.2f}")
kpi2.metric("Delivered Orders", f"{total_orders:,}")
kpi3.metric("Top Category", top_category.replace("_", " ").title())
kpi4.metric("Best Month", best_month)

st.divider()

# Visual Grid
col1, col2 = st.columns(2)

with col1:
    top_cat_df = df.groupby("category")["price"].sum().nlargest(10).reset_index()
    fig_cat = px.bar(top_cat_df, x="price", y="category", orientation="h",
                     title="Top 10 Product Categories by Revenue",
                     labels={"price": "Revenue (R$)", "category": "Category"},
                     color="price", color_continuous_scale="Blues")
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    monthly_df = df.groupby("order_month")["price"].sum().reset_index()
    fig_month = px.line(monthly_df, x="order_month", y="price", markers=True,
                        title="Monthly Revenue Trend",
                        labels={"order_month": "Month", "price": "Revenue (R$)"})
    st.plotly_chart(fig_month, use_container_width=True)