import streamlit as st
import base64

st.set_page_config(page_title="Tata Power Bill Calculator", layout="centered")

# ---------- LOAD LOGO ----------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = get_base64_of_bin_file("logo.png")

# ---------------- CSS (TATA STYLE UI) ---------------- #
st.markdown("""
<style>

.stApp {
    background-color: white;
}

.block-container {
    max-width: 760px;
    padding-top: 10px;
}

/* Logo */
.logo-container {
    text-align: center;
    margin-bottom: 5px;
}
.logo-container img {
    max-width: 160px;
    height: auto;
}

/* Title */
.title {
    text-align: center;
    color: #005aa2;
    font-size: 28px;
    font-weight: 800;
}
.subtitle {
    text-align: center;
    color: #555;
    font-size: 14px;
    margin-bottom: 20px;
}

/* Input Card */
.card {
    background: white;
    padding: 20px;
    border-radius: 6px;
    border: 1px solid #dcdcdc;
    margin-bottom: 18px;
}

/* Section Headers */
.section {
    background: #eef7ff;
    padding: 10px;
    border-radius: 4px;
    font-weight: 700;
    color: #005aa2;
    margin-top: 10px;
}

/* Rows */
.row {
    display: flex;
    justify-content: space-between;
    padding: 8px 4px;
    font-size: 14px;
    border-bottom: 1px solid #eeeeee;
}

/* Calculation text */
.calc {
    font-size: 12px;
    color: #777;
    margin-left: 4px;
    margin-bottom: 6px;
}

/* Button */
div.stButton > button {
    background-color: #005aa2;
    color: white;
    font-size: 16px;
    font-weight: 700;
    border-radius: 4px;
    height: 45px;
    width: 100%;
    border: none;
}
div.stButton > button:hover {
    background-color: #00447a;
}

/* Solar rebate green */
.green {
    color: #1a7f37;
    font-weight: 600;
}

/* Net Bill */
.total {
    font-size: 22px;
    font-weight: 800;
    color: black;
    text-align: right;
    padding-top: 10px;
}

label {
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
<div class="subtitle">Mumbai Region Official Tariff</div>
""", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox(
    "Network Type",
    ["Welcome (AEML Network - 5.36% Loss)", "Direct (Tata Power Network)"]
)

mu = st.number_input("Metered Units (Total MU)", min_value=0.0, step=1.0)
su = st.number_input("Solar Hour Units (Direct Meter Reading)", min_value=0.0, step=1.0)

calculate = st.button("Calculate")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATIONS ---------------- #
if calculate:

    if su > mu:
        st.error("Solar units cannot exceed Metered Units.")
        st.stop()

    is_welcome = "Welcome" in network

    if is_welcome:
        bu = mu * 1.0536
        bu_calc = f"{mu:.2f} × 1.0536 = {bu:.0f} BU"
    else:
        bu = mu
        bu_calc = f"BU = {bu:.0f}"

    # Slabs
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

    # ---------------- RESULTS ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 1 : Unit Conversion</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{bu:.0f}</b></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{bu_calc}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 2 : Energy Charges</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>0 - 100 Slab @ ₹2.00</span><span>₹{s1:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>101 - 300 Slab @ ₹5.20</span><span>₹{s2:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>301 - 500 Slab @ ₹10.79</span><span>₹{s3:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Above 500 Slab @ ₹11.79</span><span>₹{s4:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><strong>Total Energy</strong><strong>₹{total_energy:.2f}</strong></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 3 : Other Charges & Rebates</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Wheeling Charges</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row green"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Fixed Charges</span><span>₹{fixed:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Electricity Duty (16%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>TOSE @ ₹0.3594/BU</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total):,}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
