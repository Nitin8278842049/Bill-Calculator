import streamlit as st
import math
import base64

# Set page layout
st.set_page_config(page_title="Tata Power | Bill Estimator Pro", layout="centered")

# --- Helper Function for Logo ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except: return None

logo_path = r"D:\Tata Power Bill Caculator Code\download.png"
logo_base64 = get_base64_of_bin_file(logo_path)

# ---------------- TARIFF DICTIONARY (STRICTLY FROM TABLE) ---------------- #
# FY 2024-25 Solar Rebate is set to 0.00
TARIFF_DATA = {
    "FY 2024-2025": {
        "slabs": [2.18, 5.36, 11.62, 12.56], 
        "fixed": [90, 135, 135, 160], 
        "wheel_aeml": 2.60, "wheel_direct": 3.15, "solar_rebate": 0.00
    },
    "FY 2025-2026": {
        "slabs": [2.00, 5.20, 10.79, 11.79], 
        "fixed": [90, 135, 135, 160], 
        "wheel_aeml": 2.93, "wheel_direct": 2.76, "solar_rebate": 0.50
    },
    "FY 2026-2027": {
        "slabs": [1.90, 4.70, 9.24, 10.24], 
        "fixed": [90, 135, 135, 160], 
        "wheel_aeml": 2.28, "wheel_direct": 2.40, "solar_rebate": 0.55
    },
    "FY 2027-2028": {
        "slabs": [1.90, 4.53, 9.04, 10.04], 
        "fixed": [90, 135, 135, 160], 
        "wheel_aeml": 2.23, "wheel_direct": 2.33, "solar_rebate": 0.60
    }
}

