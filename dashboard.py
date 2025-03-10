# Mengimport library yang dibutuhkan
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
sns.set(style='dark')

# Membuat fungsi produk paling banyak dibelii
def get_top_categories(df, n=10):
    category_counts = df['product_category_name'].value_counts().reset_index()
    category_counts.columns = ['product_category_name', 'total_orders']
    return category_counts.head(n)

# Membuat fungsi produk paling sedikit dibeli
def get_bottom_ordered_categories(df, top_n=10):
    category_counts = df.groupby("product_category_name").size().reset_index(name="total_orders")
    return category_counts.nsmallest(top_n, "total_orders")

# membuat untuk distribusi jenis pembayaran
def create_payment_distribution_df(df):
    payment_counts = df['payment_type'].value_counts(normalize=True).reset_index()
    payment_counts.columns = ['payment_type', 'percentage']
    return payment_counts

# Membuat fungsi total order setiap negara bagian
def get_state_transaction_counts(df):
    state_transaction_counts = df.groupby("customer_state")["order_id"].count().reset_index()
    state_transaction_counts.columns = ["customer_state", "total_orders"]
    return state_transaction_counts

# Membuat fungsi RFM
def calculate_rfm(df):
    # Mengubah tipedata
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    reference_date = df['order_purchase_timestamp'].max()

    rfm = df.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (reference_date - x.max()).days,
        'order_id': 'count',
        'payment_value': 'sum'
    }).reset_index()

    rfm.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']
    return rfm



# Meload data untuk membuat Visualisasi
# Membuat Judul Dashboard
st.header('El-shopping E-Commerce Dashboard :goat:')

# Meload dataset
all_df = pd.read_csv("all_df.csv")

datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date",
                "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date_y"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Site Bar
with st.sidebar:
    # Logo
    st.image("Elshopping.png")
    st.header("E-Commerce Dashboard")

# Top Most and Bottom Least Purchased Categories Visualization 
st.subheader("Top Most and Bottom Least Purchased Categories")
import textwrap

# Membuat 2 kolom
col1, col2 = st.columns(2)

# Memberi text wrap agar tulisan tida terlalu panjang
def wrap_labels(ax, width=20):
    labels = [textwrap.fill(label.get_text(), width) for label in ax.get_yticklabels()]
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10)

# Menampilkan 10 kategori teratas
top_categories = get_top_categories(all_df)
# menampilkan 10 kategori terbawah
bottom_categories = get_bottom_ordered_categories(all_df)

# Plot Bar 1 (Top)
with col1:
    st.caption("Top 10 Most Ordered Categories")
    fig, ax = plt.subplots(figsize=(5, 5))
    sns.barplot(
        x="total_orders",
        y="product_category_name",
        hue="product_category_name", 
        data=top_categories,
        palette="Blues_r",
        ax=ax
    )
    ax.set_xlabel("Total Orders", fontsize=10)
    ax.set_ylabel("Product Category", fontsize=10)
    wrap_labels(ax, width=15)
    st.pyplot(fig)
    with st.expander("See Explanation"):
        st.write(
            'Cama_mesa_banho(beth_bath_table) merupakan produk paling banyak dibeli oleh customer. '
            'Hal ini menunjukkan bahwa perlengkapan kebutuhan rumah tangga seperti memiliki penjualan yang tinggi di pasar.')

# Plot Bar 2 (Bottom)
with col2:
    st.caption("Bottom 10 Least Ordered Categories")
    fig, ax = plt.subplots(figsize=(5, 5))
    sns.barplot(
        x="total_orders",
        y="product_category_name",
        hue="product_category_name", 
        data=bottom_categories,
        palette="Reds_r",
        ax=ax
    )
    ax.set_xlabel("Total Orders", fontsize=10)
    ax.set_ylabel("Product Category", fontsize=10)
    wrap_labels(ax, width=15) 
    st.pyplot(fig)
    with st.expander("See Explanation"):
        st.write(
            'seguros_e_servicos(security and services) merupakan produk paling sedikit dibeli oleh customer. '
            'Penyebabnya adalah kemungkinan kategori produk ini tidak terlalu penting bagi pelanggan dan tidak perlu dibeli melalui e-commerce.')
        
with st.expander("See Explanation"):
        st.write(
            'Strategi pemasaran untuk mendongkrak pasar penjualan seguros_e_servicos(security and services). '
            'Kedepannya yaitu mengedukasi para pelanggan pentingnya privacy and security di lingkungan rumah dan keluarga agar selalu aman.')



# Distribution of Most Customer Payment Methods Visualization #
# Buat data frame baru
payment_counts = create_payment_distribution_df(all_df)

