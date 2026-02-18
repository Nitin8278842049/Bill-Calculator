import streamlit as st
import base64

st.set_page_config(page_title="Tata Power Commercial Bill Calculator", layout="centered")

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
.section { background: #fff3e0; padding: 8px; border-radius: 4px; font-weight: 700; color: #e65100; margin-top: 10px; border: 1px solid #ffe0b2; }
.row { display: flex; justify-content: space-between; padding: 8px; font-size: 14px; border: 1px solid #e6e6e6; margin-top: 4px; }
.calc { font-size: 12px; color: #666; margin-left: 6px; margin-bottom: 6px; }
.total { font-size: 22px; font-weight: 800; text-align: right; padding-top: 10px; color: #d32f2f; }
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
<div class="title">TATA POWER COMMERCIAL CALCULATOR</div>
<div class="subtitle">LT-II (Non-Residential) Tariff Structure</div>
""", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox("Network Type", ["Direct (Tata Power Network)", "Welcome (AEML Network)"])
mu_text = st.text_input("Metered Units (MU)", placeholder="Enter Total Units Consumed")
load_text = st.text_input("Sanctioned Load (kW)", placeholder="Enter Sanctioned Load")

calculate = st.button("Calculate Commercial Bill")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATIONS ---------------- #
if calculate:
    try:
        mu = float(mu_text)
        load_kw = float(load_text)
    except:
        st.error("Please enter valid numeric values.")
        st.stop()

    is_welcome = "Welcome" in network
    
    # Unit Conversion for Welcome Users
    if is_welcome:
        bu = mu * 1.05785
        wheeling_rate = 2.93
        bu_calc = f"Calculation : BU = {mu} × 1.05785 = {round(bu)} BU"
    else:
        bu = mu
        wheeling_rate = 2.76
        bu_calc = f"Calculation : BU = {round(bu)} BU"

    # Commercial (LT-II) Energy Slabs (Approximate based on latest tariff)
    # 0-500 Units and Above 500 Units
    s1_units = min(bu, 500)
    s2_units = max(bu - 500, 0)

    r1, r2 = 7.63, 9.42  # Standard Commercial LT-II Rates

    s1 = s1_units * r1
    s2 = s2_units * r2
    total_energy = s1 + s2

    wheeling = mu * wheeling_rate
    
    # Fixed Charges for Commercial (Calculated per kW per month)
    fixed_rate_per_kw = 470.00 
    fixed = load_kw * fixed_rate_per_kw

    # Commercial Electricity Duty (21%) and TOSE (0.1916)
    duty_base = total_energy + wheeling + fixed
    duty = duty_base * 0.21
    tose = bu * 0.1916

    total = total_energy + wheeling + fixed + duty + tose

    # ---------------- RESULTS ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 1 : Unit Conversion</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{round(bu)}</b></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{bu_calc}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 2 : Energy Charges (Commercial)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>0 – 500 Units (@ ₹{r1})</span><span>₹{s1:.2f}</span></div>', unsafe_allow_html=True)
    if s2_units > 0:
        st.markdown(f'<div class="row"><span>Above 500 Units (@ ₹{r2})</span><span>₹{s2:.2f}</span></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="row"><strong>Total Energy Charges</strong><strong>₹{total_energy:.2f}</strong></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 3 : Fixed & Statutory Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Fixed Charges (@ ₹{fixed_rate_per_kw}/kW)</span><span>₹{fixed:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {load_kw} kW × {fixed_rate_per_kw}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Wheeling Charges</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="row"><span>Electricity Duty (21%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="row"><span>TOSE (@ ₹0.1916)</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Commercial Bill : ₹{round(total):,}</div>', unsafe_allow_html=True)
    st.caption("Note: This is an estimate. Actual bills include FAC and Tax on Sale adjustments.")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
