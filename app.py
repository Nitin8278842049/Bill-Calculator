import streamlit as st
import base64

st.set_page_config(page_title="Tata Power Bill Calculator", layout="centered")

# ---------- LOAD LOGO ----------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64_of_bin_file("logo.png")

# ---------------- BEAUTIFUL CSS ---------------- #
st.markdown("""
<style>

/* App background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

/* Main container */
.block-container {
    max-width: 760px;
    padding-top: 20px;
}

/* Logo */
.logo-container {
    text-align: center;
    margin-bottom: 10px;
}
.logo-container img {
    width: 140px;
}

/* Titles */
.title {
    text-align: center;
    font-size: 34px;
    font-weight: 800;
    margin-top: 10px;
}
.subtitle {
    text-align: center;
    font-size: 15px;
    opacity: 0.8;
    margin-bottom: 25px;
}

/* Glass card effect */
.card {
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(14px);
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.15);
}

/* Section headers */
.section {
    font-size: 17px;
    font-weight: 700;
    margin-top: 12px;
    margin-bottom: 6px;
    color: #aadfff;
}

/* Rows */
.row {
    display: flex;
    justify-content: space-between;
    padding: 8px 2px;
    font-size: 15px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

/* Highlight values */
.value {
    font-weight: 600;
}

/* Solar rebate */
.green {
    color: #7CFC9A;
    font-weight: 600;
}

/* Total box */
.total {
    background: linear-gradient(135deg, #ffffff, #dfe9f3);
    color: black;
    padding: 16px;
    border-radius: 10px;
    font-size: 26px;
    font-weight: 800;
    text-align: right;
    margin-top: 10px;
}

/* Button */
div.stButton > button {
    background: linear-gradient(135deg, #00c6ff, #0072ff);
    color: white;
    font-size: 18px;
    font-weight: 700;
    border-radius: 10px;
    height: 52px;
    width: 100%;
    border: none;
    transition: 0.3s;
}
div.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 18px rgba(0,114,255,0.6);
}

/* Input fields */
label, .stSelectbox label {
    font-weight: 600 !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown(f"""
<div class="logo-container">
    <img src="data:image/png;base64,{logo_base64}">
</div>
<div class="title">TATA POWER BILL CALCULATOR</div>
<div class="subtitle">Mumbai Region • Tariff Logic Simulator</div>
""", unsafe_allow_html=True)

# ---------------- INPUT CARD ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox(
    "Select Network Type",
    ["Welcome (AEML Network)", "Direct (Tata Power Network)"]
)

mu = st.number_input("Metered Units (MU)", min_value=0.0, step=1.0)
su = st.number_input("Solar Units (SU)", min_value=0.0, step=1.0)

calculate = st.button("Calculate Bill")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATION ---------------- #
if calculate:

    if su > mu:
        st.error("Solar units cannot exceed Metered Units.")
        st.stop()

    is_welcome = "Welcome" in network

    if is_welcome:
        bu = mu * 1.0536
        note_bu = f"{mu:.2f} × 1.0536 = {bu:.2f} BU (Loss Adjusted)"
    else:
        bu = mu
        note_bu = f"Direct Supply → BU = {bu:.2f}"

    # Slab Units
    s1_units = min(bu, 100)
    s2_units = min(max(bu - 100, 0), 200)
    s3_units = min(max(bu - 300, 0), 200)
    s4_units = max(bu - 500, 0)

    # Rates
    r1, r2, r3, r4 = 2.00, 5.20, 10.79, 11.79

    s1 = s1_units * r1
    s2 = s2_units * r2
    s3 = s3_units * r3
    s4 = s4_units * r4

    total_energy = s1 + s2 + s3 + s4

    wheeling = mu * 2.93
    solar_rebate = su * 0.50

    if bu <= 100:
        fixed = 90
    elif bu <= 500:
        fixed = 135
    else:
        fixed = 160

    duty_base = max(total_energy + wheeling + fixed - solar_rebate, 0)
    duty = duty_base * 0.16

    tose = bu * 0.3594

    total = total_energy + wheeling + fixed + duty + tose - solar_rebate

    # ---------------- RESULT CARD ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section">Unit Conversion</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span class="value">{bu:.2f}</span></div>', unsafe_allow_html=True)
    st.caption(note_bu)

    st.markdown('<div class="section">Energy Charges</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>0–100 Units @ ₹{r1}</span><span>₹{s1:.2f}</span></div>', unsafe_allow_html=True)
    st.caption(f"{s1_units:.2f} × {r1}")

    st.markdown(f'<div class="row"><span>100–300 Units @ ₹{r2}</span><span>₹{s2:.2f}</span></div>', unsafe_allow_html=True)
    st.caption(f"{s2_units:.2f} × {r2}")

    st.markdown(f'<div class="row"><span>300–500 Units @ ₹{r3}</span><span>₹{s3:.2f}</span></div>', unsafe_allow_html=True)
    st.caption(f"{s3_units:.2f} × {r3}")

    st.markdown(f'<div class="row"><span>Above 500 Units @ ₹{r4}</span><span>₹{s4:.2f}</span></div>', unsafe_allow_html=True)
    st.caption(f"{s4_units:.2f} × {r4}")

    st.markdown(f'<div class="row"><strong>Total Energy</strong><strong>₹{total_energy:.2f}</strong></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Other Charges</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Wheeling Charges</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row green"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Fixed Charges</span><span>₹{fixed:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Electricity Duty (16%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>TOSE</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total):,}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
