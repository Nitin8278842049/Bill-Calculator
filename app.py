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

.title { text-align: center; color: #005aa2; font-size: 26px; font-weight: 800; }
.subtitle { text-align: center; color: #555; font-size: 13px; margin-bottom: 15px; }

.section {
    background: #dbeeff;
    padding: 10px;
    font-weight: 700;
    color: #005aa2;
    border: 1px solid #b5d7ff;
    margin-top: 15px;
}

.row {
    display: flex;
    justify-content: space-between;
    padding: 8px;
    border: 1px solid #e0e0e0;
    font-size: 14px;
}

.calc {
    font-size: 12px;
    color: #666;
    margin: 4px 0 8px 8px;
}

.total {
    font-size: 20px;
    font-weight: 800;
    text-align: right;
    margin-top: 15px;
}

.green { color: green; font-weight: 600; }
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

# Integer-only inputs — no decimals
mu = st.number_input("Metered Units (MU)", min_value=0, step=1, format="%d")
su = st.number_input("Solar Units (BU)", min_value=0, step=1, format="%d")
load_kw = st.number_input("Sanctioned Load (kW)", min_value=0, step=1, format="%d")

if st.button("Calculate"):

    # -------- BU Calculation --------
    if "Welcome" in network:
        bu = mu * 1.05785
        wheeling_rate = 2.93
        bu_calc = f"Calculation : BU = {mu} (MU) × 1.05785 = {bu:.0f} (BU)"
    else:
        bu = mu
        wheeling_rate = 2.76
        bu_calc = f"Calculation : BU = {bu:.0f} (BU)"

    if su > bu:
        st.error("Solar Units (BU) cannot exceed Billed Units (BU).")
        st.stop()

    # ===============================
    # STEP 1 : UNIT CONVERSION
    # ===============================
    st.markdown('<div class="section">Step 1 : Unit Conversion</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span>{bu:.0f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{bu_calc}</div>', unsafe_allow_html=True)

    # ===============================
    # STEP 2 : ENERGY CHARGES
    # ===============================
    st.markdown('<div class="section">Step 2 : Energy Charges</div>', unsafe_allow_html=True)

    s1_units = min(bu, 100)
    s2_units = min(max(bu - 100, 0), 200)
    s3_units = min(max(bu - 300, 0), 200)
    s4_units = max(bu - 500, 0)

    s1 = s1_units * 2.00
    s2 = s2_units * 5.20
    s3 = s3_units * 10.79
    s4 = s4_units * 11.79

    st.markdown(f'<div class="row"><span>0 – 100 Units (BU) @ ₹2.00</span><span>₹{s1:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {s1_units:.0f} × 2.00 = ₹{s1:.2f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>101 – 300 Units (BU) @ ₹5.20</span><span>₹{s2:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {s2_units:.0f} × 5.20 = ₹{s2:.2f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>301 – 500 Units (BU) @ ₹10.79</span><span>₹{s3:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {s3_units:.0f} × 10.79 = ₹{s3:.2f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Above 500 Units (BU) @ ₹11.79</span><span>₹{s4:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {s4_units:.0f} × 11.79 = ₹{s4:.2f}</div>', unsafe_allow_html=True)

    total_energy = s1 + s2 + s3 + s4

    st.markdown(f'<div class="row"><strong>Total Energy Charges</strong><strong>₹{total_energy:.2f}</strong></div>', unsafe_allow_html=True)

    # ===============================
    # STEP 3 : OTHER CHARGES
    # ===============================
    st.markdown('<div class="section">Step 3 : Other Charges</div>', unsafe_allow_html=True)

    wheeling = mu * wheeling_rate
    st.markdown(f'<div class="row"><span>Wheeling Charges (MU) @ ₹{wheeling_rate}</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {mu} (MU) × {wheeling_rate} = ₹{wheeling:.2f}</div>', unsafe_allow_html=True)

    # -------- FIXED CHARGES --------
    base_fixed = 160

    if load_kw > 10:
        load_above = load_kw - 10
        blocks = math.ceil(load_above / 10)
        additional = blocks * 250
    else:
        load_above = 0
        additional = 0

    total_fixed = base_fixed + additional

    st.markdown(f'<div class="row"><span>Fixed Charges (Base)</span><span>₹{base_fixed}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : Base Fixed Charge (3-Phase Residential) = ₹{base_fixed}</div>', unsafe_allow_html=True)

    if additional > 0:
        st.markdown(f'<div class="row"><span>Additional Fixed Charges (Load Based)</span><span>₹{additional}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc">Calculation : ({load_kw} − 10 = {load_above}) ÷ 10 → {blocks} × 250 = ₹{additional}</div>', unsafe_allow_html=True)

    solar_rebate = su * 0.50
    st.markdown(f'<div class="row green"><span>Solar Rebate (BU)</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {su} (BU) × 0.50 = ₹{solar_rebate:.2f}</div>', unsafe_allow_html=True)

    duty_base = total_energy + wheeling + total_fixed - solar_rebate
    duty = duty_base * 0.16

    st.markdown(f'<div class="row"><span>Electricity Duty (16%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : ({duty_base:.2f}) × 16% = ₹{duty:.2f}</div>', unsafe_allow_html=True)

    tose = bu * 0.3594
    st.markdown(f'<div class="row"><span>TOSE (BU)</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {bu:.0f} (BU) × 0.3594 = ₹{tose:.2f}</div>', unsafe_allow_html=True)

    total = total_energy + wheeling + total_fixed + duty + tose - solar_rebate

    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total):,}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
