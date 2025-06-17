# cluster.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import os

# Fungsi dashboard clustering
def cluster_dashboard():
    # Cek apakah file data ada
    data_path = "data/clustering.csv"
    if not os.path.exists(data_path):
        st.error(f"❌ File data '{data_path}' tidak ditemukan!")
        st.info("💡 Pastikan file clustering.csv ada di folder 'data/'")
        return
    
    try:
        # Load Data
        data = pd.read_csv(data_path)
        
        # Sidebar (Navbar)
        st.sidebar.title("Navigasi Dashboard")
        
        # Tombol logout di sidebar
        if st.sidebar.button("Logout", type="secondary", use_container_width=True):
            # Reset session state
            for key in st.session_state.keys():
                del st.session_state[key]
            st.session_state.logged_in = False
            st.success("✅ Berhasil logout!")
            st.rerun()
        
        st.sidebar.markdown("---")
        
        # Info user di sidebar
        st.sidebar.info(" **User:** Admin")
        st.sidebar.success(f"📊 **Total Data:** {len(data):,} records")
        
        st.sidebar.markdown("---")
        
        menu = st.sidebar.radio(
            "Pilih Visualisasi:",
            (
                "📋 Preview Dataset",
                "📊 Distribusi Cluster", 
                "🔍 Elbow Method",
                "📌 Scatter Plot Clustering",
                "📈 Penjualan 2023 & 2024",
                "🏆 Produk Terlaris & Tidak Laku",
                "📅 Penjualan Bulanan (Gabungan)",
                "📆 Penjualan Tahunan",
                "📊 Penjualan Bulanan per Tahun"
            )
        )

        # Konten Berdasarkan Menu
        if menu == "📋 Preview Dataset":
            st.header("📋 Preview Dataset")
            st.markdown("**Informasi Dataset:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Baris", len(data))
            with col2:
                st.metric("Total Kolom", len(data.columns))
            with col3:
                st.metric("Missing Values", data.isnull().sum().sum())
            with col4:
                if 'cluster' in data.columns:
                    st.metric("Jumlah Cluster", data['cluster'].nunique())
            
            st.subheader("📊 5 Data Teratas")
            st.dataframe(data.head(), use_container_width=True)
            
            st.subheader("📈 Statistik Deskriptif")
            st.dataframe(data.describe(), use_container_width=True)

        elif menu == "📊 Distribusi Cluster":
            st.header("📊 Distribusi Data per Cluster")
            if 'cluster' in data.columns:
                cluster_count = data['cluster'].value_counts().sort_index()
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    fig_cluster = px.bar(
                        x=cluster_count.index.astype(str),
                        y=cluster_count.values,
                        labels={'x': 'Cluster', 'y': 'Jumlah Data'},
                        title='Jumlah Data pada Setiap Cluster',
                        color=cluster_count.index.astype(str),
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    fig_cluster.update_layout(showlegend=False)
                    st.plotly_chart(fig_cluster, use_container_width=True)
                
                with col2:
                    st.subheader("📊 Detail Cluster")
                    for cluster in sorted(data['cluster'].unique()):
                        count = len(data[data['cluster'] == cluster])
                        percentage = (count / len(data)) * 100
                        st.metric(f"Cluster {cluster}", f"{count:,}", f"{percentage:.1f}%")
            else:
                st.error("❌ Kolom 'cluster' tidak ditemukan dalam dataset!")
            
        elif menu == "🔍 Elbow Method":
            st.header("🔍 Menentukan Jumlah Cluster: Elbow Method")
            
            # Cek kolom yang diperlukan
            required_cols = ['QUANTITY', 'HARGA SATUAN', 'JUMLAH']
            missing_cols = [col for col in required_cols if col not in data.columns]
            
            if missing_cols:
                st.error(f"❌ Kolom berikut tidak ditemukan: {missing_cols}")
                return
            
            numerik_data = data[required_cols].dropna()
            
            if len(numerik_data) == 0:
                st.error("❌ Tidak ada data numerik yang valid!")
                return
            
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(numerik_data)

            with st.spinner("🔄 Menghitung WCSS untuk setiap cluster..."):
                wcss = []
                K = range(1, 11)
                for k in K:
                    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                    kmeans.fit(scaled_data)
                    wcss.append(kmeans.inertia_)

            fig_elbow = plt.figure(figsize=(10, 6))
            plt.plot(K, wcss, 'bo-', linewidth=2, markersize=8)
            plt.xlabel('Jumlah Cluster', fontsize=12)
            plt.ylabel('WCSS (Within-Cluster Sum of Squares)', fontsize=12)
            plt.title('Elbow Method untuk Menentukan Jumlah Cluster Optimal', fontsize=14)
            plt.grid(True, alpha=0.3)
            st.pyplot(fig_elbow, use_container_width=True)
            
            st.info("💡 **Tip:** Pilih jumlah cluster di titik 'elbow' (siku) pada grafik untuk mendapatkan hasil clustering yang optimal.")

        elif menu == "📌 Scatter Plot Clustering":
            st.header("📌 Scatter Plot Clustering")
            
            if 'cluster' not in data.columns:
                st.error("❌ Kolom 'cluster' tidak ditemukan!")
                return
            
            required_cols = ['QUANTITY', 'JUMLAH']
            missing_cols = [col for col in required_cols if col not in data.columns]
            
            if missing_cols:
                st.error(f"❌ Kolom berikut tidak ditemukan: {missing_cols}")
                return
            
            fig_scatter = px.scatter(
                data,
                x='QUANTITY',
                y='JUMLAH',
                color='cluster',
                title='Scatter Plot: Quantity vs Total Harga per Cluster',
                labels={'QUANTITY': 'Quantity', 'JUMLAH': 'Total Harga (Rp)'},
                color_discrete_sequence=px.colors.qualitative.Set1,
                hover_data=['NAMA BARANG'] if 'NAMA BARANG' in data.columns else None
            )
            fig_scatter.update_layout(height=600)
            st.plotly_chart(fig_scatter, use_container_width=True)

        elif menu == "📈 Penjualan 2023 & 2024":
            st.header("📈 Visualisasi Penjualan Tahun 2023 & 2024")
            
            if 'TAHUN' not in data.columns or 'BULAN' not in data.columns:
                st.error("❌ Kolom 'TAHUN' atau 'BULAN' tidak ditemukan!")
                return
            
            for tahun in [2023, 2024]:
                if tahun in data['TAHUN'].values:
                    st.subheader(f"📊 Total Penjualan Tahun {tahun}")
                    data_tahun = data[data['TAHUN'] == tahun]
                    penjualan_bulanan = data_tahun.groupby('BULAN')['JUMLAH'].sum().reset_index()
                    
                    fig_tahun = px.bar(
                        penjualan_bulanan,
                        x='BULAN',
                        y='JUMLAH',
                        title=f"Total Penjualan per Bulan - {tahun}",
                        labels={'JUMLAH': 'Total Penjualan (Rp)', 'BULAN': 'Bulan'},
                        color='JUMLAH',
                        color_continuous_scale='Blues'
                    )
                    fig_tahun.update_layout(height=400)
                    st.plotly_chart(fig_tahun, use_container_width=True)
                    
                    # Tampilkan total penjualan tahun ini
                    total_tahun = data_tahun['JUMLAH'].sum()
                    st.info(f"💰 **Total Penjualan {tahun}:** Rp {total_tahun:,.0f}")
                else:
                    st.warning(f"⚠️ Data untuk tahun {tahun} tidak ditemukan.")

        elif menu == "🏆 Produk Terlaris & Tidak Laku":
            st.header("🏆 Produk Terlaris dan Paling Tidak Laku")
            
            if 'NAMA BARANG' not in data.columns or 'QUANTITY' not in data.columns:
                st.error("❌ Kolom 'NAMA BARANG' atau 'QUANTITY' tidak ditemukan!")
                return
            
            top_barang = data.groupby('NAMA BARANG')['QUANTITY'].sum().sort_values(ascending=False)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🥇 5 Produk Terlaris")
                top_5 = top_barang.head(5).reset_index()
                st.dataframe(top_5, use_container_width=True)
                
            with col2:
                st.subheader("📉 5 Produk Paling Tidak Laku")
                bottom_5 = top_barang.tail(5).reset_index()
                st.dataframe(bottom_5, use_container_width=True)

            st.subheader("📊 Grafik 10 Produk Terlaris")
            fig_top = px.bar(
                top_barang.head(10).reset_index(),
                x='QUANTITY',
                y='NAMA BARANG',
                orientation='h',
                title="10 Produk Paling Laku",
                labels={'QUANTITY': 'Jumlah Terjual', 'NAMA BARANG': 'Produk'},
                color='QUANTITY',
                color_continuous_scale='Viridis'
            )
            fig_top.update_layout(height=600)
            st.plotly_chart(fig_top, use_container_width=True)

        elif menu == "📅 Penjualan Bulanan (Gabungan)":
            st.header("📅 Total Penjualan per Bulan (Gabungan Tahun)")
            
            if 'BULAN' not in data.columns or 'JUMLAH' not in data.columns:
                st.error("❌ Kolom 'BULAN' atau 'JUMLAH' tidak ditemukan!")
                return
            
            penjualan_bulanan = data.groupby('BULAN')['JUMLAH'].sum().reset_index()
            fig_bulan = px.bar(
                penjualan_bulanan,
                x='BULAN',
                y='JUMLAH',
                title="Total Penjualan per Bulan (Semua Tahun)",
                labels={'JUMLAH': 'Total Penjualan (Rp)', 'BULAN': 'Bulan'},
                color='JUMLAH',
                color_continuous_scale='Plasma'
            )
            fig_bulan.update_layout(height=500)
            st.plotly_chart(fig_bulan, use_container_width=True)

        elif menu == "📆 Penjualan Tahunan":
            st.header("📆 Total Penjualan per Tahun")
            
            if 'TAHUN' not in data.columns or 'JUMLAH' not in data.columns:
                st.error("❌ Kolom 'TAHUN' atau 'JUMLAH' tidak ditemukan!")
                return
            
            penjualan_tahunan = data.groupby('TAHUN')['JUMLAH'].sum().reset_index()
            fig_tahunan = px.bar(
                penjualan_tahunan,
                x='TAHUN',
                y='JUMLAH',
                title="Total Penjualan per Tahun",
                labels={'JUMLAH': 'Total Penjualan (Rp)', 'TAHUN': 'Tahun'},
                color='JUMLAH',
                color_continuous_scale='Oranges'
            )
            fig_tahunan.update_layout(height=500)
            st.plotly_chart(fig_tahunan, use_container_width=True)
            
            # Tampilkan perbandingan tahun
            if len(penjualan_tahunan) > 1:
                growth = ((penjualan_tahunan.iloc[-1]['JUMLAH'] - penjualan_tahunan.iloc[-2]['JUMLAH']) / penjualan_tahunan.iloc[-2]['JUMLAH']) * 100
                if growth > 0:
                    st.success(f"📈 **Pertumbuhan:** +{growth:.1f}% dari tahun sebelumnya")
                else:
                    st.error(f"📉 **Penurunan:** {growth:.1f}% dari tahun sebelumnya")

        elif menu == "📊 Penjualan Bulanan per Tahun":
            st.header("📊 Total Penjualan Bulanan per Tahun")
            
            required_cols = ['TAHUN', 'BULAN', 'JUMLAH']
            missing_cols = [col for col in required_cols if col not in data.columns]
            
            if missing_cols:
                st.error(f"❌ Kolom berikut tidak ditemukan: {missing_cols}")
                return
            
            penjualan_per_bulan_tahun = data.groupby(['TAHUN', 'BULAN'])['JUMLAH'].sum().reset_index()
            fig_bulan_tahun = px.bar(
                penjualan_per_bulan_tahun,
                x='BULAN',
                y='JUMLAH',
                color='TAHUN',
                barmode='group',
                title="Perbandingan Penjualan Bulanan Antar Tahun",
                labels={'JUMLAH': 'Total Penjualan (Rp)', 'BULAN': 'Bulan', 'TAHUN': 'Tahun'},
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            fig_bulan_tahun.update_layout(height=600)
            st.plotly_chart(fig_bulan_tahun, use_container_width=True)

    except FileNotFoundError:
        st.error("❌ File data tidak ditemukan!")
        st.info("💡 Pastikan file 'clustering.csv' ada di folder 'data/'")
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan: {str(e)}")
        st.info("💡 Periksa format data dan pastikan kolom yang diperlukan tersedia.")