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
.block-container { max-width: 760px; padding-top: 10px; }
.card { background: white; padding: 18px; border-radius: 6px; border: 1px solid #dcdcdc; margin-bottom: 15px; }
.section { background: #eef7ff; padding: 8px; border-radius: 4px; font-weight: 700; color: #005aa2; margin-top: 10px; border: 1px solid #d0e7ff; }
.row { display: flex; justify-content: space-between; padding: 8px; font-size: 14px; border: 1px solid #e6e6e6; margin-top: 4px; }
.calc { font-size: 12px; color: #666; margin-left: 6px; margin-bottom: 6px; }
.total { font-size: 22px; font-weight: 800; text-align: right; padding-top: 10px; }
.green { color: #1a7f37; font-weight: 600; }
div.stButton > button { background-color: #005aa2; color: white; font-size: 16px; font-weight: 700; height: 45px; width: 100%; }
label { font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown("### TATA POWER BILL CALCULATOR")

# ---------------- INPUTS ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox("Network Type", ["Welcome (AEML Network)", "Direct (Tata Power Network)"])
mu_text = st.text_input("Metered Units (MU)", placeholder="Enter Units")
su_text = st.text_input("Solar Units (BU)", placeholder="Enter Solar Units")
load_text = st.text_input("Sanctioned Load (kW)", placeholder="Enter Load")

calculate = st.button("Calculate")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATIONS ---------------- #
if calculate:

    try:
        mu = float(mu_text)
        su = float(su_text)
        load_kw = float(load_text)
    except:
        st.error("Invalid numeric values.")
        st.stop()

    is_welcome = "Welcome" in network

    if is_welcome:
        bu = mu * 1.05785
        wheeling_rate = 2.93
        bu_calc = f"Calculation : {mu} × 1.05785 = {round(bu)} BU"
    else:
        bu = mu
        wheeling_rate = 2.76
        bu_calc = f"Calculation : BU = {round(bu)}"

    if su > bu:
        st.error("Solar units cannot exceed BU.")
        st.stop()

    # -------- SLABS --------
    s1_units = min(bu, 100)
    s2_units = min(max(bu - 100, 0), 200)
    s3_units = min(max(bu - 300, 0), 200)
    s4_units = max(bu - 500, 0)

    r1, r2, r3, r4 = 2.00, 5.20, 10.79, 11.79

    s1 = s1_units * r1
    s2 = s2_units * r2
    s3 = s3_units * r3
    s4 = s4_units * r4

    total_energy = s1 + s2 + s3 + s4

    wheeling = mu * wheeling_rate
    solar_rebate = su * 0.50

    if bu <= 100:
        fixed = 90
    elif bu <= 500:
        fixed = 135
    else:
        fixed = 160

    additional_fixed = 250 if load_kw > 10 else 0

    duty_base = max(total_energy + wheeling + fixed + additional_fixed - solar_rebate, 0)
    duty = duty_base * 0.16

    tose = bu * 0.3594

    total = total_energy + wheeling + fixed + additional_fixed + duty + tose - solar_rebate

    # ---------------- RESULTS ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 1 : Units</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{round(bu)}</b></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{bu_calc}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 2 : Energy Charges</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>0 – 100 Units (@ ₹2.00)</span><span>₹{s1:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {round(s1_units)} × 2.00 = ₹{s1:.2f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>101 – 300 Units (@ ₹5.20)</span><span>₹{s2:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {round(s2_units)} × 5.20 = ₹{s2:.2f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>301 – 500 Units (@ ₹10.79)</span><span>₹{s3:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {round(s3_units)} × 10.79 = ₹{s3:.2f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Above 500 Units (@ ₹11.79)</span><span>₹{s4:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {round(s4_units)} × 11.79 = ₹{s4:.2f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><strong>Total Energy Charges</strong><strong>₹{total_energy:.2f}</strong></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 3 : Other Charges</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Wheeling Charges</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {mu} × {wheeling_rate} = ₹{wheeling:.2f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Fixed Charges</span><span>₹{fixed:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : Based on BU slab = ₹{fixed:.2f}</div>', unsafe_allow_html=True)

    if additional_fixed:
        st.markdown(f'<div class="row"><span>Additional Fixed Charges</span><span>₹250.00</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc">Calculation : Load > 10 kW → ₹250</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row green"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {su} × 0.50 = ₹{solar_rebate:.2f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Electricity Duty (16%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : ({total_energy:.2f} + {wheeling:.2f} + {fixed:.2f} + {additional_fixed:.2f} - {solar_rebate:.2f}) × 16% = ₹{duty:.2f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>TOSE</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : {round(bu)} × 0.3594 = ₹{tose:.2f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total):,}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
