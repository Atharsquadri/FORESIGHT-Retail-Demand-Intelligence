import streamlit as st
import pandas as pd
import numpy as np

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="FORESIGHT | Retail Demand Intelligence",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# CONFIGURATION
# =========================================================
LEAD_TIME_DAYS = 7
SAFETY_BUFFER = 0.25
TARGET_STOCK_DAYS = 14

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.hero {
    padding: 1rem 0 0.5rem 0;
}

.hero h1 {
    font-size: 44px;
    font-weight: 800;
    margin-bottom: 0;
}

.hero p {
    font-size: 18px;
    margin-top: 5px;
    color: #777;
}

.section-title {
    font-size: 25px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 12px;
}

.small-note {
    color: #777;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="hero">
    <h1>FORESIGHT</h1>
    <p>Retail Demand Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("⚙️ Control Center")

st.sidebar.subheader("📁 Data Source")

uploaded_file = st.sidebar.file_uploader(
    "Upload Sales CSV",
    type=["csv"]
)

# =========================================================
# DEMO DATA GENERATOR
# =========================================================
def create_demo_data():

    np.random.seed(42)

    dates = pd.date_range(
        end=pd.Timestamp.today().normalize(),
        periods=180
    )

    products = [
        "Product A",
        "Product B",
        "Product C",
        "Product D",
        "Product E"
    ]

    base_demand = {
        "Product A": 180,
        "Product B": 140,
        "Product C": 220,
        "Product D": 100,
        "Product E": 160
    }

    prices = {
        "Product A": 499,
        "Product B": 699,
        "Product C": 899,
        "Product D": 399,
        "Product E": 599
    }

    data = []

    for date in dates:

        for product in products:

            base = base_demand[product]

            # Weekend effect
            if date.weekday() >= 5:
                base *= 1.10

            demand = max(
                0,
                int(
                    base +
                    np.random.normal(0, 25)
                )
            )

            price = prices[product]

            data.append({
                "Date": date,
                "Product": product,
                "Sales": demand,
                "Price": price
            })

    return pd.DataFrame(data)


# =========================================================
# LOAD DATA
# =========================================================
if uploaded_file is not None:

    try:

        df = pd.read_csv(uploaded_file)

        st.sidebar.success(
            "✅ CSV loaded successfully"
        )

    except Exception:

        st.error(
            "❌ Unable to read the CSV file."
        )

        st.stop()

else:

    df = create_demo_data()

    st.sidebar.info(
        "Demo retail data is being used."
    )


# =========================================================
# DATA VALIDATION
# =========================================================
required_columns = [
    "Date",
    "Sales"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        "Missing required column(s): "
        + ", ".join(missing_columns)
    )

    st.info(
        "Your CSV should contain at least "
        "'Date' and 'Sales'."
    )

    st.stop()


# =========================================================
# DATA CLEANING
# =========================================================
df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

df["Sales"] = pd.to_numeric(
    df["Sales"],
    errors="coerce"
)

df = df.dropna(
    subset=["Date", "Sales"]
).copy()

if df.empty:

    st.error(
        "No valid data found."
    )

    st.stop()


# =========================================================
# OPTIONAL PRICE / REVENUE
# =========================================================
if "Price" in df.columns:

    df["Price"] = pd.to_numeric(
        df["Price"],
        errors="coerce"
    )

    df["Revenue"] = (
        df["Sales"] *
        df["Price"].fillna(0)
    )

else:

    df["Revenue"] = 0


# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.subheader("🔎 Filters")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if (
    isinstance(date_range, tuple)
    and len(date_range) == 2
):

    start_date, end_date = date_range

    filtered_df = df[
        (df["Date"].dt.date >= start_date)
        &
        (df["Date"].dt.date <= end_date)
    ].copy()

else:

    filtered_df = df.copy()


