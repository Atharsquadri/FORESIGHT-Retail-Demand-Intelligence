import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="FORESIGHT | Retail Demand Intelligence",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# CONSTANTS
# =========================================================
LEAD_TIME_DAYS = 7
SAFETY_BUFFER = 0.25
TARGET_STOCK_DAYS = 14

# =========================================================
# STYLE
# =========================================================
st.markdown(
    """
    <style>
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
        color: #777;
    }

    .section-title {
        font-size: 25px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HEADER
# =========================================================
st.markdown(
    """
    <div class="hero">
        <h1>FORESIGHT</h1>
        <p>Retail Demand Intelligence Platform</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("⚙️ Control Center")

uploaded_file = st.sidebar.file_uploader(
    "📁 Upload Sales CSV",
    type=["csv"]
)

# =========================================================
# DEMO DATA
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

    base = {
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

    inventory = {
        "Product A": 100,
        "Product B": 150,
        "Product C": 120,
        "Product D": 200,
        "Product E": 180
    }

    data = []

    for date in dates:

        for product in products:

            demand = base[product]

            if date.weekday() >= 5:
                demand *= 1.10

            demand += np.random.normal(0, 25)

            demand = max(0, int(demand))

            data.append(
                {
                    "Date": date,
                    "Product": product,
                    "Sales": demand,
                    "Price": prices[product],
                    "Inventory": inventory[product]
                }
            )

    return pd.DataFrame(data)


# =========================================================
# LOAD DATA
# =========================================================
if uploaded_file is not None:

    try:

        df = pd.read_csv(uploaded_file)

        st.sidebar.success("✅ CSV loaded successfully")

    except Exception as e:

        st.error(f"Unable to read CSV: {e}")
        st.stop()

else:

    df = create_demo_data()

    st.sidebar.info("Demo data active")


# =========================================================
# VALIDATION
# =========================================================
required = [
    "Date",
    "Sales"
]

missing = [
    column
    for column in required
    if column not in df.columns
]

if missing:

    st.error(
        "Missing required column(s): "
        + ", ".join(missing)
    )

    st.info(
        "Required format: Date, Sales. "
        "Recommended: Product, Price, Inventory."
    )

    st.stop()


# =========================================================
# CLEAN DATA
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


# =========================================================
# PRODUCT COLUMN
# =========================================================
if "Product" not in df.columns:

    df["Product"] = "All Products"


# =========================================================
# PRICE / REVENUE
# =========================================================
if "Price" in df.columns:

    df["Price"] = pd.to_numeric(
        df["Price"],
        errors="coerce"
    ).fillna(0)

    df["Revenue"] = (
        df["Sales"] *
        df["Price"]
    )

else:

    df["Revenue"] = 0


# =========================================================
# INVENTORY CLEANING
# =========================================================
if "Inventory" in df.columns:

    df["Inventory"] = pd.to_numeric(
        df["Inventory"],
        errors="coerce"
    ).fillna(0)


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
products = sorted(
    filtered_df["Product"]
    .dropna()
    .astype(str)
    .unique()
)

selected_products = st.sidebar.multiselect(
    "Products",
    products,
    default=products
)

if selected_products:

    filtered_df = filtered_df[
        filtered_df["Product"]
        .astype(str)
        .isin(selected_products)
    ].copy()


# =========================================================
# EMPTY CHECK
# =========================================================
if filtered_df.empty:

    st.warning(
        "No data available for selected filters."
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

total_sales = daily_sales.sum()

average_daily = (
    daily_sales.mean()
    if len(daily_sales) > 0
    else 0
)

peak_daily = (
    daily_sales.max()
    if len(daily_sales) > 0
    else 0
)


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
        "Total Units",
        f"{total_sales:,.0f}"
    )

with k2:

    st.metric(
        "Avg Daily Demand",
        f"{average_daily:,.0f}"
    )

with k3:

    st.metric(
        "Peak Demand",
        f"{peak_daily:,.0f}"
    )

with k4:

    revenue = filtered_df["Revenue"].sum()

    if revenue > 0:

        st.metric(
            "Revenue",
            f"₹{revenue:,.0f}"
        )

    else:

        st.metric(
            "Products",
            str(
                filtered_df["Product"].nunique()
            )
        )

with k5:

    recent_forecast = (
        daily_sales.tail(
            min(14, len(daily_sales))
        ).mean()
        if len(daily_sales) > 0
        else 0
    )

    st.metric(
        "Current Forecast",
        f"{recent_forecast:,.0f}"
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

st.line_chart(
    daily_sales.rename("Demand"),
    height=350
)


# =========================================================
# AI DEMAND FORECAST
# =========================================================
st.markdown(
    '<div class="section-title">'
    '🤖 AI Demand Forecast'
    '</div>',
    unsafe_allow_html=True
)

forecast_days = st.select_slider(
    "Forecast Horizon",
    options=[7, 14, 21, 30],
    value=14
)


if len(daily_sales) >= 14:

    recent_data = daily_sales.tail(14)

    previous_data = daily_sales.iloc[-28:-14]

    recent_avg = recent_data.mean()

    previous_avg = (
        previous_data.mean()
        if len(previous_data) > 0
        else recent_avg
    )

    # -----------------------------------------------------
    # TREND
    # -----------------------------------------------------
    if previous_avg != 0:

        trend_pct = (
            (recent_avg - previous_avg)
            / previous_avg
        ) * 100

    else:

        trend_pct = 0

    trend_pct = max(
        -20,
        min(trend_pct, 20)
    )

    # -----------------------------------------------------
    # VOLATILITY
    # -----------------------------------------------------
    volatility = recent_data.std()

    if pd.isna(volatility):

        volatility = 0

    # -----------------------------------------------------
    # FORECAST
    # -----------------------------------------------------
    forecast_values = []

    for day in range(
        1,
        forecast_days + 1
    ):

        progress = day / forecast_days

        trend_factor = (
            1
            + (trend_pct / 100)
            * progress
        )

        value = (
            recent_avg
            * trend_factor
        )

        forecast_values.append(
            max(0, value)
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
            "Forecast": forecast_values
        },
        index=forecast_dates
    )

    # -----------------------------------------------------
    # FORECAST CHART
    # -----------------------------------------------------
    chart_data = pd.concat(
        [
            daily_sales.tail(30).rename(
                "Historical"
            ),
            forecast_df["Forecast"]
        ],
        axis=1
    )

    st.line_chart(
        chart_data,
        height=350
    )

    # -----------------------------------------------------
    # FORECAST KPIs
    # -----------------------------------------------------
    f1, f2, f3, f4 = st.columns(4)

    forecast_avg = (
        forecast_df["Forecast"].mean()
    )

    forecast_total = (
        forecast_df["Forecast"].sum()
    )

    confidence_margin = (
        volatility * 1.28
    )

    lower_forecast = max(
        0,
        forecast_avg - confidence_margin
    )

    upper_forecast = (
        forecast_avg
        + confidence_margin
    )

    with f1:

        st.metric(
            "Forecast / Day",
            f"{forecast_avg:,.0f}"
        )

    with f2:

        st.metric(
            f"{forecast_days}-Day Demand",
            f"{forecast_total:,.0f}"
        )

    with f3:

        st.metric(
            "Trend",
            f"{trend_pct:+.1f}%"
        )

    with f4:

        st.metric(
            "Forecast Range",
            f"{lower_forecast:,.0f}"
            f" – "
            f"{upper_forecast:,.0f}"
        )

    # -----------------------------------------------------
    # INTERPRETATION
    # -----------------------------------------------------
    if trend_pct > 5:

        st.warning(
            f"📈 Demand is increasing "
            f"({trend_pct:+.1f}%). "
            "Prepare additional inventory."
        )

    elif trend_pct < -5:

        st.info(
            f"📉 Demand is declining "
            f"({trend_pct:+.1f}%). "
            "Control replenishment."
        )

    else:

        st.success(
            "➡️ Demand is relatively stable."
        )

else:

    st.warning(
        "At least 14 days of data are recommended "
        "for forecasting."
    )


# =========================================================
# PRODUCT ANALYTICS
# =========================================================
st.markdown(
    '<div class="section-title">'
    '🏆 Product Analytics'
    '</div>',
    unsafe_allow_html=True
)

product_summary = (
    filtered_df
    .groupby("Product")
    .agg(
        Units_Sold=("Sales", "sum"),
        Revenue=("Revenue", "sum")
    )
    .sort_values(
        "Units_Sold",
        ascending=False
    )
)

st.bar_chart(
    product_summary["Units_Sold"],
    height=350
)

product_table = (
    product_summary
    .reset_index()
)

product_table.columns = [
    "Product",
    "Units Sold",
    "Revenue"
]

total_units = (
    product_table["Units Sold"].sum()
)

if total_units > 0:

    product_table[
        "Sales Share (%)"
    ] = (
        product_table["Units Sold"]
        / total_units
        * 100
    ).round(1)

st.dataframe(
    product_table,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# SMART INVENTORY
# =========================================================
st.markdown(
    '<div class="section-title">'
    '🚨 Smart Inventory Intelligence'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    f"Supplier Lead Time: "
    f"{LEAD_TIME_DAYS} days | "
    f"Safety Buffer: "
    f"{SAFETY_BUFFER:.0%} | "
    f"Target Coverage: "
    f"{TARGET_STOCK_DAYS} days"
)


inventory_data = []

inventory_products = sorted(
    filtered_df["Product"]
    .dropna()
    .astype(str)
    .unique()
)


for product in inventory_products:

    product_data = filtered_df[
        filtered_df["Product"]
        .astype(str)
        == product
    ].copy()

    product_daily = (
        product_data
        .groupby("Date")["Sales"]
        .sum()
        .sort_index()
    )

    # -----------------------------------------------------
    # PRODUCT FORECAST
    # -----------------------------------------------------
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


    # -----------------------------------------------------
    # CURRENT STOCK
    # -----------------------------------------------------
    if "Inventory" in filtered_df.columns:

        inventory_values = (
            product_data["Inventory"]
            .dropna()
        )

        if len(inventory_values) > 0:

            current_stock = int(
                inventory_values.iloc[-1]
            )

        else:

            current_stock = st.number_input(
                f"📦 {product} — Current Stock",
                min_value=0,
                value=100,
                step=10,
                key=f"stock_{product}"
            )

    else:

        current_stock = st.number_input(
            f"📦 {product} — Current Stock",
            min_value=0,
            value=100,
            step=10,
            key=f"stock_{product}"
        )


    # -----------------------------------------------------
    # DEMAND VARIABILITY
    # -----------------------------------------------------
    if len(product_daily) > 1:

        demand_std = product_daily.std()

    else:

        demand_std = 0


    if pd.isna(demand_std):

        demand_std = 0


    # -----------------------------------------------------
    # SAFETY STOCK
    # -----------------------------------------------------
    safety_stock = (
        demand_std
        * np.sqrt(LEAD_TIME_DAYS)
        * SAFETY_BUFFER
    )


    # -----------------------------------------------------
    # REORDER POINT
    # -----------------------------------------------------
    reorder_point = (
        product_forecast
        * LEAD_TIME_DAYS
        + safety_stock
    )


    # -----------------------------------------------------
    # TARGET INVENTORY
    # -----------------------------------------------------
    target_inventory = (
        product_forecast
        * TARGET_STOCK_DAYS
        + safety_stock
    )


    # -----------------------------------------------------
    # RECOMMENDED ORDER
    # -----------------------------------------------------
    recommended_order = max(
        0,
        int(
            np.ceil(
                target_inventory
                - current_stock
            )
        )
    )


    # -----------------------------------------------------
    # DAYS OF COVER
    # -----------------------------------------------------
    if product_forecast > 0:

        days_cover = (
            current_stock
            / product_forecast
        )

    else:

        days_cover = 999


    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------
    if current_stock <= reorder_point:

        status = "🔴 ORDER NOW"

    elif current_stock <= reorder_point * 1.25:

        status = "🟡 MONITOR"

    else:

        status = "🟢 STOCK OK"


    inventory_data.append(
        {
            "Product": product,
            "Current Stock": int(
                current_stock
            ),
            "Daily Forecast": round(
                product_forecast
            ),
            "Safety Stock": round(
                safety_stock
            ),
            "Reorder Point": round(
                reorder_point
            ),
            "Days of Cover": round(
                days_cover,
                1
            ),
            "Recommended Order": (
                recommended_order
            ),
            "Status": status
        }
    )


# =========================================================
# INVENTORY DATAFRAME
# =========================================================
inventory_df = pd.DataFrame(
    inventory_data
)


st.markdown(
    "### 📦 Inventory Status"
)

st.dataframe(
    inventory_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# INVENTORY KPIs
# =========================================================
current_total = (
    inventory_df["Current Stock"].sum()
)

safety_total = (
    inventory_df["Safety Stock"].sum()
)

order_total = (
    inventory_df["Recommended Order"].sum()
)

order_now = (
    inventory_df["Status"]
    .eq("🔴 ORDER NOW")
    .sum()
)

monitor = (
    inventory_df["Status"]
    .eq("🟡 MONITOR")
    .sum()
)

ok = (
    inventory_df["Status"]
    .eq("🟢 STOCK OK")
    .sum()
)


i1, i2, i3, i4 = st.columns(4)

with i1:

    st.metric(
        "Current Stock",
        f"{current_total:,.0f}"
    )

with i2:

    st.metric(
        "Safety Stock",
        f"{safety_total:,.0f}"
    )

with i3:

    st.metric(
        "Recommended Order",
        f"{order_total:,.0f}"
    )

with i4:

    st.metric(
        "Order Now",
        str(order_now)
    )


# =========================================================
# ORDER ALERT
# =========================================================
if order_now > 0:

    st.error(
        f"🚨 {order_now} product(s) "
        "require immediate reordering."
    )

    urgent = inventory_df[
        inventory_df["Status"]
        == "🔴 ORDER NOW"
    ]

    st.dataframe(
        urgent[
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


if monitor > 0:

    st.warning(
        f"🟡 {monitor} product(s) "
        "should be monitored."
    )


# =========================================================
# INVENTORY CSV DOWNLOAD
# =========================================================
inventory_csv = (
    inventory_df
    .to_csv(index=False)
    .encode("utf-8")
)

st.download_button(
    "⬇️ Download Inventory CSV",
    inventory_csv,
    "foresight_inventory_report.csv",
    "text/csv"
)


# =========================================================
# EXCEL REPORT
# =========================================================
def create_excel_report():

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        product_table.to_excel(
            writer,
            sheet_name="Product Analytics",
            index=False
        )

        inventory_df.to_excel(
            writer,
            sheet_name="Inventory",
            index=False
        )

        filtered_df.to_excel(
            writer,
            sheet_name="Sales Data",
            index=False
        )

        if "forecast_df" in globals():

            forecast_export = (
                forecast_df
                .reset_index()
            )

            forecast_export.columns = [
                "Date",
                "Forecast"
            ]

            forecast_export.to_excel(
                writer,
                sheet_name="Forecast",
                index=False
            )

    output.seek(0)

    return output


excel_file = create_excel_report()

st.download_button(
    "📥 Download Complete Excel Report",
    excel_file,
    "foresight_complete_report.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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

b1, b2, b3 = st.columns(3)


# ---------------------------------------------------------
# DEMAND INSIGHT
# ---------------------------------------------------------
with b1:

    st.markdown("### 📈 Demand")

    if len(daily_sales) >= 28:

        recent_avg = (
            daily_sales
            .tail(14)
            .mean()
        )

        old_avg = (
            daily_sales
            .iloc[-28:-14]
            .mean()
        )

        if old_avg != 0:

            change = (
                (recent_avg - old_avg)
                / old_avg
                * 100
            )

        else:

            change = 0

        if change > 5:

            st.warning(
                f"Demand rising by "
                f"{change:.1f}%."
            )

        elif change < -5:

            st.info(
                f"Demand falling by "
                f"{abs(change):.1f}%."
            )

        else:

            st.success(
                "Demand is stable."
            )

    else:

        st.info(
            "More historical data needed."
        )


# ---------------------------------------------------------
# BEST SELLER
# ---------------------------------------------------------
with b2:

    st.markdown("### 🏆 Best Seller")

    best_product = (
        filtered_df
        .groupby("Product")["Sales"]
        .sum()
        .idxmax()
    )

    best_sales = (
        filtered_df
        .groupby("Product")["Sales"]
        .sum()
        .max()
    )

    st.success(
        f"{best_product}: "
        f"{best_sales:,.0f} units"
    )


# ---------------------------------------------------------
# INVENTORY ACTION
# ---------------------------------------------------------
with b3:

    st.markdown("### 🎯 Inventory Action")

    if order_now > 0:

        st.error(
            f"{order_now} product(s) "
            "need ordering."
        )

    elif monitor > 0:

        st.warning(
            f"{monitor} product(s) "
            "need monitoring."
        )

    else:

        st.success(
            "Inventory looks healthy."
        )


# =========================================================
# RAW DATA
# =========================================================
with st.expander("🔍 View Raw Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# CSV FORMAT
# =========================================================
with st.expander("📄 Recommended CSV Format"):

    st.write(
        "Recommended CSV columns:"
    )

    st.code(
        "Date,Product,Sales,Price,Inventory\n"
        "2026-01-01,Product A,180,499,500\n"
        "2026-01-02,Product A,195,499,480"
    )

    st.caption(
        "Date and Sales are required. "
        "Product, Price and Inventory are recommended."
    )


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    "FORESIGHT | Retail Demand Intelligence | "
    "AI-Assisted Decision Support Platform"
)
