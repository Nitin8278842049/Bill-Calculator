import streamlit as st
import base64
import math

st.set_page_config(page_title="Tata Power Bill Calculator", layout="centered")

# ---------- LOAD LOGO ----------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = get_base64_of_bin_file("logo.png")

# ---------------- CSS ---------------- #
st.markdown("""
<style>
.main-container { border: 2px solid #005aa2; padding: 20px; border-radius: 8px; }
.logo-container { text-align: center; margin-bottom: 5px; }
.logo-container img { max-width: 160px; }
.title { text-align: center; color: #005aa2; font-size: 28px; font-weight: 800; }
.subtitle { text-align: center; color: #555; font-size: 14px; margin-bottom: 15px; }
.section { background: #eef7ff; padding: 8px; border-radius: 4px; font-weight: 700; color: #005aa2; margin-top: 15px; }
.calc { font-size: 14px; margin-left: 10px; margin-bottom: 8px; color: #333; }
.total { font-size: 22px; font-weight: 800; text-align: right; padding-top: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown(f"""
<div class="logo-container">
<img src="data:image/png;base64,{logo_base64}">
</div>
<div class="title">TATA POWER BILL CALCULATOR</div>
<div class="subtitle">Mumbai Residential Tariff</div>
""", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
network = st.selectbox("Network Type", ["Welcome (AEML Network)", "Direct (Tata Power Network)"])
mu = st.number_input("Metered Units (MU)", min_value=0.0)
su = st.number_input("Solar Units (BU)", min_value=0.0)
load_kw = st.number_input("Sanctioned Load (kW)", min_value=0.0)

if st.button("Calculate"):

    if "Welcome" in network:
        bu = mu * 1.05785
        wheeling_rate = 2.93
    else:
        bu = mu
        wheeling_rate = 2.76

    if su > bu:
        st.error("Solar units cannot exceed Billed Units.")
        st.stop()

    # ===============================
    # 1️⃣ UNIT CONVERSION
    # ===============================
    st.markdown('<div class="section">1️⃣ Unit Conversion</div>', unsafe_allow_html=True)

    if "Welcome" in network:
        st.markdown(f'<div class="calc">BU = MU × 1.05785</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc">BU = {mu} × 1.05785 = {bu:.2f} Units</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="calc">BU = MU</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc">BU = {bu:.2f} Units</div>', unsafe_allow_html=True)

    # ===============================
    # 2️⃣ ENERGY CHARGES
    # ===============================
    st.markdown('<div class="section">2️⃣ Energy Charges (Slab-wise)</div>', unsafe_allow_html=True)

    s1_units = min(bu, 100)
    s2_units = min(max(bu - 100, 0), 200)
    s3_units = min(max(bu - 300, 0), 200)
    s4_units = max(bu - 500, 0)

    s1 = s1_units * 2.00
    s2 = s2_units * 5.20
    s3 = s3_units * 10.79
    s4 = s4_units * 11.79

    st.markdown(f'<div class="calc">0–100 Units: {s1_units:.2f} × 2.00 = ₹{s1:.2f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">101–300 Units: {s2_units:.2f} × 5.20 = ₹{s2:.2f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">301–500 Units: {s3_units:.2f} × 10.79 = ₹{s3:.2f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Above 500 Units: {s4_units:.2f} × 11.79 = ₹{s4:.2f}</div>', unsafe_allow_html=True)

    total_energy = s1 + s2 + s3 + s4
    st.markdown(f'<div class="calc"><b>Total Energy Charges = ₹{total_energy:.2f}</b></div>', unsafe_allow_html=True)

    # ===============================
    # 3️⃣ FIXED CHARGES
    # ===============================
    st.markdown('<div class="section">3️⃣ Fixed Charges (Sanctioned Load Based)</div>', unsafe_allow_html=True)

    base_fixed = 160
    st.markdown(f'<div class="calc">Base Fixed Charge (3-Phase) = ₹{base_fixed}</div>', unsafe_allow_html=True)

    if load_kw > 10:
        load_above = load_kw - 10
        blocks = math.ceil(load_above / 10)
        additional = blocks * 250

        st.markdown(f'<div class="calc">Load above 10 kW = {load_kw} − 10 = {load_above:.2f} kW</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc">Charge = ₹250 per 10 kW or part thereof</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc">{load_above:.2f} ÷ 10 = {blocks}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc">{blocks} × 250 = ₹{additional}</div>', unsafe_allow_html=True)
    else:
        additional = 0
        st.markdown(f'<div class="calc">No additional fixed charge (Load ≤ 10 kW)</div>', unsafe_allow_html=True)

    total_fixed = base_fixed + additional
    st.markdown(f'<div class="calc"><b>Total Fixed Charges = {base_fixed} + {additional} = ₹{total_fixed}</b></div>', unsafe_allow_html=True)

    # ===============================
    # 4️⃣ OTHER CHARGES
    # ===============================
    st.markdown('<div class="section">4️⃣ Other Charges</div>', unsafe_allow_html=True)

    wheeling = mu * wheeling_rate
    st.markdown(f'<div class="calc">Wheeling = {mu} × {wheeling_rate} = ₹{wheeling:.2f}</div>', unsafe_allow_html=True)

    solar_rebate = su * 0.50
    st.markdown(f'<div class="calc">Solar Rebate = {su} × 0.50 = ₹{solar_rebate:.2f}</div>', unsafe_allow_html=True)

    duty_base = total_energy + wheeling + total_fixed - solar_rebate
    duty = duty_base * 0.16
    st.markdown(f'<div class="calc">Electricity Duty = ({duty_base:.2f}) × 16% = ₹{duty:.2f}</div>', unsafe_allow_html=True)

    tose = bu * 0.3594
    st.markdown(f'<div class="calc">TOSE = {bu:.2f} × 0.3594 = ₹{tose:.2f}</div>', unsafe_allow_html=True)

    # ===============================
    # 5️⃣ FINAL BILL
    # ===============================
    total = total_energy + wheeling + total_fixed + duty + tose - solar_rebate

    st.markdown('<div class="section">5️⃣ Final Bill Amount</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc"><b>Net Bill = ₹{total:.2f}</b></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
