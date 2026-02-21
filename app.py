import streamlit as st
import base64

st.set_page_config(page_title="Mumbai Bill Calculator 2026", layout="centered")

# ---------- LOAD LOGO ----------
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

logo_base64 = get_base64_of_bin_file("logo.png")

# ---------------- CSS (Updated for Red Highlights) ---------------- #
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
.calc { font-size: 12px; color: #666; margin-left: 6px; margin-bottom: 6px; }
.total { font-size: 22px; font-weight: 800; text-align: right; padding-top: 10px; }
.green { color: #1a7f37; font-weight: 600; }
/* Red Highlight for Adani Selection */
.adani-highlight { color: #d73a49; font-weight: 700; }
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
<div class="title">MUMBAI POWER BILL CALCULATOR</div>
<div class="subtitle">Adani & Tata Power | 2025-26 Tariff Cycle</div>
""", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox("Select Supply/Network Type", 
    ["Welcome (AEML Network)", "Direct (Tata Power Network)", "Adani Direct Supply"])

mu_text = st.text_input("Metered Units (MU)", placeholder="Enter Metered Units")
su_text = st.text_input("Solar Units (BU)", value="0", placeholder="Enter Solar Units")
load_text = st.text_input("Sanctioned Load (kW)", placeholder="Enter Load")

calculate = st.button("Calculate Bill")

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

    # --- TARIFF LOGIC 2025-2026 ---
    is_welcome = "Welcome" in network
    is_adani = "Adani" in network and "Direct" in network

    if is_welcome:
        bu = mu * 1.05785 # Loss adjustment
        wheeling_rate = 2.93
        r1, r2, r3, r4 = 2.00, 5.20, 10.79, 11.79
        ppca = 0.85 # Avg PPCA for Tata
        bu_calc = f"Calculation : BU = {mu} × 1.05785 = {round(bu)} BU"
    elif is_adani:
        bu = mu
        wheeling_rate = 2.93
        # Adani 2025-26 Residential Rates
        r1, r2, r3, r4 = 3.45, 6.70, 8.10, 9.05
        ppca = 1.25 # Avg PPCA for Adani
        bu_calc = f"Calculation : BU = {round(bu)} BU"
    else: # Tata Direct
        bu = mu
        wheeling_rate = 1.82 
        r1, r2, r3, r4 = 2.02, 5.35, 10.04, 11.25
        ppca = 0.85
        bu_calc = f"Calculation : BU = {round(bu)} BU"

    # --- Energy Slabs ---
    s1_units = min(bu, 100)
    s2_units = min(max(bu - 100, 0), 200)
    s3_units = min(max(bu - 300, 0), 200)
    s4_units = max(bu - 500, 0)

    s1, s2, s3, s4 = s1_units * r1, s2_units * r2, s3_units * r3, s4_units * r4
    total_energy = s1 + s2 + s3 + s4
    wheeling = mu * wheeling_rate
    solar_rebate = su * 0.50

    # --- Fixed Charges ---
    if bu <= 100: fixed = 90
    elif bu <= 500: fixed = 135
    else: fixed = 160

    # Three-phase or High Load Adjustment
    additional_fixed = 250 if load_kw > 10 else 0
    ppca_total = bu * ppca
    
    # --- Taxes ---
    # Duty is 16% on (Energy + Wheeling + Fixed + PPCA - Solar Rebate)
    duty_base = max(total_energy + wheeling + fixed + additional_fixed + ppca_total - solar_rebate, 0)
    duty = duty_base * 0.16
    tose = bu * 0.2604 # Tax on Sale of Electricity

    total_bill = duty_base + duty + tose

    # ---------------- RESULTS ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    title_color = "adani-highlight" if is_adani else ""
    st.markdown(f'<div class="section">Step 1 : Unit Conversion <span class="{title_color}">({network})</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{round(bu)}</b></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{bu_calc}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 2 : Energy Charges (Slab-wise)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>0 – 100 (@ ₹{r1})</span><span>₹{s1:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>101 – 300 (@ ₹{r2})</span><span>₹{s2:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>301 – 500 (@ ₹{r3})</span><span>₹{s3:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Above 500 (@ ₹{r4})</span><span>₹{s4:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><strong>Total Energy</strong><strong>₹{total_energy:.2f}</strong></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 3 : Fixed & Regulatory Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Wheeling Charges (@ ₹{wheeling_rate})</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Fixed Charges</span><span>₹{fixed + additional_fixed:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>PPCA (Estimated)</span><span>₹{ppca_total:.2f}</span></div>', unsafe_allow_html=True)
    
    if su > 0:
        st.markdown(f'<div class="row green"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Electricity Duty (16%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>TOSE (@ ₹0.2604)</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Payable : ₹{round(total_bill):,}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
