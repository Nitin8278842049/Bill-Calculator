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
.stApp { background-color: white; }
.logo-container { text-align: center; margin-bottom: 5px; }
.logo-container img { max-width: 160px; }
.title { text-align: center; color: #005aa2; font-size: 28px; font-weight: 800; }
.subtitle { text-align: center; color: #555; font-size: 14px; margin-bottom: 15px; }
.card { background: white; padding: 18px; border-radius: 6px; border: 1px solid #dcdcdc; margin-bottom: 15px; }
.section { background: #eef7ff; padding: 8px; border-radius: 4px; font-weight: 700; color: #005aa2; margin-top: 10px; border: 1px solid #d0e7ff; }
.row { display: flex; justify-content: space-between; padding: 8px; font-size: 14px; border: 1px solid #e6e6e6; margin-top: 4px; }
.calc { font-size: 13px; color: #444; margin-left: 6px; margin-bottom: 6px; }
.total { font-size: 22px; font-weight: 800; text-align: right; padding-top: 10px; }
.green { color: #1a7f37; font-weight: 600; }
div.stButton > button { background-color: #005aa2; color: white; font-size: 16px; font-weight: 700; height: 45px; width: 100%; }
label { font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown(f"""
<div class="logo-container">
    <img src="data:image/png;base64,{logo_base64}">
</div>
<div class="title">TATA POWER BILL CALCULATOR</div>
<div class="subtitle">Mumbai Based Regional Tariff</div>
""", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox("Network Type", ["Welcome (AEML Network)", "Direct (Tata Power Network)"])
mu_text = st.text_input("Metered Units (MU)")
su_text = st.text_input("Solar Units (BU)")
load_text = st.text_input("Sanctioned Load (kW)")

calculate = st.button("Calculate")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATIONS ---------------- #
if calculate:

    try:
        mu = float(mu_text)
        su = float(su_text)
        load_kw = float(load_text)
    except:
        st.error("Please enter valid numeric values.")
        st.stop()

    # -------- BU Calculation --------
    if "Welcome" in network:
        bu = mu * 1.05785
        wheeling_rate = 2.93
    else:
        bu = mu
        wheeling_rate = 2.76

    if su > bu:
        st.error("Solar units cannot exceed BU.")
        st.stop()

    # -------- Energy Charges --------
    s1 = min(bu, 100) * 2.00
    s2 = min(max(bu - 100, 0), 200) * 5.20
    s3 = min(max(bu - 300, 0), 200) * 10.79
    s4 = max(bu - 500, 0) * 11.79

    total_energy = s1 + s2 + s3 + s4
    wheeling = mu * wheeling_rate
    solar_rebate = su * 0.50

    # ======================================================
    # ✅ SANCTIONED LOAD FIXED CHARGE LOGIC
    # ======================================================

    base_fixed = 160  # 3-phase residential base

    if load_kw > 10:
        load_above_10 = load_kw - 10
        additional_blocks = math.ceil(load_above_10 / 10)
        additional_fixed = additional_blocks * 250
    else:
        load_above_10 = 0
        additional_blocks = 0
        additional_fixed = 0

    total_fixed = base_fixed + additional_fixed

    # -------- Duty & TOSE --------
    duty_base = max(total_energy + wheeling + total_fixed - solar_rebate, 0)
    duty = duty_base * 0.16
    tose = bu * 0.3594

    total = total_energy + wheeling + total_fixed + duty + tose - solar_rebate

    # ================= RESULTS =================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section">Fixed Charge Detailed Calculation</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Base Fixed Charge (3-Phase)</span><span>₹{base_fixed}</span></div>', unsafe_allow_html=True)

    if load_kw > 10:
        st.markdown(f'<div class="row"><span>Additional Fixed Charges</span><span>₹{additional_fixed}</span></div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="calc">
        Load above 10 kW = {load_kw} − 10 = {load_above_10:.2f} kW<br>
        Charge = ₹250 per 10 kW or part thereof<br>
        {load_above_10:.2f} ÷ 10 = {additional_blocks}<br>
        {additional_blocks} × 250 = ₹{additional_fixed}
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="row"><strong>Total Fixed Charges</strong><strong>₹{total_fixed}</strong></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Final Bill Summary</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Energy Charges</span><span>₹{total_energy:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Wheeling Charges</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Electricity Duty (16%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>TOSE</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row green"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total):,}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
