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
<div class="logo-container">
    <img src="data:image/png;base64,{logo_base64}">
</div>
<div class="title">TATA POWER BILL CALCULATOR</div>
<div class="subtitle">Mumbai Based Regional Tariff</div>
""", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

# Selection for Calculator Type
calc_type = st.radio("Select Category", ["Residential", "Commercial"], horizontal=True)

network = st.selectbox("Network Type", ["Direct (Tata Power Network)", "Welcome (AEML Network)"])
mu_text = st.text_input("Metered Units (MU)", placeholder="Enter Units")
load_text = st.text_input("Sanctioned Load (kW)", placeholder="Enter Load")

# Conditional Inputs
su_text = "0"
rmd_text = "0"
if calc_type == "Residential":
    su_text = st.text_input("Solar Units (BU)", value="0", placeholder="Enter Solar Units")
else:
    rmd_text = st.text_input("Recorded Max Demand (RMD in kW)", placeholder="Enter RMD")

calculate = st.button("Calculate Bill")
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

    # Step 1: Unit Conversion (BU)
    is_welcome = "Welcome" in network
    if is_welcome:
        bu = mu * 1.05785
        wheeling_rate = 2.93
        bu_calc = f"Calculation : BU = {mu} × 1.05785 = {round(bu)} BU"
    else:
        bu = mu
        wheeling_rate = 2.76
        bu_calc = f"Calculation : BU = {round(bu)} BU"

    # Step 2: Category Specific Logic
    if calc_type == "Residential":
        # RESIDENTIAL SLABS
        s1_units = min(bu, 100)
        s2_units = min(max(bu - 100, 0), 200)
        s3_units = min(max(bu - 300, 0), 200)
        s4_units = max(bu - 500, 0)
        r1, r2, r3, r4 = 2.00, 5.20, 10.79, 11.79
        
        s1, s2, s3, s4 = s1_units*r1, s2_units*r2, s3_units*r3, s4_units*r4
        total_energy = s1 + s2 + s3 + s4

        if bu <= 100: fixed = 90
        elif bu <= 500: fixed = 135
        else: fixed = 160
        
        additional_fixed = 250 if load_kw > 10 else 0
        penalty_charge = 0
        duty_rate = 0.16
        tose_rate = 0.3594
        sec_class = "section"

    else:
        # COMMERCIAL SLABS
        s1_units = min(bu, 500)
        s2_units = max(bu - 500, 0)
        r1, r2 = 7.63, 9.42
        
        s1, s2 = s1_units * r1, s2_units * r2
        total_energy = s1 + s2

        # BMD Logic (75% rule)
        bmd = max(rmd, load_kw * 0.75)
        demand_rate = 470.00
        fixed = bmd * demand_rate
        
        penalty_charge = (rmd - load_kw) * (demand_rate * 1.5) if rmd > load_kw else 0
        additional_fixed = 0
        duty_rate = 0.21
        tose_rate = 0.1916
        sec_class = "section-comm"

    # Step 3: Global Charges
    wheeling = mu * wheeling_rate
    solar_rebate = su * 0.50
    duty_base = max(total_energy + wheeling + fixed + additional_fixed + penalty_charge - solar_rebate, 0)
    duty = duty_base * duty_rate
    tose = bu * tose_rate
    total_bill = duty_base + duty + tose

    # ---------------- RESULTS ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Step 1: Units
    st.markdown(f'<div class="{sec_class}">Step 1 : Unit & Demand Analysis</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{round(bu)}</b></span></div>', unsafe_allow_html=True)
    if calc_type == "Commercial":
        st.markdown(f'<div class="row"><span>Billing Demand (BMD)</span><span><b>{bmd:.2f} kW</b></span></div>', unsafe_allow_html=True)

    # Step 2: Energy
    st.markdown(f'<div class="{sec_class}">Step 2 : Energy Charges</div>', unsafe_allow_html=True)
    if calc_type == "Residential":
        st.markdown(f'<div class="row"><span>0-100 Units (@ ₹2.00)</span><span>₹{s1:.2f}</span></div>', unsafe_allow_html=True)
        if s2_units > 0: st.markdown(f'<div class="row"><span>101-300 Units (@ ₹5.20)</span><span>₹{s2:.2f}</span></div>', unsafe_allow_html=True)
        if s3_units > 0: st.markdown(f'<div class="row"><span>301-500 Units (@ ₹10.79)</span><span>₹{s3:.2f}</span></div>', unsafe_allow_html=True)
        if s4_units > 0: st.markdown(f'<div class="row"><span>Above 500 Units (@ ₹11.79)</span><span>₹{s4:.2f}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="row"><span>0-500 Units (@ ₹7.63)</span><span>₹{s1:.2f}</span></div>', unsafe_allow_html=True)
        if s2_units > 0: st.markdown(f'<div class="row"><span>Above 500 Units (@ ₹9.42)</span><span>₹{s2:.2f}</span></div>', unsafe_allow_html=True)

    # Step 3: Others
    st.markdown(f'<div class="{sec_class}">Step 3 : Other Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Wheeling (@ ₹{wheeling_rate})</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>{"Demand" if calc_type == "Commercial" else "Fixed"} Charges</span><span>₹{fixed:.2f}</span></div>', unsafe_allow_html=True)
    
    if penalty_charge > 0:
        st.markdown(f'<div class="row penalty"><span>Demand Penalty</span><span>₹{penalty_charge:.2f}</span></div>', unsafe_allow_html=True)
    if additional_fixed > 0:
        st.markdown(f'<div class="row"><span>Addl. Fixed Charges</span><span>₹250.00</span></div>', unsafe_allow_html=True)
    if su > 0:
        st.markdown(f'<div class="row green"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Electricity Duty ({int(duty_rate*100)}%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>TOSE</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total_bill):,}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
