import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Olist Executive Sales Dashboard", page_icon="📈", layout="wide"
)


# --- Data Pipeline ---
@st.cache_data
def load_and_prep_data():
  orders = pd.read_csv("Data/olist_orders_dataset.csv")
  order_items = pd.read_csv("Data/olist_order_items_dataset.csv")
  products = pd.read_csv("Data/olist_products_dataset.csv")
  customers = pd.read_csv("Data/olist_customers_dataset.csv")
  reviews = pd.read_csv("Data/olist_order_reviews_dataset.csv")
  translation = pd.read_csv("Data/product_category_name_translation.csv")

  # English translation
  products = products.merge(
      translation, on="product_category_name", how="left"
  )
  products["category"] = (
      products["product_category_name_english"]
      .fillna("other")
      .str.replace("_", " ")
      .str.title()
  )

  # Filter delivered orders and parse dates
  orders = orders[orders["order_status"] == "delivered"].copy()
  date_cols = [
      "order_purchase_timestamp",
      "order_delivered_customer_date",
      "order_estimated_delivery_date",
  ]
  for col in date_cols:
    orders[col] = pd.to_datetime(orders[col])

  orders["order_month"] = orders["order_purchase_timestamp"].dt.to_period("M")
  orders["order_month_str"] = orders["order_month"].astype(str)

  # Delivery delta (Late flag)
  orders["delivery_days"] = (
      orders["order_delivered_customer_date"]
      - orders["order_purchase_timestamp"]
  ).dt.days
  orders["is_delayed"] = (
      orders["order_delivered_customer_date"]
      > orders["order_estimated_delivery_date"]
  )

  # Deduplicate reviews
  reviews = reviews.sort_values("review_creation_date").drop_duplicates(
      "order_id", keep="last"
  )

  # Unified table
  df = (
      order_items.merge(orders, on="order_id", how="inner")
      .merge(products, on="product_id", how="left")
      .merge(customers, on="customer_id", how="left")
      .merge(reviews[["order_id", "review_score"]], on="order_id", how="left")
  )
  df["freight_ratio"] = (df["freight_value"] / df["price"]) * 100
  return df


df = load_and_prep_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Executive Filters")

# 1. State Filter
all_states = sorted(df["customer_state"].dropna().unique())
selected_states = st.sidebar.multiselect(
    "Select Customer States", all_states, default=[]
)

# 2. Year Filter
years = sorted(df["order_purchase_timestamp"].dt.year.unique().tolist())
selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)

# 3. Minimum Review Score Filter
min_score = st.sidebar.slider(
    "Minimum Review Score", min_value=1, max_value=5, value=1
)

# Apply Filters
filtered_df = df[
    (df["order_purchase_timestamp"].dt.year.isin(selected_years))
    & (df["review_score"] >= min_score)
]

if selected_states:
  filtered_df = filtered_df[filtered_df["customer_state"].isin(selected_states)]

# --- Top Level Metrics ---
st.title("Olist E-Commerce Performance & Operations")
st.caption("Executive Overview • Delivered Orders • 27 Brazilian States")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
total_rev = filtered_df["price"].sum()
total_orders = filtered_df["order_id"].nunique()
aov = total_rev / total_orders if total_orders else 0
avg_review = filtered_df["review_score"].mean()
delay_rate = (filtered_df["is_delayed"].mean()) * 100

kpi1.metric("Gross Revenue", f"R$ {total_rev:,.2f}")
kpi2.metric("Delivered Orders", f"{total_orders:,}")
kpi3.metric("Avg Order Value (AOV)", f"R$ {aov:,.2f}")
kpi4.metric(
    "Avg Review Score", f"{avg_review:.2f} / 5.0" if total_orders else "N/A"
)
kpi5.metric("Delivery Delay Rate", f"{delay_rate:.1f}%")

st.divider()

# --- Row 1: Revenue Trends & Category Power ---
col1, col2 = st.columns(2)

