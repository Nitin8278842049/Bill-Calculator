import streamlit as st
import math
import base64
import os

# --- Page Configuration ---
st.set_page_config(page_title="Tata Power | Bill Estimator Pro", layout="centered", page_icon="⚡")

# --- Helper Function for Logo ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except: 
        return None

# Use logo.png (ensure this file is in your GitHub repo/folder)
logo_path = "logo.png" 
logo_base64 = get_base64_of_bin_file(logo_path)

# ---------------- TARIFF DICTIONARY (MERC APPROVED) ---------------- #
TARIFF_DATA = {
    "FY 2024-2025": {"slabs": [2.18, 5.36, 11.62, 12.56], "fixed": [90, 135, 135, 160], "wheel_aeml": 2.60, "wheel_direct": 3.15, "solar_rebate": 0.00},
    "FY 2025-2026": {"slabs": [2.00, 5.20, 10.79, 11.79], "fixed": [90, 135, 135, 160], "wheel_aeml": 2.93, "wheel_direct": 2.76, "solar_rebate": 0.50},
    "FY 2026-2027": {"slabs": [1.90, 4.70, 9.24, 10.24], "fixed": [90, 135, 135, 160], "wheel_aeml": 2.28, "wheel_direct": 2.40, "solar_rebate": 0.55},
    "FY 2027-2028": {"slabs": [1.90, 4.53, 9.04, 10.04], "fixed": [90, 135, 135, 160], "wheel_aeml": 2.23, "wheel_direct": 2.33, "solar_rebate": 0.60}
}

