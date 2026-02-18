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
.section-comm { background: #fff3e0; padding: 8px; border-radius: 4px; font-weight: 700; color: #e65100; margin-top: 10px; border: 1px solid #ffe0b2; }
.row { display: flex; justify-content: space-between; padding: 8px; font-size: 14px; border: 1px solid #e6e6e6; margin-top: 4px; }
.calc { font-size: 12px; color: #666; margin-left: 6px; margin-bottom: 6px; }
.total { font-size: 22px; font-weight: 800; text-align: right; padding-top: 10px; }
.green { color: #1a7f37; font-weight: 600; }
.penalty { color: #d32f2f; font-weight: 700; background-color: #ffebee; }
div.stButton > button { background-color: #005aa2; color: white; font-size: 16px; font-weight: 700; height: 45px; width: 100%; }
label { font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown(f"""
<div class="logo-container"><img src="data:image/png;base64,{logo_base64}"></div>
<div class="title">TATA POWER BILL CALCULATOR</div>
<div class="subtitle">Detailed Calculation Breakdown</div>
""", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)
calc_type = st.radio("Select Category", ["Residential", "Commercial"], horizontal=True)
network = st.selectbox("Network Type", ["Direct (Tata Power Network)", "Welcome (AEML Network)"])
mu_text = st.text_input("Metered Units (MU)", value="0")
load_text = st.text_input("Sanctioned Load (kW)", value="0")

# Conditional Inputs
su_text = "0"
rmd_text = "0"
if calc_type == "Residential":
    su_text = st.text_input("Solar Units (BU)", value="0")
else:
    rmd_text = st.text_input("Recorded Max Demand (RMD in kW)", value="0")

calculate = st.button("Calculate Detailed Bill")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATIONS ---------------- #
if calculate:
    try:
        mu = float(mu_text)
        load_kw = float(load_text)
        su = float(su_text)
        rmd = float(rmd_text)
    except:
        st.error("Please enter valid numeric values.")
        st.stop()

    is_welcome = "Welcome" in network
    if is_welcome:
        bu = mu * 1.05785
        wheeling_rate = 2.93
        bu_calc_text = f"BU = {mu} × 1.05785 = {round(bu)} Units"
    else:
        bu = mu
        wheeling_rate = 2.76
        bu_calc_text = f"BU = {round(bu)} Units"

    # Split Logic
    if calc_type == "Residential":
        s1_u, s2_u, s3_u, s4_u = min(bu, 100), min(max(bu-100, 0), 200), min(max(bu-300, 0), 200), max(bu-500, 0)
        r1, r2, r3, r4 = 2.00, 5.20, 10.79, 11.79
        total_energy = (s1_u*r1) + (s2_u*r2) + (s3_u*r3) + (s4_u*r4)
        
        fixed = 90 if bu <= 100 else 135 if bu <= 500 else 160
        add_fixed = 250 if load_kw > 10 else 0
        penalty = 0
        duty_pct = 0.16
        tose_rate = 0.3594
        sec_class = "section"
    else:
        s1_u, s2_u = min(bu, 500), max(bu-500, 0)
        r1, r2 = 7.63, 9.42
        total_energy = (s1_u*r1) + (s2_u*r2)
        
        bmd = max(rmd, load_kw * 0.75)
        fixed = bmd * 470.00
        penalty = (rmd - load_kw) * (470.00 * 1.5) if rmd > load_kw else 0
        add_fixed = 0
        duty_pct = 0.21
        tose_rate = 0.1916
        sec_class = "section-comm"

    wheeling = mu * wheeling_rate
    solar_rebate = su * 0.50
    duty = (total_energy + wheeling + fixed + add_fixed + penalty - solar_rebate) * duty_pct
    tose = bu * tose_rate
    total_bill = total_energy + wheeling + fixed + add_fixed + penalty + duty + tose - solar_rebate

    # ---------------- RESULTS ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    st.markdown(f'<div class="{sec_class}">Step 1 : Unit Conversion</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{round(bu)}</b></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{bu_calc_text}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="{sec_class}">Step 2 : Energy Charges Breakdown</div>', unsafe_allow_html=True)
    if calc_type == "Residential":
        st.markdown(f'<div class="row"><span>0-100 Units (@ ₹2.00)</span><span>₹{s1_u*r1:.2f}</span></div>')
        st.markdown(f'<div class="calc">{s1_u} × 2.00 = ₹{s1_u*r1:.2f}</div>')
        if s2_u > 0:
            st.markdown(f'<div class="row"><span>101-300 Units (@ ₹5.20)</span><span>₹{s2_u*r2:.2f}</span></div>')
            st.markdown(f'<div class="calc">{s2_u} × 5.20 = ₹{s2_u*r2:.2f}</div>')
        # ... (S3, S4 added similarly)
    else:
        st.markdown(f'<div class="row"><span>0-500 Units (@ ₹7.63)</span><span>₹{s1_u*r1:.2f}</span></div>')
        st.markdown(f'<div class="calc">{s1_u} × 7.63 = ₹{s1_u*r1:.2f}</div>')
        if s2_u > 0:
            st.markdown(f'<div class="row"><span>Above 500 Units (@ ₹9.42)</span><span>₹{s2_u*r2:.2f}</span></div>')
            st.markdown(f'<div class="calc">{s2_u} × 9.42 = ₹{s2_u*r2:.2f}</div>')

    st.markdown(f'<div class="{sec_class}">Step 3 : Fixed & Statutory Charges</div>', unsafe_allow_html=True)
    if calc_type == "Commercial":
        st.markdown(f'<div class="row"><span>Demand Charges</span><span>₹{fixed:.2f}</span></div>')
        st.markdown(f'<div class="calc">BMD {bmd:.2f}kW × ₹470.00 = ₹{fixed:.2f}</div>')
        if penalty > 0:
            st.markdown(f'<div class="row penalty"><span>Demand Penalty</span><span>₹{penalty:.2f}</span></div>')
    else:
        st.markdown(f'<div class="row"><span>Fixed Charges</span><span>₹{fixed:.2f}</span></div>')

    st.markdown(f'<div class="row"><span>Electricity Duty ({int(duty_pct*100)}%)</span><span>₹{duty:.2f}</span></div>')
    st.markdown(f'<div class="row"><span>TOSE</span><span>₹{tose:.2f}</span></div>')
    
    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total_bill):,}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
