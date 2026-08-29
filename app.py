import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# =========================================================
# FORESIGHT
# Retail Demand Intelligence & AI-Assisted
# Inventory Decision Support Platform
# =========================================================

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
SEASONAL_PERIOD = 7

# =========================================================
# CUSTOM STYLE
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

    .small-note {
        color: #777;
        font-size: 14px;
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

            # Weekend demand effect
            if date.weekday() >= 5:
                demand *= 1.10

            # Random demand variation
            demand += np.random.normal(0, 25)

            demand = max(
                0,
                int(demand)
            )

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

        st.sidebar.success(
            "✅ CSV loaded successfully"
        )

    except Exception as e:

        st.error(
            f"Unable to read CSV: {e}"
        )

        st.stop()

else:

    df = create_demo_data()

    st.sidebar.info(
        "Demo data active"
    )


# =========================================================
# VALIDATION
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
        "Required columns: Date, Sales. "
        "Recommended: Product, Price, Inventory."
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
    subset=[
        "Date",
        "Sales"
    ]
).copy()


# =========================================================
# PRODUCT
# =========================================================
if "Product" not in df.columns:

    df["Product"] = "All Products"


df["Product"] = (
    df["Product"]
    .astype(str)
)


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

    df["Price"] = 0

    df["Revenue"] = 0


# =========================================================
# INVENTORY
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
    value=(
        min_date,
        max_date
    ),
    min_value=min_date,
    max_value=max_date
)


if (
    isinstance(date_range, tuple)
    and len(date_range) == 2
):

    start_date, end_date = date_range

    filtered_df = df[
        (
            df["Date"].dt.date
            >= start_date
        )
        &
        (
            df["Date"].dt.date
            <= end_date
        )
    ].copy()

else:

    filtered_df = df.copy()


# =========================================================
# PRODUCT FILTER
# =========================================================
product_options = sorted(
    filtered_df["Product"]
    .dropna()
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
        .isin(selected_products)
    ].copy()


# =========================================================
# EMPTY DATA CHECK
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

total_sales = (
    daily_sales.sum()
)

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

recent_forecast = (
    daily_sales
    .tail(
        min(
            14,
            len(daily_sales)
        )
    )
    .mean()
    if len(daily_sales) > 0
    else 0
)


# =========================================================
# FORECAST FUNCTIONS
# =========================================================
def seasonal_naive_forecast(
    series,
    horizon=7,
    season=7
):

    series = (
        series
        .sort_index()
        .dropna()
    )

    future_dates = pd.date_range(
        start=(
            series.index.max()
            + pd.Timedelta(days=1)
        ),
        periods=horizon
    )

    if len(series) < season:

        values = [
            series.mean()
            for _ in range(horizon)
        ]

        return pd.Series(
            values,
            index=future_dates
        )

    values = []

    for i in range(horizon):

        source_position = (
            len(series)
            - season
            + (i % season)
        )

        if (
            source_position >= 0
            and source_position < len(series)
        ):

            value = series.iloc[
                source_position
            ]

        else:

            value = series.mean()

        values.append(
            max(
                0,
                value
            )
        )

    return pd.Series(
        values,
        index=future_dates
    )


def wape(
    actual,
    predicted
):

    actual = np.asarray(
        actual
    )

    predicted = np.asarray(
        predicted
    )

    denominator = np.sum(
        np.abs(actual)
    )

    if denominator == 0:

        return np.nan

    return (
        np.sum(
            np.abs(
                actual - predicted
            )
        )
        / denominator
    ) * 100


def forecast_bias(
    actual,
    predicted
):

    actual = np.asarray(
        actual
    )

    predicted = np.asarray(
        predicted
    )

    denominator = np.sum(
        np.abs(actual)
    )

    if denominator == 0:

        return 0

    return (
        np.sum(
            predicted - actual
        )
        / denominator
    ) * 100


def rolling_backtest(
    series,
    horizon=7,
    season=7
):

    series = (
        series
        .sort_index()
        .dropna()
    )

    minimum_history = (
        season
        + horizon
        + 14
    )

    if len(series) < minimum_history:

        return None

    actual_values = []
    predicted_values = []

    start = (
        season
        + 14
    )

    end = (
        len(series)
        - horizon
        + 1
    )

    for split in range(
        start,
        end,
        horizon
    ):

        train = series.iloc[
            :split
        ]

        test = series.iloc[
            split:
            split + horizon
        ]

        if len(test) == 0:
            continue

        prediction = (
            seasonal_naive_forecast(
                train,
                horizon=len(test),
                season=season
            )
        )

        actual_values.extend(
            test.values
        )

        predicted_values.extend(
            prediction.values
        )

    if len(actual_values) == 0:

        return None

    return {
        "WAPE": wape(
            actual_values,
            predicted_values
        ),
        "Bias": forecast_bias(
            actual_values,
            predicted_values
        )
    }


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

    revenue = (
        filtered_df["Revenue"]
        .sum()
    )

    if revenue > 0:

        st.metric(
            "Revenue",
            f"₹{revenue:,.0f}"
        )

    else:

        st.metric(
            "Products",
            str(
                filtered_df[
                    "Product"
                ].nunique()
            )
        )


