import streamlit as st
import base64

st.set_page_config(page_title="Tata Power Bill Calculator", layout="centered")

# ---------- LOAD LOGO ----------
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

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
.calc { font-size: 12px; color: #666; margin-left: 6px; margin-bottom: 6px; }
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
<div class="subtitle">Official 2026 Residential Tariff Verification</div>
""", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox("Network Type", ["Direct (Tata Power Network)", "Welcome (AEML Network)"])
mu_text = st.text_input("Metered Units (MU)", placeholder="e.g. 4565")
su_text = st.text_input("Solar Units (BU)", placeholder="e.g. 1573")
load_text = st.text_input("Sanctioned Load (kW)", placeholder="e.g. 40.00")

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

    is_welcome = "Welcome" in network

    if is_welcome:
        bu = mu * 1.05785
        wheeling_rate = 2.93
        bu_calc = f"Calculation : BU = {mu} × 1.05785 = {round(bu)} BU"
    else:
        bu = mu
        wheeling_rate = 2.76
        bu_calc = f"Calculation : BU = {round(bu)} BU"

    # -------- ENERGY SLABS --------
    s1_u = min(bu, 100)
    s2_u = min(max(bu - 100, 0), 200)
    s3_u = min(max(bu - 300, 0), 200)
    s4_u = max(bu - 500, 0)

    # Tariff Rates [cite: 109]
    r1, r2, r3, r4 = 2.00, 5.20, 10.79, 11.79
    s1, s2, s3, s4 = s1_u * r1, s2_u * r2, s3_u * r3, s4_u * r4
    total_energy = s1 + s2 + s3 + s4

    # -------- PPCA SLABS  --------
    p1 = s1_u * 0.05
    p2 = s2_u * 0.10
    p3 = s3_u * 0.20
    p4 = s4_u * 0.25
    total_ppca = p1 + p2 + p3 + p4

    # -------- OTHER CHARGES --------
    wheeling = mu * wheeling_rate
    solar_rebate = su * 0.50 # 
    
    # Fixed Charges based on Residential 3 Phase logic [cite: 109, 113]
    fixed_base = 160.00 
    additional_fixed = (max(0, (load_kw - 10)) / 10) * 250 if load_kw > 10 else 0
    total_fixed = fixed_base + additional_fixed

    # -------- TAXES & DUTY  --------
    # Duty is 16% on (Energy + PPCA + Wheeling + Fixed - Solar Rebate)
    duty_base = max(total_energy + total_ppca + wheeling + total_fixed - solar_rebate, 0)
    duty = duty_base * 0.16
    
    tose = bu * 0.3594 # Tax on Sale of Electricity [cite: 109]

    total_current_bill = total_energy + total_ppca + wheeling + total_fixed + duty + tose - solar_rebate

    # ---------------- RESULTS ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 1 : Unit Conversion</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{round(bu)}</b></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{bu_calc}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 2 : Energy & PPCA Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Total Energy Charges (Slab-wise)</span><span>₹{total_energy:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>PPCA Charges (Slab-wise)</span><span>₹{total_ppca:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">PPCA Cal: (100×.05)+(200×.10)+(200×.20)+({round(s4_u)}×.25)</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 3 : Fixed & Wheeling Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Wheeling Charges (@ ₹{wheeling_rate})</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Total Fixed Charges</span><span>₹{total_fixed:.2f}</span></div>', unsafe_allow_html=True)
    if load_kw > 10:
        st.markdown(f'<div class="calc">Incl. Addl. Fixed: ₹{additional_fixed:.2f} for {load_kw}kW load</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 4 : Rebates & Taxes</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row green"><span>Solar Rebate (@ ₹0.50)</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Electricity Duty (16%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">16% of (Energy+PPCA+Wheeling+Fixed-Solar Rebate)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>TOSE (@ ₹0.3594)</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Current Bill Amount : ₹{round(total_current_bill):,}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
