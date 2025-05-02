import streamlit as st

st.markdown("<h1 style='text-align: center;'>Mining KBM (TO)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Exportable Transfit Ore (Intermediate)</p>", unsafe_allow_html=True)

# Ambil nilai dari session_state
date_input = st.session_state.get("date_input", None)
start_time = st.session_state.get("start_time_input", None)
end_time = st.session_state.get("end_time_input", None)
data_plan = st.session_state.get("data_plan", None)
summary_utilisasi = st.session_state.get("summary_utilisasi", None)

if date_input:
    st.write(f"Data dari halaman sebelumnya:")
    st.write(f"Tanggal: {date_input}")
    st.write(f"Start Time: {start_time}")
    st.write(f"End Time: {end_time}")
    st.write(summary_utilisasi)
else:
    st.warning("Input belum tersedia. Silakan isi dari halaman Summary Utilisasi.")