# =========================================================
# PRODUCT FILTER
# =========================================================
if "Product" in filtered_df.columns:

    product_options = sorted(
        filtered_df["Product"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_products = st.sidebar.multiselect(
        "Products",
        product_options,
        default=product_options
    )

    if selected_products:

        filtered_df = filtered_df[
            filtered_df["Product"]
            .astype(str)
            .isin(selected_products)
        ]


# =========================================================
# EMPTY FILTER CHECK
# =========================================================
if filtered_df.empty:

    st.warning(
        "⚠️ No data available for the selected filters."
    )

    st.stop()


# =========================================================
# DAILY DEMAND
# =========================================================
daily_sales = (
    filtered_df
    .groupby("Date")["Sales"]
    .sum()
    .sort_index()
)

average_daily_demand = daily_sales.mean()

peak_demand = daily_sales.max()

total_sales = filtered_df["Sales"].sum()

total_revenue = filtered_df["Revenue"].sum()


# =========================================================
# FORECAST
# =========================================================
forecast_window = min(
    14,
    len(daily_sales)
)

if forecast_window > 0:

    forecast_demand = (
        daily_sales
        .tail(forecast_window)
        .mean()
    )

else:

    forecast_demand = 0


# =========================================================
# EXECUTIVE OVERVIEW
# =========================================================
st.markdown(
    '<div class="section-title">'
    '📊 Executive Overview'
    '</div>',
    unsafe_allow_html=True
)

k1, k2, k3, k4, k5 = st.columns(5)

with k1:

    st.metric(
        "Total Units Sold",
        f"{total_sales:,.0f}"
    )

with k2:

    st.metric(
        "Average Daily Demand",
        f"{average_daily_demand:,.0f}"
    )

with k3:

    st.metric(
        "Peak Daily Demand",
        f"{peak_demand:,.0f}"
    )

with k4:

    st.metric(
        "14-Day Forecast",
        f"{forecast_demand:,.0f}"
    )

with k5:

    if total_revenue > 0:

        st.metric(
            "Revenue",
            f"₹{total_revenue:,.0f}"
        )

    else:

        st.metric(
            "Products",
            f"{filtered_df['Product'].nunique() if 'Product' in filtered_df.columns else 0}"
        )


# =========================================================
# DEMAND TREND
# =========================================================
st.markdown(
    '<div class="section-title">'
    '📈 Demand Trend'
    '</div>',
    unsafe_allow_html=True
)

trend_df = daily_sales.rename(
    "Demand"
)

st.line_chart(
    trend_df,
    height=350
)


# =========================================================
# FORECAST SECTION
# =========================================================
st.markdown(
    '<div class="section-title">'
    '🤖 Demand Forecast'
    '</div>',
    unsafe_allow_html=True
)

forecast_days = st.select_slider(
    "Forecast Horizon",
    options=[7, 14, 21, 30],
    value=14
)

if len(daily_sales) >= 7:

    moving_average = (
        daily_sales
        .tail(
            min(
                14,
                len(daily_sales)
            )
        )
        .mean()
    )

    forecast_dates = pd.date_range(
        start=(
            daily_sales.index.max()
            + pd.Timedelta(days=1)
        ),
        periods=forecast_days
    )

    forecast_df = pd.DataFrame(
        {
            "Forecast": [
                moving_average
                for _ in forecast_dates
            ]
        },
        index=forecast_dates
    )

    st.line_chart(
        forecast_df,
        height=300
    )

    st.info(
        f"Forecast uses a {min(14, len(daily_sales))}-day "
        "moving average of observed demand."
    )


# =========================================================
# PRODUCT PERFORMANCE
# =========================================================
if "Product" in filtered_df.columns:

    st.markdown(
        '<div class="section-title">'
        '🏆 Product Performance'
        '</div>',
        unsafe_allow_html=True
    )

    product_sales = (
        filtered_df
        .groupby("Product")["Sales"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    st.bar_chart(
        product_sales,
        height=350
    )

    performance = (
        product_sales
        .reset_index()
    )

    performance.columns = [
        "Product",
        "Units Sold"
    ]

    total_product_sales = (
        performance["Units Sold"].sum()
    )

    if total_product_sales > 0:

        performance["Share of Sales (%)"] = (
            performance["Units Sold"]
            /
            total_product_sales
            * 100
        ).round(1)

    else:

        performance["Share of Sales (%)"] = 0

    st.dataframe(
        performance,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# INVENTORY INTELLIGENCE
# =========================================================
st.markdown(
    '<div class="section-title">'
    '🚨 Inventory Intelligence'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    f"Lead Time: {LEAD_TIME_DAYS} days | "
    f"Safety Buffer: {SAFETY_BUFFER:.0%} | "
    f"Target Stock: {TARGET_STOCK_DAYS} days"
)


# =========================================================
# INVENTORY CALCULATION
# =========================================================
if "Product" in filtered_df.columns:

    stock_products = sorted(
        filtered_df["Product"]
        .dropna()
        .astype(str)
        .unique()
    )

    stock_data = []

    for product in stock_products:

        product_df = filtered_df[
            filtered_df["Product"].astype(str)
            == product
        ]

        product_daily = (
            product_df
            .groupby("Date")["Sales"]
            .sum()
            .sort_index()
        )

        if len(product_daily) > 0:

            product_forecast = (
                product_daily
                .tail(
                    min(
                        14,
                        len(product_daily)
                    )
                )
                .mean()
            )

        else:

            product_forecast = 0


        # ---------------------------------------------
        # Current Stock
        # ---------------------------------------------
        current_stock = st.number_input(
            f"📦 {product} — Current Stock",
            min_value=0,
            value=100,
            step=10,
            key=f"inventory_{product}"
        )


        # ---------------------------------------------
        # Demand Variability
        # ---------------------------------------------
        if len(product_daily) > 1:

            demand_std = (
                product_daily.std()
            )

        else:

            demand_std = 0


        # ---------------------------------------------
        # Safety Stock
        # ---------------------------------------------
        safety_stock = (
            demand_std
            *
            np.sqrt(LEAD_TIME_DAYS)
            *
            SAFETY_BUFFER
        )


        # ---------------------------------------------
        # Reorder Point
        # ---------------------------------------------
        reorder_point = (
            product_forecast
            *
            LEAD_TIME_DAYS
            +
            safety_stock
        )


        # ---------------------------------------------
        # Target Inventory
        # ---------------------------------------------
        target_inventory = (
            product_forecast
            *
            TARGET_STOCK_DAYS
            +
            safety_stock
        )


        # ---------------------------------------------
        # Recommended Order
        # ---------------------------------------------
        recommended_order = max(
            0,
            int(
                np.ceil(
                    target_inventory
                    -
                    current_stock
                )
            )
        )


        # ---------------------------------------------
        # Days of Cover
        # ---------------------------------------------
        if product_forecast > 0:

            days_of_cover = (
                current_stock
                /
                product_forecast
            )

        else:

            days_of_cover = 999


        # ---------------------------------------------
        # Status
        # ---------------------------------------------
        if current_stock <= reorder_point:

            status = "🔴 ORDER NOW"

        elif current_stock <= reorder_point * 1.25:

            status = "🟡 MONITOR"

        else:

            status = "🟢 STOCK OK"


        stock_data.append(
            {
                "Product": product,
                "Current Stock": int(
                    current_stock
                ),
                "Daily Forecast": round(
                    product_forecast
                ),
                "Reorder Point": round(
                    reorder_point
                ),
                "Safety Stock": round(
                    safety_stock
                ),
                "Days of Cover": round(
                    days_of_cover,
                    1
                ),
                "Recommended Order": (
                    recommended_order
                ),
                "Status": status
            }
        )


    stock_df = pd.DataFrame(
        stock_data
    )


    # =====================================================
    # INVENTORY TABLE
    # =====================================================
    st.markdown(
        "### 📦 Current Inventory Status"
    )

    st.dataframe(
        stock_df,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # INVENTORY KPIs
    # =====================================================
    total_current_stock = (
        stock_df["Current Stock"].sum()
    )

    total_safety_stock = (
        stock_df["Safety Stock"].sum()
    )

    total_order_quantity = (
        stock_df["Recommended Order"].sum()
    )

    order_now_count = (
        stock_df["Status"]
        .eq("🔴 ORDER NOW")
        .sum()
    )

    monitor_count = (
        stock_df["Status"]
        .eq("🟡 MONITOR")
        .sum()
    )

    stock_ok_count = (
        stock_df["Status"]
        .eq("🟢 STOCK OK")
        .sum()
    )


    st.markdown(
        "### 📊 Inventory Summary"
    )

    i1, i2, i3, i4 = st.columns(4)

    with i1:

        st.metric(
            "Current Stock",
            f"{total_current_stock:,.0f}"
        )

    with i2:

        st.metric(
            "Safety Stock",
            f"{total_safety_stock:,.0f}"
        )

    with i3:

        st.metric(
            "Recommended Order",
            f"{total_order_quantity:,.0f}"
        )

    with i4:

        st.metric(
            "Order Now",
            f"{order_now_count}"
        )


    # =====================================================
    # ALERTS
    # =====================================================
    orders_required = stock_df[
        stock_df["Status"]
        == "🔴 ORDER NOW"
    ]

    monitor_products = stock_df[
        stock_df["Status"]
        == "🟡 MONITOR"
    ]


    if len(orders_required) > 0:

        st.error(
            f"🚨 {len(orders_required)} product(s) "
            "require immediate reordering."
        )

        st.dataframe(
            orders_required[
                [
                    "Product",
                    "Current Stock",
                    "Daily Forecast",
                    "Reorder Point",
                    "Days of Cover",
                    "Recommended Order"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "✅ No product currently requires "
            "immediate reordering."
        )


    if len(monitor_products) > 0:

        st.warning(
            f"🟡 {len(monitor_products)} product(s) "
            "should be monitored."
        )


    # =====================================================
    # DOWNLOAD INVENTORY REPORT
    # =====================================================
    st.markdown(
        "### 📥 Inventory Report"
    )

    csv_data = stock_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Inventory Recommendations",
        data=csv_data,
        file_name="foresight_inventory_report.csv",
        mime="text/csv"
    )


# =========================================================
# BUSINESS INSIGHTS
# =========================================================
st.markdown(
    '<div class="section-title">'
    '💡 Business Insights'
    '</div>',
    unsafe_allow_html=True
)

insight1, insight2, insight3 = st.columns(3)


with insight1:

    st.markdown("### 📈 Demand Planning")

    if forecast_demand > average_daily_demand * 1.10:

        st.warning(
            "Demand is trending upward. "
            "Prepare additional inventory."
        )

    elif forecast_demand < average_daily_demand * 0.90:

        st.info(
            "Demand is trending downward. "
            "Avoid unnecessary stock accumulation."
        )

    else:

        st.success(
            "Demand is relatively stable."
        )


with insight2:

    st.markdown("### 🏆 Best Product")

    if "Product" in filtered_df.columns:

        best_product = (
            filtered_df
            .groupby("Product")["Sales"]
            .sum()
            .idxmax()
        )

        best_product_sales = (
            filtered_df
            .groupby("Product")["Sales"]
            .sum()
            .max()
        )

        st.success(
            f"{best_product} is the top-selling "
            f"product with {best_product_sales:,.0f} "
            "units sold."
        )

    else:

        st.info(
            "Product information is unavailable."
        )


with insight3:

    st.markdown("### 🎯 Inventory Action")

    if "Product" in filtered_df.columns:

        if order_now_count > 0:

            st.error(
                f"{order_now_count} product(s) "
                "need immediate attention."
            )

        elif monitor_count > 0:

            st.warning(
                f"{monitor_count} product(s) "
                "need monitoring."
            )

        else:

            st.success(
                "Inventory levels look healthy."
            )


# =========================================================
# DATA PREVIEW
# =========================================================
with st.expander("🔍 View Raw Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# DEMO CSV TEMPLATE
# =========================================================
with st.expander("📄 CSV Format"):

    st.write(
        "For your own data, the recommended columns are:"
    )

    template = pd.DataFrame(
        {
            "Date": [
                "2026-01-01",
                "2026-01-02"
            ],
            "Product": [
                "Product A",
                "Product A"
            ],
            "Sales": [
                180,
                195
            ],
            "Price": [
                499,
                499
            ]
        }
    )

    st.dataframe(
        template,
        use_container_width=True,
        hide_index=True
    )

    template_csv = template.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download CSV Template",
        template_csv,
        "foresight_sales_template.csv",
        "text/csv"
    )


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    "FORESIGHT | Retail Demand Intelligence | "
    "Decision Support Dashboard"
)
