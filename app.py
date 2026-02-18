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
.penalty { color: #d32f2f; font-weight: 700; background-color: #ffebee; border: 1px solid #ffcdd2; }
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
<div class="subtitle">LT-II (Non-Residential) / Commercial Tariff</div>
""", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox("Network Type", ["Direct (Tata Power)", "Welcome (AEML Network)"])
mu_text = st.text_input("Metered Units (MU)", placeholder="Enter Units Consumed")
load_text = st.text_input("Sanctioned Load (kW)", placeholder="Enter Sanctioned Load")
rmd_text = st.text_input("Recorded Max Demand (RMD in kW)", placeholder="Enter Actual RMD")

calculate = st.button("Calculate Bill")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATIONS ---------------- #
if calculate:
    try:
        mu = float(mu_text)
        load_kw = float(load_text)
        rmd = float(rmd_text)
    except:
        st.error("Please enter valid numeric values for all fields.")
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

    # Step 2: BMD Calculation (75% Rule)
    # BMD is higher of RMD or 75% of Sanctioned Load
    min_billing_demand = load_kw * 0.75
    bmd = max(rmd, min_billing_demand)
    
    # Step 3: Energy Charges (Commercial LT-II Slabs)
    # Rates: 0-500: ₹7.63, >500: ₹9.42 (Example Commercial Rates)
    s1_units = min(bu, 500)
    s2_units = max(bu - 500, 0)
    r1, r2 = 7.63, 9.42
    
    s1_cost = s1_units * r1
    s2_cost = s2_units * r2
    total_energy = s1_cost + s2_cost

    # Step 4: Demand Charges & Penalty
    demand_rate = 470.00 # Typical commercial demand rate
    demand_charges = bmd * demand_rate
    
    penalty_charge = 0
    if rmd > load_kw:
        excess_demand = rmd - load_kw
        # Penalty is usually charged on the excess demand at 150% of the normal rate
        penalty_charge = excess_demand * (demand_rate * 1.5)

    # Step 5: Other Charges & Taxes
    wheeling = mu * wheeling_rate
    tose = bu * 0.1916 # Commercial TOSE rate
    
    # Duty is usually 21% for commercial
    duty_base = total_energy + wheeling + demand_charges + penalty_charge
    duty = duty_base * 0.21
    
    total_bill = duty_base + duty + tose

    # ---------------- DISPLAY RESULTS ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Unit Conversion Section
    st.markdown('<div class="section">Step 1: Unit & Demand Analysis</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{round(bu)}</b></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>75% of Sanctioned Load</span><span>{min_billing_demand:.2f} kW</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Recorded Demand (RMD)</span><span>{rmd:.2f} kW</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span><b>Billing Max Demand (BMD)</b></span><span><b>{bmd:.2f} kW</b></span></div>', unsafe_allow_html=True)
    st.markdown('<div class="calc">BMD = Higher of RMD or 75% of Sanctioned Load</div>', unsafe_allow_html=True)

    # Energy Charges Section
    st.markdown('<div class="section">Step 2: Energy Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>0 – 500 Units (@ ₹{r1})</span><span>₹{s1_cost:.2f}</span></div>', unsafe_allow_html=True)
    if s2_units > 0:
        st.markdown(f'<div class="row"><span>Above 500 Units (@ ₹{r2})</span><span>₹{s2_cost:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><strong>Total Energy Charges</strong><strong>₹{total_energy:.2f}</strong></div>', unsafe_allow_html=True)

    # Demand & Penalty Section
    st.markdown('<div class="section">Step 3: Demand & Fixed Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Demand Charges (@ ₹{demand_rate})</span><span>₹{demand_charges:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {bmd:.2f} kW × ₹{demand_rate}</div>', unsafe_allow_html=True)

    if penalty_charge > 0:
        st.markdown(f'<div class="row penalty"><span>Demand Penalty (Excess Load)</span><span>₹{penalty_charge:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc">Calculation : {rmd - load_kw:.2f} kW excess × ₹{demand_rate * 1.5}</div>', unsafe_allow_html=True)

    # Statutory Section
    st.markdown('<div class="section">Step 4: Statutory Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Wheeling Charges</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Electricity Duty (21%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>TOSE (@ ₹0.1916)</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)

    # Final Total
    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total_bill):,}</div>', unsafe_allow_html=True)
    st.caption("Disclaimer: This is an estimation based on standard LT-II Commercial tariff rules.")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
