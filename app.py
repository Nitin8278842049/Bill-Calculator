import streamlit as st
import math
import base64

# --- Page Configuration ---
st.set_page_config(page_title="Tata Power Mumbai | Bill Pro", layout="centered", page_icon="⚡")

# --- Custom CSS for Professional Look ---
st.markdown("""
<style>
    .reportview-container { background: #f8fafc; }
    .main-title { font-size: 28px; font-weight: 800; color: #1e3a8a; text-align: center; margin-bottom: 0px; }
    .sub-title { font-size: 14px; color: #64748b; text-align: center; margin-bottom: 30px; }
    .calc-card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .math-text { font-family: 'Courier New', monospace; font-size: 13px; color: #0369a1; background: #f0f9ff; padding: 10px; border-radius: 6px; border-left: 4px solid #0ea5e9; margin: 5px 0; }
    .total-box { background: #1e293b; color: white; padding: 25px; border-radius: 12px; text-align: center; margin-top: 20px; border-bottom: 6px solid #38bdf8; }
    .final-val { font-size: 36px; font-weight: 800; color: #38bdf8; }
</style>
""", unsafe_allow_html=True)

# ---------------- TARIFF DATA ---------------- #
TARIFF_DATA = {
    "FY 2024-2025": {"slabs": [2.18, 5.36, 11.62, 12.56], "fixed": [90, 135, 135, 160], "wheel_aeml": 2.60, "wheel_direct": 3.15, "solar_rebate": 0.00},
    "FY 2025-2026": {"slabs": [2.00, 5.20, 10.79, 11.79], "fixed": [90, 135, 135, 160], "wheel_aeml": 2.93, "wheel_direct": 2.76, "solar_rebate": 0.50},
    "FY 2026-2027": {"slabs": [1.90, 4.70, 9.24, 10.24], "fixed": [90, 135, 135, 160], "wheel_aeml": 2.28, "wheel_direct": 2.40, "solar_rebate": 0.55},
    "FY 2027-2028": {"slabs": [1.90, 4.53, 9.04, 10.04], "fixed": [90, 135, 135, 160], "wheel_aeml": 2.23, "wheel_direct": 2.33, "solar_rebate": 0.60}
}

# ---------------- HEADER ---------------- #
st.markdown('<div class="main-title">TATA POWER BILL ESTIMATOR</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Residential Mumbai Region - Multi-Year Tariff Support</div>', unsafe_allow_html=True)

# ---------------- INPUT SECTION ---------------- #
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        sel_year = st.selectbox("Financial Year", [2024, 2025, 2026, 2027, 2028], index=2)
        network = st.selectbox("Network Type", ["Welcome (AEML)", "Direct (Tata Power)"])
        mu_in = st.number_input("Metered Units (MU)", min_value=0, value=250)
    with col2:
        all_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        sel_month = st.selectbox("Billing Month", all_months, index=3)
        phase = st.selectbox("Supply Phase", ["1 Phase", "3 Phase"])
        load_kw = st.number_input("Sanctioned Load (kW)", min_value=1.0, value=1.0)

    su_in = st.number_input("Solar Units (Consumed 09:00 - 17:00)", min_value=0, value=0)

# ---------------- CALCULATION LOGIC ---------------- #
m_idx = all_months.index(sel_month) + 1
fy_start = sel_year - 1 if m_idx <= 3 else sel_year
fy_str = f"FY {fy_start}-{fy_start+1}"
rates = TARIFF_DATA.get(fy_str, TARIFF_DATA["FY 2024-2025"])

# 1. Billed Units (BU)
is_welcome = "AEML" in network
bu = math.ceil(mu_in / 0.9464) if is_welcome else int(mu_in)
loss_math = f"{mu_in} / 0.9464 (5.36% Loss)" if is_welcome else f"{mu_in} (No Loss)"

# 2. Energy Slabs
s = rates["slabs"]
v1, v2, v3, v4 = min(bu, 100), min(max(bu-100, 0), 200), min(max(bu-300, 0), 200), max(bu-500, 0)
c1, c2, c3, c4 = v1*s[0], v2*s[1], v3*s[2], v4*s[3]
e_total = c1 + c2 + c3 + c4

# 3. Fixed Charges
fixed_base = rates["fixed"][0] if bu <= 100 else rates["fixed"][1] if bu <= 500 else rates["fixed"][3]
if phase == "3 Phase": fixed_base = 160
add_load = (math.ceil(max(load_kw - 10, 0) / 10) * 250) if phase == "3 Phase" else 0
fixed_total = fixed_base + add_load

# 4. Other Taxes
w_rate = rates["wheel_aeml"] if is_welcome else rates["wheel_direct"]
wheeling = mu_in * w_rate
tose = bu * 0.3594
solar_rebate = su_in * rates["solar_rebate"]
duty = max((e_total + fixed_total + wheeling - solar_rebate), 0) * 0.16

final_amt = e_total + fixed_total + wheeling + tose + duty - solar_rebate

# ---------------- DETAILED DISPLAY ---------------- #
st.markdown("---")
st.subheader("📝 Detailed Calculation Breakdown")



with st.expander("⚡ Step 1: Energy Charge Calculation", expanded=True):
    st.write(f"**Billed Units Calculation:** `{loss_math} = {bu} Units`")
    st.markdown(f"""
    <div class="math-text">
    001 - 100 Units: {v1} U x ₹{s[0]:.2f} = ₹{c1:,.2f}<br>
    101 - 300 Units: {v2} U x ₹{s[1]:.2f} = ₹{c2:,.2f}<br>
    301 - 500 Units: {v3} U x ₹{s[2]:.2f} = ₹{c3:,.2f}<br>
    501 - Above:    {v4} U x ₹{s[3]:.2f} = ₹{c4:,.2f}<br>
    <strong>Total Energy Charge: ₹{e_total:,.2f}</strong>
    </div>
    """, unsafe_allow_html=True)

with st.expander("🏗️ Step 2: Fixed & Wheeling Charges"):
    st.markdown(f"""
    <div class="math-text">
    Fixed Charge: ₹{fixed_base} (Base) + ₹{add_load} (Load Adj) = ₹{fixed_total:,.2f}<br>
    Wheeling Charge: {mu_in} MU x ₹{w_rate:.2f} = ₹{wheeling:,.2f}
    </div>
    """, unsafe_allow_html=True)

with st.expander("🏛️ Step 3: Government Taxes & Solar Rebate"):
    st.markdown(f"""
    <div class="math-text">
    TOSE (Tax on Sale): {bu} BU x ₹0.3594 = ₹{tose:,.2f}<br>
    Electricity Duty (16%): 16% x (EC + Fixed + Wheel - Solar) = ₹{duty:,.2f}<br>
    Solar Rebate: {su_in} U x ₹{rates['solar_rebate']:.2f} = -₹{solar_rebate:,.2f}
    </div>
    """, unsafe_allow_html=True)

# ---------------- FINAL SUMMARY ---------------- #
st.markdown(f"""
<div class="total-box">
    <div style="font-size: 14px; opacity: 0.8; letter-spacing: 1px;">ESTIMATED TOTAL PAYABLE</div>
    <div class="final-val">₹{round(final_amt):,}</div>
    <div style="font-size: 11px; margin-top: 10px; color: #94a3b8;">
        Applied Tariff: {fy_str} | Month: {sel_month} {sel_year}<br>
        <i>Excludes PPCA and RAC charges if applicable.</i>
    </div>
</div>
""", unsafe_allow_html=True)
