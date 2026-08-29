# FORESIGHT 📊
### Retail Demand Intelligence & Inventory Decision Support Platform

FORESIGHT is a retail analytics and inventory decision-support platform built with Python and Streamlit.

It helps businesses analyze historical sales, understand demand trends, estimate future demand, monitor inventory health, calculate reorder points, and generate actionable replenishment recommendations.

---

## 🚀 Key Features

### 📊 Executive Dashboard
- Total units sold
- Average daily demand
- Peak demand
- Revenue analytics
- Current demand forecast

### 📈 Demand Analytics
- Historical demand trends
- Product-level sales analysis
- Sales share by product
- Best-selling product identification

### 🤖 Demand Forecasting
- 7, 14, 21 and 30-day forecast horizons
- Recent demand trend analysis
- Forecast range based on demand volatility
- Automated demand interpretation

### 📦 Inventory Intelligence
- Current stock monitoring
- Daily demand forecast
- Safety stock calculation
- Reorder point calculation
- Days of inventory cover
- Recommended order quantity

### 🚨 Smart Inventory Alerts
- 🔴 ORDER NOW
- 🟡 MONITOR
- 🟢 STOCK OK

### 📤 Data & Reporting
- CSV sales data upload
- Date filtering
- Product filtering
- Inventory CSV export
- Excel report generation

---

## 🧮 Inventory Decision Logic

FORESIGHT uses demand and inventory metrics to support replenishment decisions.

### Reorder Point

```text
Reorder Point =
Daily Forecast × Lead Time
+ Safety Stock