# ---------------- STYLING ---------------- #
st.markdown(f"""
<style>
    .stApp {{ background-color: #fcfcfd; }}
    .title-text {{ text-align: center; font-size: 20px; font-weight: 800; color: #1e3a8a; margin-bottom: 25px; text-transform: uppercase; }}
    .label-main {{ color: #475569; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .label-math {{ color: #0369a1; font-size: 11px; font-family: monospace; background: #f0f9ff; padding: 2px 8px; border-radius: 4px; }}
    .value-main {{ color: #0f172a; font-size: 15px; font-weight: 700; text-align: right; }}
    .subtotal-row {{ background: #f8fafc; padding: 10px; border-radius: 6px; margin-top: 10px; display: flex; justify-content: space-between; border: 1px dashed #cbd5e1; }}
    .compact-final {{ background: #1e293b; padding: 15px 25px; border-radius: 10px; margin-top: 15px; color: white; border-left: 5px solid #38bdf8; }}
    .final-flex {{ display: flex; justify-content: space-between; align-items: center; }}
    .final-amt {{ font-size: 26px; font-weight: 800; color: #38bdf8; }}
    .disclaimer {{ font-size: 10px; color: #94a3b8; margin-top: 10px; font-style: italic; border-top: 1px solid #334155; padding-top: 8px; line-height: 1.4; }}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
if logo_base64:
    st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_base64}" width="150"></div>', unsafe_allow_html=True)
st.markdown('<div class="title-text">Tata Power Bill Calculator - Mumbai Region</div>', unsafe_allow_html=True)

# ---------------- PERIOD SELECTION (OUTSIDE FORM) ---------------- #
st.markdown("##### 📅 Billing Period")
col_y, col_m = st.columns(2)

with col_y:
    sel_year = st.selectbox("Billing Year", [2024, 2025, 2026, 2027, 2028], index=0)

with col_m:
    all_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    # Logic: 2025 starts from April as per your request.
    available_months = all_months[3:] if sel_year == 2025 else all_months
    sel_month = st.selectbox("Billing Month", available_months)

# ---------------- INPUT FORM ---------------- #
with st.form("main_form"):
    st.markdown("##### 📝 Entry Details")
    c1, c2 = st.columns(2)
    with c1:
        network = st.selectbox("Network Provider", ["Welcome (AEML Network)", "Direct (Tata Power Network)"])
        mu_in = st.text_input("Metered Units (MU)", value="242")
    with c2:
        phase = st.selectbox("Type of Supply", ["1 Phase", "3 Phase"])
        load_kw = st.text_input("Sanctioned Load (kW)", value="1")
    
    su_in = st.text_input("Solar Hours (09:00-17:00)", value="0")
    submit = st.form_submit_button("CALCULATE NOW", use_container_width=True)

# ---------------- ROW RENDER FUNCTION ---------------- #
def render_clickable_item(key, label, math_str, val, info_text, is_unit=False, is_solar=False):
    col_a, col_b, col_c = st.columns([0.6, 0.3, 0.1])
    color = "#166534" if is_solar else "#475569"
    math_bg = "#dcfce7" if is_solar else "#f0f9ff"
    
    with col_a:
        st.markdown(f'<span class="label-main" style="color:{color}">{label}</span><br><span class="label-math" style="background:{math_bg}">{math_str}</span>', unsafe_allow_html=True)
    with col_b:
        pfx = "" if is_unit else "₹"
        sign = "-" if is_solar else ""
        st.markdown(f'<div class="value-main" style="color:{color}">{sign}{pfx}{val:,.2f}{" Units" if is_unit else ""}</div>', unsafe_allow_html=True)
    with col_c:
        btn_key = f"{key}_{sel_year}_{sel_month}"
        if st.button("ℹ️", key=btn_key):
            st.session_state[f"show_{btn_key}"] = not st.session_state.get(f"show_{btn_key}", False)
    
    if st.session_state.get(f"show_{btn_key}", False):
        st.info(info_text)

# ---------------- LOGIC & CALCULATION ---------------- #
if submit or st.session_state.get('calculated', False):
    st.session_state['calculated'] = True
    try:
        mu, load, su = float(mu_in), float(load_kw), float(su_in)
        
        m_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        m_idx = m_list.index(sel_month) + 1
        fy_start = sel_year - 1 if m_idx <= 3 else sel_year
        fy_str = f"FY {fy_start}-{fy_start+1}"
        
        rates = TARIFF_DATA.get(fy_str, TARIFF_DATA["FY 2024-2025"])
        
        is_welcome = "Welcome" in network
        bu = math.ceil(mu / 0.9464) if is_welcome else int(mu)
        
        # Slabs
        s1, s2, s3, s4 = min(bu, 100), min(max(bu-100, 0), 200), min(max(bu-300, 0), 200), max(bu-500, 0)
        c1, c2, c3, c4 = s1*rates["slabs"][0], s2*rates["slabs"][1], s3*rates["slabs"][2], s4*rates["slabs"][3]
        e_total = c1+c2+c3+c4
        
        # Fixed Charges
        fixed_base = rates["fixed"][0] if bu <= 100 else rates["fixed"][1] if bu <= 500 else rates["fixed"][3]
        if phase == "3 Phase": fixed_base = 160
        add_load = (math.ceil(max(load - 10, 0) / 10) * 250) if phase == "3 Phase" else 0
        fixed_grand = fixed_base + add_load
        
        # Wheeling, Taxes, Rebates
        w_rate = rates["wheel_aeml"] if is_welcome else rates["wheel_direct"]
        wheeling = mu * w_rate
        tose = bu * 0.3594
        solar_rebate = su * rates["solar_rebate"]
        
        duty = max((e_total + fixed_grand + wheeling - solar_rebate), 0) * 0.16
        gov_total = fixed_grand + wheeling + tose + duty

        st.write(f"### 🔍 Detailed Bill Breakdown")
        
        with st.expander("📊 1. Consumption Units", expanded=True):
            render_clickable_item("bu_info", "Billed Units", f"{mu} + 5.36% Loss" if is_welcome else f"{mu} Direct", bu, "Network Loss adjustment (AEML-5.36%, Direct -0%).", is_unit=True)

        with st.expander("💸 2. Energy Slabs", expanded=True):
            render_clickable_item("s1", f"Slab 1 (0-100)", f"{s1} x ₹{rates['slabs'][0]}", c1, "Rate for first 100 units.")
            if s2 > 0: render_clickable_item("s2", "Slab 2 (101-300)", f"{s2} x ₹{rates['slabs'][1]}", c2, "Rate for units 101-300.")
            if s3 > 0: render_clickable_item("s3", "Slab 3 (301-500)", f"{s3} x ₹{rates['slabs'][2]}", c3, "Rate for units 301-500.")
            if s4 > 0: render_clickable_item("s4", "Slab 4 (>500)", f"{s4} x ₹{rates['slabs'][3]}", c4, "Rate for units above 500.")
            st.markdown(f'<div class="subtotal-row"><b>Total Energy Charges</b> <b>₹{e_total:,.2f}</b></div>', unsafe_allow_html=True)

        with st.expander("🏛️ 3. Fixed & Gov Charges", expanded=True):
            render_clickable_item("fix", "Fixed Charges", f"Base ₹{fixed_base} + Load ₹{add_load}", fixed_grand, "A monthly fixed fee, along with an additional ₹250, is payable for every 10 kW above the sanctioned load.")
            render_clickable_item("wheel", "Wheeling Charges", f"{mu} x ₹{w_rate}", wheeling, "Wheeling Charges are fees for using the power network to supply electricity to you..")
            render_clickable_item("tose", "Tax on Sales of Electricity", f"{bu} x ₹0.3594", tose, "Tax on Sale of Electricity means a government tax charged on the electricity you consume.")
            render_clickable_item("eduty", "Electricity Duty", "16% of Net Total", duty, "16%*(Total Energy+Fixed Charge+Wheeling-Solar)  Electricity Duty is a state government tax charged on the electricity consumed.")
            st.markdown(f'<div class="subtotal-row"><b>Total Fixed & Gov Charges</b> <b>₹{gov_total:,.2f}</b></div>', unsafe_allow_html=True)

        with st.expander("🌞 4. Solar Rebate & Credits", expanded=True):
            render_clickable_item("solar", "Green Solar Rebate", f"{su} Units x ₹{rates['solar_rebate']}", solar_rebate, f"Solar rebate is given for using supply in solar hours i.e. 09:00-17:00.", is_solar=True)

        total_bill = e_total + gov_total - solar_rebate
        st.markdown(f"""
        <div class="compact-final">
            <div class="final-flex">
                <div><div style="font-size:12px;opacity:0.8;">APPROX AMOUNT PAY</div><div style="font-size:10px;">Rates Applied: {fy_str}</div></div>
                <div class="final-amt">₹{round(total_bill):,}</div>
            </div>
            <div class="disclaimer">
                Please note that PPCA and RAC charges are excluded from this calculation and will be imposed if applicable.
            </div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e: st.error(f"Error: {e}"    s1_units = min(bu, 100)
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