with col1:
  monthly_data = (
      filtered_df.groupby("order_month_str")
      .agg(
          monthly_rev=("price", "sum"),
      )
      .reset_index()
  )

  fig_trend = go.Figure()
  fig_trend.add_trace(
      go.Scatter(
          x=monthly_data["order_month_str"],
          y=monthly_data["monthly_rev"],
          mode="lines+markers",
          name="Revenue (R$)",
          line=dict(color="#1f77b4", width=3),
      )
  )
  fig_trend.update_layout(
      title="<b>Monthly Sales Trajectory</b>",
      xaxis_title="Month",
      yaxis_title="Revenue (R$)",
      hovermode="x unified",
      margin=dict(l=20, r=20, t=40, b=20),
  )
  st.plotly_chart(fig_trend, use_container_width=True)

with col2:
  cat_rev = (
      filtered_df.groupby("category")["price"]
      .sum()
      .nlargest(10)
      .sort_values(ascending=True)
      .reset_index()
  )
  fig_cat = px.bar(
      cat_rev,
      x="price",
      y="category",
      orientation="h",
      title="<b>Top 10 Product Categories by Revenue</b>",
      labels={"price": "Gross Revenue (R$)", "category": "Product Category"},
      color="price",
      color_continuous_scale="Blues",
  )
  fig_cat.update_layout(
      showlegend=False, margin=dict(l=20, r=20, t=40, b=20)
  )
  st.plotly_chart(fig_cat, use_container_width=True)

# --- Row 2: Regional Performance & Customer Experience ---
col3, col4 = st.columns(2)

with col3:
  state_df = (
      filtered_df.groupby("customer_state")
      .agg(revenue=("price", "sum"), orders=("order_id", "nunique"))
      .reset_index()
      .nlargest(10, "revenue")
  )
  fig_state = px.bar(
      state_df,
      x="customer_state",
      y="revenue",
      title="<b>Regional Sales Performance: Top 10 States</b>",
      labels={"customer_state": "State", "revenue": "Sales (R$)"},
      color="revenue",
      color_continuous_scale="Teal",
  )
  fig_state.update_layout(margin=dict(l=20, r=20, t=40, b=20))
  st.plotly_chart(fig_state, use_container_width=True)

with col4:
  score_counts = (
      filtered_df["review_score"]
      .dropna()
      .value_counts()
      .sort_index(ascending=False)
      .reset_index()
  )
  score_counts.columns = ["Score", "Count"]
  score_counts["Score"] = score_counts["Score"].astype(int).astype(str) + " ⭐"

  fig_pie = px.pie(
      score_counts,
      names="Score",
      values="Count",
      title="<b>Review Sentiment Distribution</b>",
      hole=0.45,
      color_discrete_sequence=[
          "#2ca02c",
          "#8cd3ff",
          "#ffbb78",
          "#ff7f0e",
          "#d62728",
      ],
  )
  fig_pie.update_layout(margin=dict(l=20, r=20, t=40, b=20))
  st.plotly_chart(fig_pie, use_container_width=True)

# --- Row 3: Operational Diagnostic (Delivery Delays vs Ratings) ---
st.subheader("Operational Diagnostic: Delivery Transit vs Customer Ratings")
delay_review_df = (
    filtered_df.groupby("review_score")
    .agg(
        avg_delivery_days=("delivery_days", "mean"),
        delay_percentage=("is_delayed", lambda x: (x.mean()) * 100),
    )
    .reset_index()
)

fig_driver = go.Figure()
fig_driver.add_trace(
    go.Bar(
        x=delay_review_df["review_score"],
        y=delay_review_df["avg_delivery_days"],
        name="Avg Transit Days",
        marker_color="#3366cc",
    )
)
fig_driver.add_trace(
    go.Scatter(
        x=delay_review_df["review_score"],
        y=delay_review_df["delay_percentage"],
        name="Late Delivery Probability (%)",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="#dc3912", width=3),
    )
)
fig_driver.update_layout(
    title="<b>Correlation: Impact of Transit Time & Delays on Review Scores</b>",
    xaxis=dict(title="Review Score (1 to 5 Stars)"),
    yaxis=dict(title="Avg Transit Days"),
    yaxis2=dict(
        title="Late Delivery Probability (%)", overlaying="y", side="right"
    ),
    legend=dict(x=0.75, y=1.15, orientation="h"),
    margin=dict(l=20, r=20, t=50, b=20),
)
st.plotly_chart(fig_driver, use_container_width=True)