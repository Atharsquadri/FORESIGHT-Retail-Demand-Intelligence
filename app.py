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
# PROFESSIONAL DEMAND FORECAST
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

    # ---------------------------------------------
    # RECENT DEMAND
    # ---------------------------------------------
    recent_window = min(14, len(daily_sales))
    previous_window = min(14, max(0, len(daily_sales) - recent_window))

    recent_demand = daily_sales.tail(recent_window).mean()

    if previous_window > 0:
        previous_demand = (
            daily_sales.iloc[-(recent_window + previous_window):-recent_window]
            .mean()
        )
    else:
        previous_demand = recent_demand

    # ---------------------------------------------
    # DEMAND TREND
    # ---------------------------------------------
    if previous_demand != 0:
        trend_percent = (
            (recent_demand - previous_demand)
            / previous_demand
        ) * 100
    else:
        trend_percent = 0

    # Limit extreme trend impact
    trend_percent = max(-20, min(trend_percent, 20))

    # ---------------------------------------------
    # TREND-ADJUSTED FORECAST
    # ---------------------------------------------
    trend_factor = 1 + (trend_percent / 100)

    forecast_values = []

    for day in range(1, forecast_days + 1):

        # Gradually apply trend instead of jumping immediately
        progress = day / forecast_days

        forecast_value = (
            recent_demand *
            (1 + ((trend_factor - 1) * progress))
        )

        # Keep forecast within reasonable historical range
        historical_min = daily_sales.min()
        historical_max = daily_sales.max()

        forecast_value = max(
            historical_min,
            min(forecast_value, historical_max)
        )

        forecast_values.append(forecast_value)

    # ---------------------------------------------
    # FUTURE DATES
    # ---------------------------------------------
    forecast_dates = pd.date_range(
        start=daily_sales.index.max() + pd.Timedelta(days=1),
        periods=forecast_days
    )

    forecast_df = pd.DataFrame({
        "Forecast": forecast_values
    }, index=forecast_dates)

    # ---------------------------------------------
    # FORECAST CHART
    # ---------------------------------------------
    st.line_chart(
        forecast_df,
        height=300
    )

    # ---------------------------------------------
    # FORECAST SUMMARY
    # ---------------------------------------------
    forecast_average = forecast_df["Forecast"].mean()
    forecast_peak = forecast_df["Forecast"].max()

    fcol1, fcol2, fcol3 = st.columns(3)

    with fcol1:
        st.metric(
            "Forecast / Day",
            f"{forecast_average:,.0f}"
        )

    with fcol2:
        st.metric(
            "Forecast Peak",
            f"{forecast_peak:,.0f}"
        )

    with fcol3:
        st.metric(
            "Demand Trend",
            f"{trend_percent:+.1f}%"
        )

    # ---------------------------------------------
    # FORECAST TABLE
    # ---------------------------------------------
    st.markdown("### 📅 Forecast Details")

    forecast_table = forecast_df.reset_index()

    forecast_table.columns = [
        "Date",
        "Forecast Demand"
    ]

    forecast_table["Date"] = (
        forecast_table["Date"]
        .dt.strftime("%d %b %Y")
    )

    forecast_table["Forecast Demand"] = (
        forecast_table["Forecast Demand"]
        .round(0)
        .astype(int)
    )

    st.dataframe(
        forecast_table,
        use_container_width=True,
        hide_index=True
    )

    # ---------------------------------------------
    # FORECAST INTERPRETATION
    # ---------------------------------------------
    if trend_percent > 5:

        st.warning(
            f"📈 Demand is trending upward by approximately "
            f"{trend_percent:.1f}%. Consider increasing "
            f"replenishment before the forecast period."
        )

    elif trend_percent < -5:

        st.info(
            f"📉 Demand is trending downward by approximately "
            f"{abs(trend_percent):.1f}%. Consider controlling "
            f"new inventory commitments."
        )

    else:

        st.success(
            "➡️ Demand is relatively stable. "
            "Maintain normal replenishment levels."
        )

else:

    st.warning(
        "Not enough historical data for forecasting. "
        "At least 7 days of sales data are required."
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
