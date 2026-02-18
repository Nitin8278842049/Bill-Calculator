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

# ---------------- CSS Styling ---------------- #
st.markdown("""
<style>
.main-container { border: 2px solid #005aa2; padding: 20px; border-radius: 8px; }
.stApp { background-color: white; }
.logo-container { text-align: center; margin-bottom: 5px; }
.logo-container img { max-width: 160px; }
.title { text-align: center; color: #005aa2; font-size: 28px; font-weight: 800; }
.subtitle { text-align: center; color: #555; font-size: 14px; margin-bottom: 15px; }
.card { background: white; padding: 18px; border-radius: 6px; border: 1px solid #dcdcdc; margin-bottom: 15px; }
.section-res { background: #eef7ff; padding: 8px; border-radius: 4px; font-weight: 700; color: #005aa2; margin-top: 10px; border: 1px solid #d0e7ff; }
.section-comm { background: #fff3e0; padding: 8px; border-radius: 4px; font-weight: 700; color: #e65100; margin-top: 10px; border: 1px solid #ffe0b2; }
.row { display: flex; justify-content: space-between; padding: 8px; font-size: 14px; border: 1px solid #e6e6e6; margin-top: 4px; }
.calc { font-size: 12px; color: #666; margin-left: 6px; margin-bottom: 6px; }
.total { font-size: 22px; font-weight: 800; text-align: right; padding-top: 10px; }
.penalty { color: #d32f2f; font-weight: 700; background-color: #ffebee; border: 1px solid #ffcdd2; }
.green { color: #1a7f37; font-weight: 600; }
div.stButton > button { background-color: #005aa2; color: white; font-size: 16px; font-weight: 700; height: 45px; width: 100%; }
label { font-weight: 800 !important; color: #333 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown(f"""
<div class="logo-container">
    <img src="data:image/png;base64,{logo_base64}">
</div>
<div class="title">TATA POWER BILL CALCULATOR</div>
<div class="subtitle">Residential (LTI-B) & Commercial (LT-II) Unified Calculator</div>
""", unsafe_allow_html=True)

# ---------------- INPUT CARD ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

# CONNECTION SELECTION
conn_type = st.radio("Step 1: Select Connection Type", ["Residential", "Commercial"], horizontal=True)

# COMMON INPUTS
network = st.selectbox("Step 2: Network Type", ["Direct (Tata Power Network)", "Welcome (AEML Network)"])
mu_text = st.text_input("Metered Units (MU)", placeholder="e.g. 500")
load_text = st.text_input("Sanctioned Load (kW)", placeholder="e.g. 5")

# CONDITIONAL INPUTS
if conn_type == "Residential":
    su_text = st.text_input("Solar Units (BU)", value="0", help="Enter solar generation units for rebate")
    rmd_text = "0"
else:
    rmd_text = st.text_input("Recorded Max Demand (RMD in kW)", placeholder="Enter RMD from bill")
    su_text = "0"

calculate = st.button("Calculate Total Bill")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATIONS ---------------- #
if calculate:
    try:
        mu = float(mu_text) if mu_text else 0.0
        su = float(su_text) if su_text else 0.0
        load_kw = float(load_text) if load_text else 0.0
        rmd = float(rmd_text) if rmd_text else 0.0
    except ValueError:
        st.error("Please enter valid numeric values for all fields.")
        st.stop()

    is_welcome = "Welcome" in network
    
    # Unit Conversion Logic
    if is_welcome:
        bu = mu * 1.05785
        wheeling_rate = 2.93
        bu_calc = f"Calculation : {mu} MU × 1.05785 = {round(bu)} BU"
    else:
        bu = mu
        wheeling_rate = 2.76
        bu_calc = f"Calculation : {round(bu)} BU"

    # Tariff Logic Branching
    if conn_type == "Residential":
        # RESIDENTIAL (LTI-B) SLABS [cite: 103, 108]
        s1_units = min(bu, 100)
        s2_units = min(max(bu - 100, 0), 200)
        s3_units = min(max(bu - 300, 0), 200)
        s4_units = max(bu - 500, 0)
        r1, r2, r3, r4 = 2.00, 5.20, 10.79, 11.79
        
        energy_charges = (s1_units * r1) + (s2_units * r2) + (s3_units * r3) + (s4_units * r4)
        
        # Fixed charges logic [cite: 103, 108]
        if bu <= 100: fixed = 90
        elif bu <= 500: fixed = 135
        else: fixed = 160
        add_fixed = 250 if load_kw > 10 else 0
        
        duty_rate = 0.16 # 16% for Residential [cite: 103]
        tose_rate = 0.3594 # [cite: 103]
        demand_penalty = 0
        bmd = 0

    else:
        # COMMERCIAL (LT-II) SLABS
        s1_units = min(bu, 500)
        s2_units = max(bu - 500, 0)
        r1, r2 = 7.63, 9.42
        energy_charges = (s1_units * r1) + (s2_units * r2)
        
        # BMD Logic (75% rule for Commercial)
        min_billing_demand = load_kw * 0.75
        bmd = max(rmd, min_billing_demand)
        
        demand_rate = 470.00
        fixed = bmd * demand_rate
        add_fixed = 0
        
        # Demand Penalty if RMD > Sanctioned Load
        demand_penalty = (rmd - load_kw) * (demand_rate * 1.5) if rmd > load_kw else 0
            
        duty_rate = 0.21 # 21% for Commercial
        tose_rate = 0.1916

    # Final Totals
    wheeling = mu * wheeling_rate
    solar_rebate = su * 0.50 [cite: 97]
    tose = bu * tose_rate
    
    # Duty is calculated on (Energy + Wheeling + Fixed + Penalty - Rebate) [cite: 97]
    duty_base = max(energy_charges + wheeling + fixed + add_fixed + demand_penalty - solar_rebate, 0)
    duty = duty_base * duty_rate

    total_bill = duty_base + duty + tose

    # ---------------- DISPLAY RESULTS ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)
    header_class = "section-res" if conn_type == "Residential" else "section-comm"
    
    st.markdown(f'<div class="{header_class}">Step 1: Usage & Demand Data</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{round(bu)}</b></span></div>', unsafe_allow_html=True)
    if conn_type == "Commercial":
        st.markdown(f'<div class="row"><span>Billing Demand (BMD)</span><span><b>{bmd:.2f} kW</b></span></div>', unsafe_allow_html=True)
        st.caption(f"BMD is higher of RMD ({rmd}kW) or 75% of Load ({min_billing_demand}kW)")

    st.markdown(f'<div class="{header_class}">Step 2: Energy Charges ({conn_type})</div>', unsafe_allow_html=True)
    if conn_type == "Residential":
        st.markdown(f'<div class="row"><span>0-100 Units</span><span>₹{s1_units*r1:.2f}</span></div>', unsafe_allow_html=True)
        if s2_units > 0: st.markdown(f'<div class="row"><span>101-300 Units</span><span>₹{s2_units*r2:.2f}</span></div>', unsafe_allow_html=True)
        if s4_units > 0: st.markdown(f'<div class="row"><span>Above 500 Units</span><span>₹{s4_units*r4:.2f}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="row"><span>0-500 Units (@ ₹{r1})</span><span>₹{s1_units*r1:.2f}</span></div>', unsafe_allow_html=True)
        if s2_units > 0: st.markdown(f'<div class="row"><span>Above 500 (@ ₹{r2})</span><span>₹{s2_units*r2:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="{header_class}">Step 3: Fixed & Statutory Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>{"Demand" if conn_type == "Commercial" else "Fixed"} Charges</span><span>₹{fixed:.2f}</span></div>', unsafe_allow_html=True)
    
    if demand_penalty > 0:
        st.markdown(f'<div class="row penalty"><span>Demand Penalty (Excess Load)</span><span>₹{demand_penalty:.2f}</span></div>', unsafe_allow_html=True)
    
    if add_fixed > 0:
        st.markdown(f'<div class="row"><span>Addl. Fixed (Load > 10kW)</span><span>₹250.00</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row green"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Electricity Duty ({int(duty_rate*100)}%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>TOSE</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total_bill):,}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
