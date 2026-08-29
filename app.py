import streamlit as st
import pandas as pd
import numpy as np

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="FORESIGHT | Retail Demand Intelligence",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }

    .hero {
        padding: 1.5rem 0 1rem 0;
    }

    .hero h1 {
        font-size: 42px;
        margin-bottom: 0;
    }

    .hero p {
        font-size: 18px;
        color: #777;
    }

    .kpi {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #ddd;
        background: #ffffff;
    }

    .section-title {
        font-size: 24px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    .alert-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>FORESIGHT</h1>
    <p>Retail Demand Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.title("⚙️ Control Center")

st.sidebar.subheader("Data Source")

uploaded_file = st.sidebar.file_uploader(
    "Upload sales CSV",
    type=["csv"]
)

# ---------------------------------------------------------
# DATA
# ---------------------------------------------------------
if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

        st.sidebar.success("CSV loaded successfully")

    except Exception:
        st.error("Unable to read the CSV file.")
        st.stop()

else:

    # Demo data
    np.random.seed(42)

    dates = pd.date_range(
        end=pd.Timestamp.today().normalize(),
        periods=120
    )

    products = ["Product A", "Product B", "Product C", "Product D"]

    data = []

    for date in dates:
        for product in products:

            base = {
                "Product A": 180,
                "Product B": 140,
                "Product C": 220,
                "Product D": 100
            }[product]

            demand = max(
                0,
                int(base + np.random.normal(0, 25))
            )

            price = {
                "Product A": 499,
                "Product B": 699,
                "Product C": 899,
                "Product D": 399
            }[product]

            data.append({
                "Date": date,
                "Product": product,
                "Sales": demand,
                "Price": price
            })

    df = pd.DataFrame(data)

# ---------------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------------
if "Date" not in df.columns:
    st.error("Your CSV must contain a 'Date' column.")
    st.stop()

if "Sales" not in df.columns:
    st.error("Your CSV must contain a 'Sales' column.")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")

df = df.dropna(subset=["Date", "Sales"])

# ---------------------------------------------------------
# FILTERS
# ---------------------------------------------------------
st.sidebar.subheader("Filters")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:

    start_date, end_date = date_range

    filtered_df = df[
        (df["Date"].dt.date >= start_date) &
        (df["Date"].dt.date <= end_date)
    ].copy()

else:
    filtered_df = df.copy()

if "Product" in filtered_df.columns:

    product_options = sorted(
        filtered_df["Product"].dropna().unique()
    )

    selected_products = st.sidebar.multiselect(
        "Products",
        product_options,
        default=product_options
    )

    if selected_products:
        filtered_df = filtered_df[
            filtered_df["Product"].isin(selected_products)
        ]

# ---------------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------------
total_sales = filtered_df["Sales"].sum()

average_daily_demand = (
    filtered_df.groupby("Date")["Sales"]
    .sum()
    .mean()
)

peak_demand = (
    filtered_df.groupby("Date")["Sales"]
    .sum()
    .max()
)

days_in_data = filtered_df["Date"].nunique()

# Forecast based on recent demand
daily_sales = (
    filtered_df.groupby("Date")["Sales"]
    .sum()
    .sort_index()
)

recent_days = min(14, len(daily_sales))

forecast_demand = (
    daily_sales.tail(recent_days).mean()
    if recent_days > 0
    else 0
)

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title">📊 Executive Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Units Sold",
        f"{total_sales:,.0f}"
    )

with col2:
    st.metric(
        "Average Daily Demand",
        f"{average_daily_demand:,.0f}"
    )

with col3:
    st.metric(
        "Peak Daily Demand",
        f"{peak_demand:,.0f}"
    )

with col4:
    st.metric(
        "14-Day Forecast",
        f"{forecast_demand:,.0f}"
    )

# ---------------------------------------------------------
# DEMAND TREND
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title">📈 Demand Trend</div>',
    unsafe_allow_html=True
)

trend_df = daily_sales.rename("Demand")

st.line_chart(
    trend_df,
    height=350
)

# ---------------------------------------------------------
# FORECAST
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title">🤖 Demand Forecast</div>',
    unsafe_allow_html=True
)

forecast_days = st.slider(
    "Forecast horizon",
    min_value=7,
    max_value=30,
    value=14
)

if len(daily_sales) >= 7:

    window = min(14, len(daily_sales))

    moving_average = daily_sales.tail(window).mean()

    forecast_dates = pd.date_range(
        start=daily_sales.index.max() + pd.Timedelta(days=1),
        periods=forecast_days
    )

    forecast_df = pd.DataFrame({
        "Forecast": [
            moving_average
            for _ in range(forecast_days)
        ]
    }, index=forecast_dates)

    st.line_chart(
        forecast_df,
        height=300
    )

    st.info(
        f"Forecast is based on the latest {window} days "
        f"of observed demand."
    )

# ---------------------------------------------------------
# PRODUCT PERFORMANCE
# ---------------------------------------------------------
if "Product" in filtered_df.columns:

    st.markdown(
        '<div class="section-title">🏆 Product Performance</div>',
        unsafe_allow_html=True
    )

    product_sales = (
        filtered_df.groupby("Product")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(
        product_sales,
        height=350
    )

    # Top products table
    performance = product_sales.reset_index()

    performance.columns = [
        "Product",
        "Units Sold"
    ]

    performance["Share of Sales"] = (
        performance["Units Sold"] /
        performance["Units Sold"].sum() * 100
    ).round(1)

    st.dataframe(
        performance,
        use_container_width=True,
        hide_index=True
    )

# ---------------------------------------------------------
# INVENTORY INTELLIGENCE
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title">🚨 Inventory Intelligence</div>',
    unsafe_allow_html=True
)

safety_stock = forecast_demand * 0.25
recommended_inventory = forecast_demand * 14 + safety_stock

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Forecast / Day",
        f"{forecast_demand:,.0f}"
    )

with col2:
    st.metric(
        "Safety Stock",
        f"{safety_stock:,.0f}"
    )

with col3:
    st.metric(
        "Recommended 14-Day Stock",
        f"{recommended_inventory:,.0f}"
    )

if forecast_demand > average_daily_demand * 1.10:

    st.warning(
        "⚠️ Demand appears to be increasing. "
        "Consider increasing inventory before the next demand cycle."
    )

elif forecast_demand < average_daily_demand * 0.90:

    st.info(
        "ℹ️ Demand appears to be declining. "
        "Avoid unnecessary inventory accumulation."
    )

else:

    st.success(
        "✅ Demand appears relatively stable. "
        "Maintain normal inventory levels."
    )

# ---------------------------------------------------------
# BUSINESS INSIGHTS
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title">💡 Business Insights</div>',
    unsafe_allow_html=True
)

insight_col1, insight_col2 = st.columns(2)

with insight_col1:

    st.markdown("""
    **Demand Planning**

    • Monitor recent demand trends  
    • Use forecasts for replenishment planning  
    • Identify demand spikes early
    """)

with insight_col2:

    st.markdown("""
    **Inventory Strategy**

    • Maintain appropriate safety stock  
    • Reduce overstock risk  
    • Align inventory with expected demand
    """)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()

st.caption(
    "FORESIGHT | Retail Demand Intelligence | "
    "Decision Support Dashboard"
)
