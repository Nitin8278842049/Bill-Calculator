import streamlit as st
import base64

st.set_page_config(page_title="Tata Power Unified Bill Calculator", layout="centered")

# --- CSS Styling ---
st.markdown(f"""
<style>
.main-container {{ border: 2px solid #005aa2; padding: 25px; border-radius: 10px; background-color: white; font-family: sans-serif; }}
.title {{ text-align: center; color: #005aa2; font-size: 26px; font-weight: 800; }}
.card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; margin-top: 15px; }}
.section-header {{ background: #e7f1ff; padding: 10px; border-radius: 5px; font-weight: 700; color: #0c63e4; margin-top: 15px; }}
.row {{ display: flex; justify-content: space-between; padding: 8px 12px; border-bottom: 1px solid #eee; }}
.calc-details {{ font-size: 12px; color: #6c757d; font-style: italic; padding-left: 15px; }}
.total-box {{ font-size: 26px; font-weight: 800; text-align: right; color: #dc3545; border-top: 3px solid #005aa2; padding-top: 15px; }}
div.stButton > button {{ background-color: #005aa2; color: white; width: 100%; font-weight: 700; height: 50px; }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<div class="title">TATA POWER BILL CALCULATOR</div>', unsafe_allow_html=True)

# --- Input Section ---
st.markdown('<div class="card">', unsafe_allow_html=True)
category = st.selectbox("Category", ["Residential (LTI-B)", "Commercial (LT-II)"])
network = st.selectbox("Network Type", ["Welcome (AEML Network)", "Direct (Tata Power Network)"])
mu = st.number_input("Metered Units (MU)", min_value=0.0, value=242.0)
load_kw = st.number_input("Sanctioned Load (kW)", min_value=0.0, value=0.99)
su = st.number_input("Solar Generation Units (if any)", min_value=0.0, value=0.0)
calculate = st.button("Generate Detailed Bill")
st.markdown('</div>', unsafe_allow_html=True)

if calculate:
    is_resi = "Residential" in category
    is_welcome = "Welcome" in network
    
    # 1. Billed Units (BU)
    # AEML loss factor: 5.36% for Residential LT
    bu = mu * 1.05785 if (is_resi and is_welcome) else mu
    wheeling_rate = 2.93 if is_welcome else 2.76
    
    # 2. Energy Slabs
    if is_resi:
        s1, s2, s3, s4 = min(bu, 100), min(max(bu-100,0), 200), min(max(bu-300,0), 200), max(bu-500,0)
        energy_charges = (s1 * 2.00) + (s2 * 5.20) + (s3 * 10.79) + (s4 * 11.79)
        
        # Base Fixed Charge based on BU slab
        if bu <= 100: base_fixed = 90.0
        elif bu <= 500: base_fixed = 135.0
        else: base_fixed = 160.0
        
        # Additional Load Charge for 3-Phase > 10kW
        add_fixed = 0
        if load_kw > 10:
            add_fixed = (int((load_kw - 10.01) / 10) + 1) * 250
        fixed_total = base_fixed + add_fixed
        duty_pct, tose_rate = 0.16, 0.3594
    else:
        # Commercial LT-II
        s1, s2 = min(bu, 500), max(bu-500, 0)
        energy_charges = (s1 * 7.63) + (s2 * 9.42)
        fixed_total = load_kw * 470.0 
        duty_pct, tose_rate = 0.21, 0.1916

    # 3. Statutory & Taxes
    wheeling = mu * wheeling_rate
    tose = bu * tose_rate
    solar_rebate = su * 0.50
    duty_base = energy_charges + fixed_total + wheeling - solar_rebate
    duty = duty_base * duty_pct
    final_amount = duty_base + duty + tose

    # --- Result Display ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Consumption Detail</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span>{bu:.2f}</span></div>', unsafe_allow_html=True)
    if is_welcome and is_resi: st.markdown(f'<div class="calc-details">Calculation: {mu} MU * 1.05785 (Wheeling Loss)</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Charge Breakdown</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Energy Charges</span><span>₹{energy_charges:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Fixed Charges</span><span>₹{fixed_total:.2f}</span></div>', unsafe_allow_html=True)
    if add_fixed > 0: st.markdown(f'<div class="calc-details">Base: ₹{base_fixed} + Load Addl (>10kW): ₹{add_fixed}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Wheeling Charges</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">Statutory Taxes</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Electricity Duty ({int(duty_pct*100)}%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Tax on Sale (TOSE)</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="total-box">Net Bill Amount: ₹{round(final_amount + 0.35):,}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
