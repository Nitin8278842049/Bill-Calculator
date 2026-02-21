import streamlit as st
import base64

st.set_page_config(page_title="Tata Power Bill Calculator", layout="centered")

# ---------- LOAD LOGO ----------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

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
.total { font-size: 22px; font-weight: 800; text-align: right; padding-top: 10px; }
.green { color: green; font-weight: 600; }
div.stButton > button { background-color: #005aa2; color: white; font-size: 16px; font-weight: 700; height: 45px; width: 100%; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown(f"""
<div class="logo-container">
    <img src="data:image/png;base64,{logo_base64}">
</div>
<div class="title">TATA POWER BILL CALCULATOR</div>
<div class="subtitle">Residential Tariff (Mumbai)</div>
""", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox("Network Type", ["Direct (Tata Power)", "Welcome (AEML Network)"])
mu = st.number_input("Metered Units (MU)", min_value=0.0)
su = st.number_input("Solar Units", min_value=0.0)
load_kw = st.number_input("Sanctioned Load (kW)", min_value=0.0)

calculate = st.button("Calculate")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATION ---------------- #
if calculate:

    # BU Conversion
    if "Welcome" in network:
        bu = mu * 1.05785
        wheeling_rate = 2.93
    else:
        bu = mu
        wheeling_rate = 2.76

    if su > bu:
        st.error("Solar units cannot exceed billed units.")
        st.stop()

    # -------- ENERGY SLABS --------
    s1_units = min(bu, 100)
    s2_units = min(max(bu - 100, 0), 200)
    s3_units = min(max(bu - 300, 0), 200)
    s4_units = max(bu - 500, 0)

    s1 = s1_units * 2.00
    s2 = s2_units * 5.20
    s3 = s3_units * 10.79
    s4 = s4_units * 11.79

    total_energy = s1 + s2 + s3 + s4

    # -------- PPCA SLABS --------
    pp1 = s1_units * 0.05
    pp2 = s2_units * 0.10
    pp3 = s3_units * 0.20
    pp4 = s4_units * 0.25

    total_ppca = pp1 + pp2 + pp3 + pp4

    # -------- OTHER CHARGES --------
    wheeling = bu * wheeling_rate  # CORRECTED (BU not MU)
    solar_rebate = su * 0.50

    if bu <= 100:
        fixed = 90
    elif bu <= 500:
        fixed = 135
    else:
        fixed = 160

    additional_fixed = 250 if load_kw > 10 else 0

    # -------- ELECTRICITY DUTY --------
    duty_base = max(total_energy + total_ppca + wheeling + fixed + additional_fixed - solar_rebate, 0)
    duty = duty_base * 0.16

    # -------- TOSE --------
    tose = bu * 0.3594

    # -------- FINAL TOTAL --------
    total = total_energy + total_ppca + wheeling + fixed + additional_fixed + duty + tose - solar_rebate

    # ---------------- DISPLAY ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Full Calculation", "PPCA Breakdown"])

    with tab1:
        st.markdown("### Energy Charges")
        st.write(f"0–100 Units: {s1_units:.0f} × 2.00 = ₹{s1:.2f}")
        st.write(f"101–300 Units: {s2_units:.0f} × 5.20 = ₹{s2:.2f}")
        st.write(f"301–500 Units: {s3_units:.0f} × 10.79 = ₹{s3:.2f}")
        st.write(f"Above 500 Units: {s4_units:.0f} × 11.79 = ₹{s4:.2f}")
        st.write(f"Total Energy = ₹{total_energy:.2f}")

        st.markdown("### Other Charges")
        st.write(f"Wheeling: {bu:.0f} × {wheeling_rate} = ₹{wheeling:.2f}")
        st.write(f"Fixed Charges = ₹{fixed:.2f}")
        if additional_fixed:
            st.write(f"Additional Fixed (Load >10kW) = ₹{additional_fixed:.2f}")
        st.write(f"Solar Rebate = -₹{solar_rebate:.2f}")

        st.markdown("### Taxes")
        st.write(f"Electricity Duty 16% on ₹{duty_base:.2f} = ₹{duty:.2f}")
        st.write(f"TOSE: {bu:.0f} × 0.3594 = ₹{tose:.2f}")

        st.markdown("---")
        st.markdown(f"## Net Bill Amount = ₹{round(total):,}")

    with tab2:
        st.markdown("### PPCA Slab Calculation")
        st.write(f"0–100 Units: {s1_units:.0f} × 0.05 = ₹{pp1:.2f}")
        st.write(f"101–300 Units: {s2_units:.0f} × 0.10 = ₹{pp2:.2f}")
        st.write(f"301–500 Units: {s3_units:.0f} × 0.20 = ₹{pp3:.2f}")
        st.write(f"Above 500 Units: {s4_units:.0f} × 0.25 = ₹{pp4:.2f}")
        st.write(f"Total PPCA = ₹{total_ppca:.2f}")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
