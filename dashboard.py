# Mengimport library yang dibutuhkan
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
sns.set(style='dark')

# Membuat class DataAnalyzer untuk analisis data
class DataAnalyzer:
    def __init__(self, df):
        self.df = df

    # Membuat fungsi produk paling banyak dibelii
    def get_top_categories(self, n=10):
        category_counts = self.df['product_category_name'].value_counts().reset_index()
        category_counts.columns = ['product_category_name', 'total_orders']
        return category_counts.head(n)

    # Membuat fungsi produk paling sedikit dibeli
    def get_bottom_ordered_categories(self, top_n=10):
        category_counts = self.df.groupby("product_category_name").size().reset_index(name="total_orders")
        return category_counts.nsmallest(top_n, "total_orders")

    # membuat untuk distribusi jenis pembayaran 
    def create_payment_distribution_df(self):
        payment_counts = self.df['payment_type'].value_counts(normalize=True).reset_index()
        payment_counts.columns = ['payment_type', 'percentage']
        return payment_counts

    # Membuat fungsi total order setiap negara bagian
    def get_state_transaction_counts(self):
        state_transaction_counts = self.df.groupby("customer_state")["order_id"].count().reset_index()
        state_transaction_counts.columns = ["customer_state", "total_orders"]
        return state_transaction_counts

    # Membuat fungsi RFM
    def calculate_rfm(self):
        rfm_df = self.df.groupby(by="customer_id", as_index=False).agg({
            "order_purchase_timestamp": "max",
            "order_id": "nunique",
            "payment_value": "sum"
        })
        rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

        rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"]).dt.date
        recent_date = self.df["order_purchase_timestamp"].max().date()
        rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
        rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

        return rfm_df

# Meload dataset
all_df = pd.read_csv("all_df.csv")

# Mengonversi kolom waktu
datetime_cols = [
    "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date",
    "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date_y"
]

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

# Menentukan rentang tanggal untuk filter date
min_date = all_df["order_approved_at"].min().date()
max_date = all_df["order_approved_at"].max().date()

# Membuat sitebar untuk menempatkann filter date
with st.sidebar:
    st.image("Elshopping.png")
    st.header("E-Commerce Dashboard")
    start_date, end_date = st.date_input(
        label='Time Period',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data berdasarkan tanggal yang dipilih
main_df = all_df[(all_df["order_approved_at"].dt.date >= start_date) & 
        (all_df["order_approved_at"].dt.date <= end_date)]

# Membuat instance class baru
analyzer = DataAnalyzer(main_df)

# Membuat Judul Dashboard
st.header('El-shopping E-Commerce Dashboard :goat:')

# Top Most and Bottom Least Purchased Categories Visualization 
st.subheader("Top Most and Bottom Least Purchased Categories")

# Membuat dua kolom
col1, col2 = st.columns(2)

# Mengambil data kategori
top_categories = analyzer.get_top_categories()
bottom_categories = analyzer.get_bottom_ordered_categories()

# Memberi text wrap agar tulisan tida terlalu panjang
import textwrap
def wrap_labels(ax, width=20):
    labels = [textwrap.fill(label.get_text(), width) for label in ax.get_yticklabels()]
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10)

# Menampilkan 10 kategori teratas
with col1:
    st.caption("Top 10 Most Ordered Categories")
    fig, ax = plt.subplots(figsize=(5, 5))
    sns.barplot(
        x="total_orders", 
        y="product_category_name", 
        data=top_categories, 
        hue="product_category_name", 
        dodge=False, 
        palette="Blues_r", ax=ax)
    ax.set_xlabel("Total Orders", fontsize=10)
    ax.set_ylabel("Product Category", fontsize=10)
    wrap_labels(ax, width=15)
    st.pyplot(fig)