# ---------------- STYLING ---------------- #
st.markdown(f"""
<style>
    .stApp {{ background-color: #fcfcfd; }}
    .title-text {{ text-align: center; font-size: 22px; font-weight: 800; color: #1e3a8a; margin-bottom: 20px; text-transform: uppercase; }}
    .label-main {{ color: #475569; font-size: 13px; font-weight: 700; text-transform: uppercase; }}
    .label-math {{ color: #0369a1; font-size: 11px; font-family: monospace; background: #f0f9ff; padding: 2px 8px; border-radius: 4px; display: inline-block; margin-top: 4px; }}
    .value-main {{ color: #0f172a; font-size: 16px; font-weight: 700; text-align: right; }}
    .subtotal-row {{ background: #f8fafc; padding: 10px; border-radius: 6px; margin-top: 10px; display: flex; justify-content: space-between; border: 1px dashed #cbd5e1; font-weight: bold; }}
    .compact-final {{ background: #1e293b; padding: 20px; border-radius: 12px; margin-top: 20px; color: white; border-left: 6px solid #38bdf8; }}
    .final-flex {{ display: flex; justify-content: space-between; align-items: center; }}
    .final-amt {{ font-size: 32px; font-weight: 800; color: #38bdf8; }}
    .disclaimer {{ font-size: 11px; color: #94a3b8; margin-top: 12px; font-style: italic; border-top: 1px solid #334155; padding-top: 8px; line-height: 1.4; }}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
if logo_base64:
    st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_base64}" width="180"></div>', unsafe_allow_html=True)
st.markdown('<div class="title-text">Tata Power Bill Estimator - Mumbai</div>', unsafe_allow_html=True)

# ---------------- INPUT FORM ---------------- #
st.markdown("##### 📅 1. Period & Connection")
col_y, col_m = st.columns(2)
with col_y:
    sel_year = st.selectbox("Billing Year", [2024, 2025, 2026, 2027, 2028], index=2)
with col_m:
    all_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    available_months = all_months[3:] if sel_year == 2025 else all_months
    sel_month = st.selectbox("Billing Month", available_months)

with st.form("main_form"):
    st.markdown("##### 📝 2. Entry Details")
    c1, c2 = st.columns(2)
    with c1:
        network = st.selectbox("Network Provider", ["Welcome (AEML Network)", "Direct (Tata Power Network)"])
        mu_in = st.number_input("Metered Units (MU)", value=242, min_value=0)
    with c2:
        phase = st.selectbox("Type of Supply", ["1 Phase", "3 Phase"])
        load_kw = st.number_input("Sanctioned Load (kW)", value=1.0, min_value=0.1)
    
    su_in = st.number_input("Solar Units Consumed (09:00-17:00)", value=0, min_value=0)
    submit = st.form_submit_button("CALCULATE NOW", use_container_width=True)

# ---------------- ROW RENDER FUNCTION ---------------- #
def render_clickable_item(key, label, math_str, val, info_text, is_unit=False, is_solar=False):
    # Unique key for session state
    state_key = f"info_{key}"
    
    col_a, col_b, col_c = st.columns([0.65, 0.25, 0.1])
    color = "#166534" if is_solar else "#475569"
    math_bg = "#dcfce7" if is_solar else "#f0f9ff"
    
    with col_a:
        st.markdown(f'<span class="label-main" style="color:{color}">{label}</span><br><span class="label-math" style="background:{math_bg}">{math_str}</span>', unsafe_allow_html=True)
    with col_b:
        pfx = "" if is_unit else "₹"
        sign = "-" if is_solar else ""
        st.markdown(f'<div class="value-main" style="color:{color}">{sign}{pfx}{val:,.2f}{" Units" if is_unit else ""}</div>', unsafe_allow_html=True)
    with col_c:
        if st.button("ℹ️", key=f"btn_{key}"):
            st.session_state[state_key] = not st.session_state.get(state_key, False)
    
    if st.session_state.get(state_key, False):
        st.info(info_text)

# ---------------- LOGIC & CALCULATION ---------------- #
if submit or st.session_state.get('calculated', False):
    st.session_state['calculated'] = True
    
    # Logic: FY Determination
    m_idx = all_months.index(sel_month) + 1
    fy_start = sel_year - 1 if m_idx <= 3 else sel_year
    fy_str = f"FY {fy_start}-{fy_start+1}"
    rates = TARIFF_DATA.get(fy_str, TARIFF_DATA["FY 2024-2025"])
    
    # Logic: Billed Units
    is_welcome = "Welcome" in network
    bu = math.ceil(mu_in / 0.9464) if is_welcome else int(mu_in)
    
    # Logic: Slabs
    s = rates["slabs"]
    s1, s2, s3, s4 = min(bu, 100), min(max(bu-100, 0), 200), min(max(bu-300, 0), 200), max(bu-500, 0)
    c1, c2, c3, c4 = s1*s[0], s2*s[1], s3*s[2], s4*s[3]
    e_total = c1+c2+c3+c4
    
    # Logic: Fixed Charges
    fixed_base = rates["fixed"][0] if bu <= 100 else rates["fixed"][1] if bu <= 500 else rates["fixed"][3]
    if phase == "3 Phase": fixed_base = 160
    add_load = (math.ceil(max(load_kw - 10, 0) / 10) * 250) if phase == "3 Phase" else 0
    fixed_grand = fixed_base + add_load
    
    # Logic: Taxes & Rebates
    w_rate = rates["wheel_aeml"] if is_welcome else rates["wheel_direct"]
    wheeling = mu_in * w_rate
    tose = bu * 0.3594
    solar_rebate = su_in * rates["solar_rebate"]
    duty = max((e_total + fixed_grand + wheeling - solar_rebate), 0) * 0.16
    
    total_bill = e_total + fixed_grand + wheeling + tose + duty - solar_rebate

    st.markdown("---")
    st.markdown("### 🔍 Detailed Calculation Breakdown")
    

    with st.expander("📊 1. Consumption Units", expanded=True):
        render_clickable_item("bu", "Billed Units (BU)", f"{mu_in} MU + 5.36% Loss" if is_welcome else f"{mu_in} MU Direct", bu, "Units used for Energy Charge and TOSE. AEML network adds 5.36% transmission loss, Tata Power- 0%.", is_unit=True)

    with st.expander("💸 2. Energy Slabs", expanded=True):
        render_clickable_item("s1", "Slab 1 (0-100)", f"{s1} U x ₹{s[0]}", c1, "Rate for the first 100 units.")
        if s2 > 0: render_clickable_item("s2", "Slab 2 (101-300)", f"{s2} U x ₹{s[1]}", c2, "Rate for units 101 to 300.")
        if s3 > 0: render_clickable_item("s3", "Slab 3 (301-500)", f"{s3} U x ₹{s[2]}", c3, "Rate for units 301 to 500.")
        if s4 > 0: render_clickable_item("s4", "Slab 4 (>500)", f"{s4} U x ₹{s[3]}", c4, "Rate for units exceeding 500.")
        st.markdown(f'<div class="subtotal-row"><span>Energy Subtotal</span><span>₹{e_total:,.2f}</span></div>', unsafe_allow_html=True)

    with st.expander("🏛️ 3. Fixed & Gov Charges", expanded=True):
        render_clickable_item("fix", "Fixed Charges", f"Base ₹{fixed_base} + Load ₹{add_load}", fixed_grand, "Fixed Monthly charge based on your load and consumption slab,along with an additional Rs.250,is payable for every 10KW above the sanctioned load.")
        render_clickable_item("wh", "Wheeling Charges", f"{mu_in} MU x ₹{w_rate}", wheeling, "Wheeling Charges are the fees for using the power network to supply electricity to you.")
        render_clickable_item("ts", "Tax on Sale (TOSE)", f"{bu} BU x ₹0.3594", tose, "Tax on Sale of Electricity means a government tax charged on the electricity you consume.")
        render_clickable_item("ed", "Electricity Duty", "16% of Net Total", duty, "16% tax applied on (Energy + Fixed + Wheeling - Solar) Electricity Duty is a State Government tax charged on the electricity consumed.")

    with st.expander("🌞 4. Green Credits", expanded=True):
        render_clickable_item("sol", "Solar Rebate", f"{su_in} U x ₹{rates['solar_rebate']}", solar_rebate, "Rebate is given for consuming solar power during 09:00-17:00.", is_solar=True)

    # Final Amount Card
    st.markdown(f"""
    <div class="compact-final">
        <div class="final-flex">
            <div>
                <div style="font-size:12px; font-weight:700; opacity:0.8; letter-spacing:1px;">TOTAL PAYABLE AMOUNT</div>
                <div style="font-size:10px; opacity:0.7;">Tariff Year: {fy_str}</div>
            </div>
            <div class="final-amt">₹{round(total_bill):,}</div>
        </div>
        <div class="disclaimer">
            PPCA (Fuel adjustment) and RAC charges are not included. Figures rounded to nearest Rupee.
        </div>
    </div>
    """, unsafe_allow_html=True)
        