# Menampilkan subheader di dashboard Streamlit
st.subheader("Distribution of Most Customer Payment Methods")

# Membuat figure dan bar chart
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=payment_counts,
    x="payment_type",
    y="percentage",
    hue="payment_type", 
    palette="Reds_r",
    ax=ax
)
# Menambahkan judul dan label
ax.set_xlabel("Payment Methods", fontsize=14)
ax.set_ylabel("Percentage", fontsize=14)

# Mengubah total data menjadi persen
for i, v in enumerate(payment_counts["percentage"]):
    ax.text(i, v + 0.01, f'{v*100:.1f}%', ha='center', fontsize=12)
st.pyplot(fig)

with st.expander("See Explanation"):
        st.write(
            'Method payment yang sering dipakai oleh customer yaitu Credit card yang tembus hingga 73%  dari semua customer '
            'Hal ini menunjukkan bahwa pelanggan lebih praktis menggunakan metode pembayaran ini karena tidak perlu ke minimarket atau agen marketplace untuk membayar dengan uang cash atau menukarnya dengan voucher.')


# Top Number Transaction per State Visualization # 
# Memanggil fungsi untuk mendapatkan data transaksi per negara bagian
state_transaction_counts = get_state_transaction_counts(all_df)
state_transaction_counts = state_transaction_counts.sort_values(by="total_orders", ascending=False)
st.subheader("Top Number of Transactions per State")
# Membuat border
fig, ax = plt.subplots(figsize=(12, 6))

# Membuat plot bar
sns.barplot(
    x="customer_state",
    y="total_orders",
    data=state_transaction_counts,
    palette="Blues_r",
    hue="customer_state",
    legend=False,
    ax=ax
)

# Menambahkan Label pada Plot
ax.set_xlabel("Customer State", fontsize=12)
ax.set_ylabel("Total Orders", fontsize=12)
plt.xticks(rotation=45)
st.pyplot(fig)

with st.expander("See Explanation"):
        st.write(
            'Sao Paulo(SP) paling banyak atas menduduki transaksi paling banyak dibanding ibu kota yang lainnya karena termasuk pusat ekonomi di Brazil dibandingkan negara bagian lainnya. '
            'Sao Paulo memiliki populasi penduduk yang tinggi serta keberadaan logistik beserta infrastrukturnya yang merata. Hal ini banyak seller yang mendirikan lokasi usahanya di Sao Paulo.')


# RFM Visualization #
# Meload data & hitung RFM
rfm = calculate_rfm(all_df)

# Mengambil 5 customer teratas
top_recency = rfm.nsmallest(5, 'Recency')
top_frequency = rfm.nlargest(5, 'Frequency')
top_monetary = rfm.nlargest(5, 'Monetary')

st.subheader("Best Customer Based on RFM Parameters")

# Membuat 3 tab untuk 3 kategori
tab1, tab2, tab3 = st.tabs(["Recency", "Frequency", "Monetary"])

# Plot bar untuk recency
with tab1:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(y=top_recency['customer_id'].astype(str), 
                x=top_recency['Recency'], 
                hue=top_recency['customer_id'].astype(str), 
                palette='Blues', legend=False, ax=ax)
    ax.set_title('Top 5 Customers by Recency')
    st.pyplot(fig)
    with st.expander("See Explanation"):
        st.write(
            'Terdapat 5 pelanggan teratas yang menunjukkan baru belanja beberapa hari terakhir. ini menunjukkan E-Commerce masih berjalan dengan baik.')

# Plot bar untuk Frequency
with tab2:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(y=top_frequency['customer_id'].astype(str), 
                x=top_frequency['Frequency'], 
                hue=top_frequency['customer_id'].astype(str), 
                palette='Greens', legend=False, ax=ax)
    ax.set_title('Top 5 Customers by Frequency')
    st.pyplot(fig)
    with st.expander("See Explanation"):
        st.write(
            'Terdapat 5 pelanggan teratas yang memiliki jumlah order tertinggi. ini menunjukkan bahwa mereka selalu mengandalkan E-commerce untuk membeli kebutuhan rumah dan lainnya.')

# Plot bar untuk Monetary
with tab3:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(y=top_monetary['customer_id'].astype(str), 
                x=top_monetary['Monetary'], 
                hue=top_monetary['customer_id'].astype(str), 
                palette='Oranges', legend=False, ax=ax)
    ax.set_title('Top 5 Customers by Monetary Value')
    ax.set_xscale("log")
    st.pyplot(fig)
    with st.expander("See Explanation"):
        st.write(
            'Terdapat 5 pelanggan teratas yang mengeluarkan uang belanja yang tinggi. Ini menunjukkan mereka sering melakukan pembelian dengan nilai order yang besar.')