# menampilkan 10 kategori terbawah
with col2:
    st.caption("Bottom 10 Least Ordered Categories")
    fig, ax = plt.subplots(figsize=(5, 5))
    sns.barplot(
        x="total_orders",
        y="product_category_name", 
        data=bottom_categories, 
        hue="product_category_name", 
        dodge=False, 
        palette="Reds_r", ax=ax)
    ax.set_xlabel("Total Orders", fontsize=10)
    ax.set_ylabel("Product Category", fontsize=10)
    wrap_labels(ax, width=15)
    st.pyplot(fig)

# Distribution of Most Customer Payment Methods Visualization #
st.subheader("Distribution of Most Customer Payment Methods")
payment_counts = analyzer.create_payment_distribution_df()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=payment_counts, 
    x="payment_type", 
    y="percentage", 
    hue="payment_type", 
    dodge=False, 
    palette="Reds_r", ax=ax)
ax.set_xlabel("Payment Methods", fontsize=14)
ax.set_ylabel("Percentage", fontsize=14)

# Menambahkan presentase disetiap bar chart
for i, v in enumerate(payment_counts["percentage"]):
    ax.text(i, v + 0.01, f'{v*100:.1f}%', ha='center', fontsize=12)

st.pyplot(fig)

# Top Number Transaction per State Visualization # 
st.subheader("Top Number of Transactions per State")
state_transaction_counts = analyzer.get_state_transaction_counts()
state_transaction_counts = state_transaction_counts.sort_values(by="total_orders", ascending=False)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x="customer_state", 
            y="total_orders", 
            data=state_transaction_counts, 
            hue="customer_state", 
            dodge=False, 
            palette="Blues_r", ax=ax)
ax.set_xlabel("Customer State", fontsize=12)
ax.set_ylabel("Total Orders", fontsize=12)
plt.xticks(rotation=45)

st.pyplot(fig)

# RFM Visualization #
rfm = analyzer.calculate_rfm()

# **Top 5 Customers berdasarkan RFM**
top_recency = rfm.nsmallest(5, 'recency')
top_frequency = rfm.nlargest(5, 'frequency')
top_monetary = rfm.nlargest(5, 'monetary')

st.subheader("Best Customers Based on RFM Parameters")

# Membuat tab
tab1, tab2, tab3 = st.tabs(["Recency", "Frequency", "Monetary"])

# Plot bar untuk recency
with tab1:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        y=top_recency['customer_id'].astype(str), 
        x=top_recency['recency'], 
        hue=top_recency['customer_id'].astype(str), 
        palette='Blues', 
        legend=False, ax=ax)
    ax.set_title('Top 5 Customers by Recency')
    st.pyplot(fig)
    with st.expander("See Explanation"):
        st.write('Terdapat 5 pelanggan teratas yang menunjukkan baru belanja beberapa hari terakhir. ini menunjukkan E-Commerce masih berjalan dengan baik.')

# Plot bar untuk Frequency
with tab2:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        y=top_frequency['customer_id'].astype(str), 
        x=top_frequency['frequency'], 
        hue=top_frequency['customer_id'].astype(str), 
        palette='Greens', 
        legend=False, ax=ax)
    ax.set_title('Top 5 Customers by Frequency')
    st.pyplot(fig)
    with st.expander("See Explanation"):
        st.write(
            'Terdapat 5 pelanggan teratas yang memiliki jumlah order tertinggi. ini menunjukkan bahwa mereka selalu mengandalkan E-commerce untuk membeli kebutuhan rumah dan lainnya.')

# Plot bar untuk Monetary
with tab3:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        y=top_monetary['customer_id'].astype(str), 
        x=top_monetary['monetary'], 
        hue=top_monetary['customer_id'].astype(str), 
        palette='Oranges', 
        legend=False, ax=ax)
    ax.set_title('Top 5 Customers by Monetary Value')
    ax.set_xscale("log")
    st.pyplot(fig)
    with st.expander("See Explanation"):
        st.write('Terdapat 5 pelanggan teratas yang mengeluarkan uang belanja yang tinggi. Ini menunjukkan mereka sering melakukan pembelian dengan nilai order yang besar.')
