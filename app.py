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
# CURRENT STOCK INPUT
# ---------------------------------------------------------
st.markdown("### 📦 Current Inventory")

if "Product" in filtered_df.columns:

    stock_products = sorted(
        filtered_df["Product"].dropna().unique()
    )

    stock_data = []

    for product in stock_products:

        product_daily = (
            filtered_df[
                filtered_df["Product"] == product
            ]
            .groupby("Date")["Sales"]
            .sum()
            .sort_index()
        )

        if len(product_daily) > 0:

            product_forecast = product_daily.tail(
                min(14, len(product_daily))
            ).mean()

        else:
            product_forecast = 0

        current_stock = st.number_input(
            f"{product} - Current Stock",
            min_value=0,
            value=100,
            step=10,
            key=f"stock_{product}"
        )

        product_reorder_point = (
            product_forecast * lead_time_days
            + (
                product_daily.std()
                * np.sqrt(lead_time_days)
                * (service_buffer / 100)
                if len(product_daily) > 1
                else 0
            )
        )

        order_quantity = max(
            0,
            int(
                product_forecast * target_days
                - current_stock
            )
        )

        if current_stock <= product_reorder_point:
            status = "🔴 ORDER NOW"
        elif current_stock <= product_reorder_point * 1.25:
            status = "🟡 MONITOR"
        else:
            status = "🟢 STOCK OK"

        stock_data.append({
            "Product": product,
            "Current Stock": current_stock,
            "Daily Forecast": round(product_forecast),
            "Reorder Point": round(product_reorder_point),
            "Recommended Order": order_quantity,
            "Status": status
        })

    stock_df = pd.DataFrame(stock_data)

    st.dataframe(
        stock_df,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # ORDER ALERT
    # -----------------------------------------------------
    orders_required = stock_df[
        stock_df["Status"] == "🔴 ORDER NOW"
    ]

    if len(orders_required) > 0:

        st.error(
            f"🚨 {len(orders_required)} product(s) "
            "have reached their reorder point."
        )

        st.write(
            "Recommended products to reorder:"
        )

        st.dataframe(
            orders_required[
                [
                    "Product",
                    "Current Stock",
                    "Reorder Point",
                    "Recommended Order"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "✅ No product currently requires immediate reordering."
        )

else:

    st.info(
        "Product-level inventory alerts require a Product column."
    )
# ---------------------------------------------------------
# SMART INVENTORY INTELLIGENCE
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title">🚨 Smart Inventory Intelligence</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# INVENTORY PARAMETERS
# ---------------------------------------------------------
inventory_col1, inventory_col2 = st.columns(2)

with inventory_col1:
    lead_time_days = st.slider(
        "Supplier Lead Time (days)",
        min_value=1,
        max_value=30,
        value=7
    )

with inventory_col2:
    service_buffer = st.slider(
        "Safety Buffer (%)",
        min_value=5,
        max_value=50,
        value=25,
        step=5
    )

# ---------------------------------------------------------
# DEMAND STATISTICS
# ---------------------------------------------------------
forecast_daily = forecast_demand

# Demand variability
demand_std = daily_sales.std()

if pd.isna(demand_std):
    demand_std = 0

# ---------------------------------------------------------
# SAFETY STOCK
# ---------------------------------------------------------
# Safety stock increases when demand becomes more variable.
safety_stock = (
    demand_std *
    np.sqrt(lead_time_days) *
    (service_buffer / 100)
)

# ---------------------------------------------------------
# REORDER POINT
# ---------------------------------------------------------
reorder_point = (
    forecast_daily * lead_time_days
    + safety_stock
)

# ---------------------------------------------------------
# TARGET STOCK
# ---------------------------------------------------------
target_days = 14

target_inventory = (
    forecast_daily * target_days
    + safety_stock
)

# ---------------------------------------------------------
# EXPECTED 14-DAY DEMAND
# ---------------------------------------------------------
expected_demand = (
    forecast_daily * target_days
)

# ---------------------------------------------------------
# INVENTORY KPI CARDS
# ---------------------------------------------------------
icol1, icol2, icol3, icol4 = st.columns(4)

with icol1:
    st.metric(
        "Forecast / Day",
        f"{forecast_daily:,.0f}"
    )

with icol2:
    st.metric(
        "Safety Stock",
        f"{safety_stock:,.0f}"
    )

with icol3:
    st.metric(
        "Reorder Point",
        f"{reorder_point:,.0f}"
    )

with icol4:
    st.metric(
        "Target 14-Day Stock",
        f"{target_inventory:,.0f}"
    )

# ---------------------------------------------------------
# INVENTORY PLANNING TABLE
# ---------------------------------------------------------
st.markdown("### 📦 Inventory Planning")

inventory_plan = pd.DataFrame({
    "Metric": [
        "Expected 14-Day Demand",
        "Safety Stock",
        "Recommended Target Stock",
        "Reorder Point"
    ],
    "Units": [
        round(expected_demand),
        round(safety_stock),
        round(target_inventory),
        round(reorder_point)
    ]
})

st.dataframe(
    inventory_plan,
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------------
# INVENTORY STATUS
# ---------------------------------------------------------
st.markdown("### 🔎 Inventory Status")

if trend_percent > 10:

    st.warning(
        f"📈 Demand is increasing by approximately "
        f"{trend_percent:.1f}%. Increase replenishment "
        f"frequency and maintain additional safety stock."
    )

elif trend_percent < -10:

    st.info(
        f"📉 Demand is declining by approximately "
        f"{abs(trend_percent):.1f}%. Avoid aggressive "
        f"replenishment and monitor excess inventory."
    )

else:

    st.success(
        "✅ Demand is relatively stable. "
        "Maintain the recommended inventory target."
    )

# ---------------------------------------------------------
# REPLENISHMENT GUIDANCE
# ---------------------------------------------------------
st.markdown("### 🚚 Replenishment Guidance")

if forecast_daily > 0:

    st.write(
        f"Based on the current forecast, approximately "
        f"**{forecast_daily:,.0f} units/day** are expected."
    )

    st.write(
        f"With a supplier lead time of **{lead_time_days} days**, "
        f"the estimated demand during lead time is "
        f"**{forecast_daily * lead_time_days:,.0f} units**."
    )

    st.write(
        f"Recommended reorder protection is approximately "
        f"**{safety_stock:,.0f} safety-stock units**."
    )

# ---------------------------------------------------------
# INVENTORY FORMULA SUMMARY
# ---------------------------------------------------------
with st.expander("ℹ️ How the inventory recommendation works"):

    st.markdown("""
    **Safety Stock**

    Safety stock increases when demand becomes more variable.

    **Reorder Point**

    Reorder Point = Lead-Time Demand + Safety Stock

    **Target Stock**

    Target Stock = Expected 14-Day Demand + Safety Stock

    These recommendations are decision-support estimates and
    should be adjusted using actual supplier lead times,
    current inventory, and business constraints.
    """)
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