with k5:

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
    daily_sales.rename(
        "Demand"
    ),
    height=350
)


# =========================================================
# AI DEMAND FORECAST
# =========================================================
st.markdown(
    '<div class="section-title">'
    '🤖 AI-Assisted Demand Forecast'
    '</div>',
    unsafe_allow_html=True
)

forecast_days = st.select_slider(
    "Forecast Horizon",
    options=[
        7,
        14,
        21,
        30
    ],
    value=14
)


forecast_df = None
backtest_result = None


if len(daily_sales) >= 14:

    recent_data = (
        daily_sales.tail(14)
    )

    previous_data = (
        daily_sales.iloc[-28:-14]
    )

    recent_avg = (
        recent_data.mean()
    )

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
            (
                recent_avg
                - previous_avg
            )
            / previous_avg
        ) * 100

    else:

        trend_pct = 0


    # Prevent unrealistic jumps
    trend_pct = max(
        -20,
        min(
            trend_pct,
            20
        )
    )


    # -----------------------------------------------------
    # VOLATILITY
    # -----------------------------------------------------
    volatility = (
        recent_data.std()
    )

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

        progress = (
            day
            / forecast_days
        )

        trend_factor = (
            1
            + (
                trend_pct
                / 100
            )
            * progress
        )

        value = (
            recent_avg
            * trend_factor
        )

        forecast_values.append(
            max(
                0,
                value
            )
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
            "Forecast":
                forecast_values
        },
        index=forecast_dates
    )


    # -----------------------------------------------------
    # HISTORICAL + FORECAST
    # -----------------------------------------------------
    chart_data = pd.concat(
        [
            daily_sales
            .tail(30)
            .rename("Historical"),

            forecast_df[
                "Forecast"
            ]
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
        forecast_df[
            "Forecast"
        ].mean()
    )

    forecast_total = (
        forecast_df[
            "Forecast"
        ].sum()
    )

    confidence_margin = (
        volatility
        * 1.28
    )

    lower_forecast = max(
        0,
        forecast_avg
        - confidence_margin
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
    # FORECAST INTERPRETATION
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


    # =====================================================
    # MODEL EVALUATION
    # =====================================================
    st.markdown(
        "### 📏 Forecast Model Evaluation"
    )

    backtest_result = (
        rolling_backtest(
            daily_sales,
            horizon=7,
            season=SEASONAL_PERIOD
        )
    )


    if backtest_result is not None:

        e1, e2, e3 = st.columns(3)


        with e1:

            st.metric(
                "Seasonal-Naive WAPE",
                f"{backtest_result['WAPE']:.1f}%"
            )


        with e2:

            st.metric(
                "Forecast Bias",
                f"{backtest_result['Bias']:+.1f}%"
            )


        with e3:

            st.metric(
                "Evaluation Horizon",
                "7 Days"
            )


        if (
            backtest_result["WAPE"]
            <= 20
        ):

            st.success(
                "✅ Forecast baseline performance "
                "is strong."
            )

        elif (
            backtest_result["WAPE"]
            <= 35
        ):

            st.warning(
                "⚠️ Forecast accuracy is moderate. "
                "Additional demand drivers may improve "
                "forecast performance."
            )

        else:

            st.error(
                "🚨 Forecast error is relatively high. "
                "Use the forecast with caution."
            )


        st.caption(
            "Evaluation uses rolling-origin "
            "backtesting against a "
            "7-day seasonal-naive baseline."
        )

    else:

        st.info(
            "At least 28 days of historical demand "
            "are recommended for backtesting."
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
        Units_Sold=(
            "Sales",
            "sum"
        ),
        Revenue=(
            "Revenue",
            "sum"
        )
    )
    .sort_values(
        "Units_Sold",
        ascending=False
    )
)


st.bar_chart(
    product_summary[
        "Units_Sold"
    ],
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
    product_table[
        "Units Sold"
    ].sum()
)


if total_units > 0:

    product_table[
        "Sales Share (%)"
    ] = (
        product_table[
            "Units Sold"
        ]
        / total_units
        * 100
    ).round(1)


st.dataframe(
    product_table,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# SMART INVENTORY INTELLIGENCE
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
    filtered_df[
        "Product"
    ]
    .dropna()
    .astype(str)
    .unique()
)


for product in inventory_products:

    product_data = (
        filtered_df[
            filtered_df[
                "Product"
            ].astype(str)
            == product
        ]
        .copy()
    )


    product_daily = (
        product_data
        .groupby("Date")[
            "Sales"
        ]
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
    # CURRENT INVENTORY
    # -----------------------------------------------------
    if "Inventory" in product_data.columns:

        inventory_values = (
            product_data[
                "Inventory"
            ]
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

        demand_std = (
            product_daily.std()
        )

    else:

        demand_std = 0


    if pd.isna(demand_std):

        demand_std = 0


    # -----------------------------------------------------
    # SAFETY STOCK
    # -----------------------------------------------------
    safety_stock = (
        demand_std
        * np.sqrt(
            LEAD_TIME_DAYS
        )
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
    # PRICE
    # -----------------------------------------------------
    product_price = (
        pd.to_numeric(
            product_data[
                "Price"
            ],
            errors="coerce"
        )
        .fillna(0)
        .mean()
    )


    # -----------------------------------------------------
    # STOCKOUT RISK
    # -----------------------------------------------------
    shortage_units = max(
        0,
        int(
            np.ceil(
                reorder_point
                - current_stock
            )
        )
    )


    stockout_risk = (
        current_stock
        <= reorder_point
    )


    # -----------------------------------------------------
    # OVERSTOCK RISK
    # -----------------------------------------------------
    overstock_threshold = (
        product_forecast
        * TARGET_STOCK_DAYS
        * 1.50
        + safety_stock
    )


    overstock_risk = (
        current_stock
        >= overstock_threshold
    )


    # -----------------------------------------------------
    # BUSINESS IMPACT
    # -----------------------------------------------------
    sales_at_risk = (
        shortage_units
        * product_price
    )


    locked_capital = (
        current_stock
        * product_price
    )


    # -----------------------------------------------------
    # DECISION ENGINE
    # -----------------------------------------------------
    if stockout_risk:

        status = "🔴 REORDER"

        decision = (
            "Replenish inventory"
        )

    elif overstock_risk:

        status = "🟠 OVERSTOCK"

        decision = (
            "Consider markdown / promotion"
        )

    elif (
        current_stock
        <= reorder_point * 1.25
    ):

        status = "🟡 WATCH"

        decision = (
            "Monitor inventory"
        )

    else:

        status = "🟢 HEALTHY"

        decision = (
            "No immediate action"
        )


    # -----------------------------------------------------
    # INVENTORY RECORD
    # -----------------------------------------------------
    inventory_data.append(
        {
            "Product":
                product,

            "Current Stock":
                int(current_stock),

            "Daily Forecast":
                round(
                    product_forecast
                ),

            "Safety Stock":
                round(
                    safety_stock
                ),

            "Reorder Point":
                round(
                    reorder_point
                ),

            "Days of Cover":
                round(
                    days_cover,
                    1
                ),

            "Recommended Order":
                recommended_order,

            "Shortage Units":
                shortage_units,

            "Sales at Risk":
                round(
                    sales_at_risk
                ),

            "Locked Capital":
                round(
                    locked_capital
                ),

            "Risk":
                status,

            "Recommended Action":
                decision
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
    inventory_df[
        "Current Stock"
    ].sum()
)

safety_total = (
    inventory_df[
        "Safety Stock"
    ].sum()
)

order_total = (
    inventory_df[
        "Recommended Order"
    ].sum()
)

reorder_count = (
    inventory_df[
        "Risk"
    ]
    .eq("🔴 REORDER")
    .sum()
)

overstock_count = (
    inventory_df[
        "Risk"
    ]
    .eq("🟠 OVERSTOCK")
    .sum()
)

watch_count = (
    inventory_df[
        "Risk"
    ]
    .eq("🟡 WATCH")
    .sum()
)

healthy_count = (
    inventory_df[
        "Risk"
    ]
    .eq("🟢 HEALTHY")
    .sum()
)

total_sales_at_risk = (
    inventory_df[
        "Sales at Risk"
    ].sum()
)

total_locked_capital = (
    inventory_df[
        "Locked Capital"
    ].sum()
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
        "Reorder Items",
        str(reorder_count)
    )


# =========================================================
# RISK KPIs
# =========================================================
r1, r2, r3, r4 = st.columns(4)


with r1:

    st.metric(
        "Overstock Items",
        str(overstock_count)
    )


with r2:

    st.metric(
        "Watch Items",
        str(watch_count)
    )


with r3:

    st.metric(
        "Sales at Risk",
        f"₹{total_sales_at_risk:,.0f}"
    )


with r4:

    st.metric(
        "Locked Capital",
        f"₹{total_locked_capital:,.0f}"
    )


# =========================================================
# INVENTORY DECISION GRID
# =========================================================
st.markdown(
    "### 🎯 Inventory Decision Grid"
)


decision_columns = [
    "Product",
    "Current Stock",
    "Daily Forecast",
    "Days of Cover",
    "Reorder Point",
    "Recommended Order",
    "Sales at Risk",
    "Locked Capital",
    "Risk",
    "Recommended Action"
]


st.dataframe(
    inventory_df[
        decision_columns
    ],
    use_container_width=True,
    hide_index=True
)


# =========================================================
# ORDER ALERT
# =========================================================
if reorder_count > 0:

    st.error(
        f"🚨 {reorder_count} product(s) "
        "require immediate reordering."
    )

    urgent = inventory_df[
        inventory_df[
            "Risk"
        ]
        == "🔴 REORDER"
    ]

    st.dataframe(
        urgent[
            [
                "Product",
                "Current Stock",
                "Daily Forecast",
                "Reorder Point",
                "Days of Cover",
                "Recommended Order",
                "Sales at Risk"
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


if overstock_count > 0:

    st.warning(
        f"🟠 {overstock_count} product(s) "
        "show potential overstock risk."
    )


if watch_count > 0:

    st.warning(
        f"🟡 {watch_count} product(s) "
        "should be monitored."
    )


# =========================================================
# INVENTORY CSV DOWNLOAD
# =========================================================
inventory_csv = (
    inventory_df
    .to_csv(
        index=False
    )
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

        if forecast_df is not None:

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

        if backtest_result is not None:

            evaluation_df = pd.DataFrame(
                {
                    "Metric": [
                        "WAPE",
                        "Forecast Bias"
                    ],
                    "Value": [
                        backtest_result[
                            "WAPE"
                        ],
                        backtest_result[
                            "Bias"
                        ]
                    ]
                }
            )

            evaluation_df.to_excel(
                writer,
                sheet_name="Model Evaluation",
                index=False
            )

    output.seek(0)

    return output


excel_file = (
    create_excel_report()
)


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

    st.markdown(
        "### 📈 Demand"
    )

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
                (
                    recent_avg
                    - old_avg
                )
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

    st.markdown(
        "### 🏆 Best Seller"
    )

    best_product = (
        filtered_df
        .groupby(
            "Product"
        )["Sales"]
        .sum()
        .idxmax()
    )

    best_sales = (
        filtered_df
        .groupby(
            "Product"
        )["Sales"]
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

    st.markdown(
        "### 🎯 Inventory Action"
    )

    if reorder_count > 0:

        st.error(
            f"{reorder_count} product(s) "
            "need ordering."
        )

    elif overstock_count > 0:

        st.warning(
            f"{overstock_count} product(s) "
            "show overstock risk."
        )

    elif watch_count > 0:

        st.warning(
            f"{watch_count} product(s) "
            "need monitoring."
        )

    else:

        st.success(
            "Inventory looks healthy."
        )


# =========================================================
# FORECASTING METHODOLOGY
# =========================================================
with st.expander(
    "🧠 Forecasting Methodology"
):

    st.write(
        """
        FORESIGHT uses a lightweight AI-assisted
        demand forecasting approach.

        • Recent demand is used as the primary signal.
        • A rolling comparison identifies demand trends.
        • Forecast growth is capped to avoid unrealistic jumps.
        • Demand volatility is used to estimate a forecast range.
        • A 7-day seasonal-naive baseline is used for
          rolling-origin backtesting.
        • WAPE measures forecast error.
        • Forecast Bias identifies systematic over/under forecasting.
        """
    )


# =========================================================
# INVENTORY METHODOLOGY
# =========================================================
with st.expander(
    "📦 Inventory Methodology"
):

    st.write(
        f"""
        Inventory recommendations use:

        • Supplier lead time: {LEAD_TIME_DAYS} days
        • Safety buffer: {SAFETY_BUFFER:.0%}
        • Target inventory coverage: {TARGET_STOCK_DAYS} days
        • Demand variability for safety stock
        • Reorder point for replenishment decisions
        • Days of cover for stock sufficiency
        • Sales-at-risk for potential lost revenue
        • Locked capital for inventory exposure
        """
    )


# =========================================================
# RAW DATA
# =========================================================
with st.expander(
    "🔍 View Raw Data"
):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# CSV FORMAT
# =========================================================
with st.expander(
    "📄 Recommended CSV Format"
):

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
