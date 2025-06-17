import streamlit as st
from auth.login import login_page
from cluster import cluster_dashboard


# Set default session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Halaman Login jika belum login
if not st.session_state.logged_in:
    login_page()
else:
    # Header dengan tombol logout
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("Dashboard Clustering Analysis")
    with col2:
        if st.button("Logout", type="secondary", help="Keluar dari aplikasi"):
            # Reset session state
            for key in st.session_state.keys():
                del st.session_state[key]
            st.session_state.logged_in = False
            st.success("✅ Berhasil logout!")
            st.rerun()
    
    st.markdown("---")
    # Tampilkan dashboard jika sudah login
    cluster_dashboard()
